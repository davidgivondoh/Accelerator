"""
Growth Engine Scheduler

Autonomous scheduling system for running the Growth Engine
at optimal times with rate limiting, retry logic, and monitoring.

Features:
- Daily discovery loops at configurable times
- Weekly learning cycles
- Rate limiting across API providers
- Graceful failure handling with retries
- Health monitoring and alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_MISSED,
    JobExecutionEvent,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config.settings import settings

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class JobResult:
    """Result of a scheduled job execution"""
    job_id: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    concurrent_requests: int = 10
    
    # Per-provider limits
    gemini_rpm: int = 60
    anthropic_rpm: int = 50
    openai_rpm: int = 60


@dataclass
class SchedulerConfig:
    """Scheduler configuration"""
    # Daily loop timing (24-hour format)
    daily_discovery_hour: int = 6  # 6 AM
    daily_discovery_minute: int = 0
    
    # Weekly learning cycle
    weekly_learning_day: str = "sunday"  # Day of week
    weekly_learning_hour: int = 2  # 2 AM
    
    # Health check interval (minutes)
    health_check_interval: int = 15
    
    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # Rate limiting
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)


class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._request_times: dict[str, list[datetime]] = {
            "gemini": [],
            "anthropic": [],
            "openai": [],
            "global": [],
        }
        self._semaphore = asyncio.Semaphore(config.concurrent_requests)
        self._lock = asyncio.Lock()
    
    async def acquire(self, provider: str = "global") -> bool:
        """
        Acquire permission to make an API request.
        
        Args:
            provider: API provider name
            
        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            # Clean old entries
            self._request_times[provider] = [
                t for t in self._request_times.get(provider, [])
                if t > hour_ago
            ]
            self._request_times["global"] = [
                t for t in self._request_times["global"]
                if t > hour_ago
            ]
            
            # Check per-minute limit
            recent_requests = sum(
                1 for t in self._request_times.get(provider, [])
                if t > minute_ago
            )
            
            provider_rpm = getattr(
                self.config, 
                f"{provider}_rpm", 
                self.config.requests_per_minute
            )
            
            if recent_requests >= provider_rpm:
                logger.warning(f"Rate limited: {provider} ({recent_requests}/{provider_rpm} rpm)")
                return False
            
            # Check global hourly limit
            global_requests = sum(
                1 for t in self._request_times["global"]
                if t > hour_ago
            )
            
            if global_requests >= self.config.requests_per_hour:
                logger.warning(f"Rate limited: global ({global_requests}/{self.config.requests_per_hour} rph)")
                return False
            
            # Record request
            self._request_times[provider].append(now)
            self._request_times["global"].append(now)
            
            return True
    
    async def wait_and_acquire(self, provider: str = "global", timeout: float = 60.0) -> bool:
        """
        Wait for rate limit to clear, then acquire.
        
        Args:
            provider: API provider name
            timeout: Maximum time to wait
            
        Returns:
            True if acquired within timeout
        """
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).total_seconds() < timeout:
            if await self.acquire(provider):
                return True
            await asyncio.sleep(1.0)
        
        return False
    
    def get_stats(self) -> dict[str, Any]:
        """Get current rate limiter statistics."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        stats = {}
        for provider, times in self._request_times.items():
            rpm = sum(1 for t in times if t > minute_ago)
            rph = sum(1 for t in times if t > hour_ago)
            stats[provider] = {"rpm": rpm, "rph": rph}
        
        return stats


class HealthMonitor:
    """
    Monitors system health and sends alerts.
    """
    
    def __init__(self):
        self.checks: dict[str, Callable] = {}
        self.last_results: dict[str, bool] = {}
        self.failure_counts: dict[str, int] = {}
        self.alert_handlers: list[Callable] = []
    
    def register_check(self, name: str, check_func: Callable[[], bool]):
        """Register a health check."""
        self.checks[name] = check_func
        self.failure_counts[name] = 0
    
    def register_alert_handler(self, handler: Callable[[str, str], None]):
        """Register an alert handler."""
        self.alert_handlers.append(handler)
    
    async def run_checks(self) -> dict[str, bool]:
        """Run all health checks."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[name] = result
                
                if not result:
                    self.failure_counts[name] += 1
                    if self.failure_counts[name] >= 3:
                        await self._send_alert(
                            f"Health check failed: {name}",
                            f"Check '{name}' has failed {self.failure_counts[name]} times"
                        )
                else:
                    self.failure_counts[name] = 0
                    
            except Exception as e:
                results[name] = False
                self.failure_counts[name] += 1
                logger.error(f"Health check '{name}' error: {e}")
        
        self.last_results = results
        return results
    
    async def _send_alert(self, title: str, message: str):
        """Send alert to all handlers."""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(title, message)
                else:
                    handler(title, message)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def get_status(self) -> dict[str, Any]:
        """Get current health status."""
        return {
            "healthy": all(self.last_results.values()) if self.last_results else True,
            "checks": self.last_results,
            "failure_counts": self.failure_counts,
        }


class GrowthEngineScheduler:
    """
    Main scheduler for the Growth Engine.
    
    Handles:
    - Daily discovery loops
    - Weekly learning cycles
    - Health monitoring
    - Rate limiting
    - Graceful failure handling
    """
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        self.config = config or SchedulerConfig()
        self.scheduler = AsyncIOScheduler()
        self.rate_limiter = RateLimiter(self.config.rate_limits)
        self.health_monitor = HealthMonitor()
        
        # Job tracking
        self.job_history: list[JobResult] = []
        self.current_jobs: dict[str, JobResult] = {}
        
        # Setup
        self._setup_scheduler()
        self._setup_health_checks()
    
    def _setup_scheduler(self):
        """Configure scheduled jobs."""
        # Daily discovery loop
        self.scheduler.add_job(
            self._run_daily_discovery,
            CronTrigger(
                hour=self.config.daily_discovery_hour,
                minute=self.config.daily_discovery_minute,
            ),
            id="daily_discovery",
            name="Daily Discovery Loop",
            replace_existing=True,
        )
        
        # Weekly learning cycle
        self.scheduler.add_job(
            self._run_weekly_learning,
            CronTrigger(
                day_of_week=self.config.weekly_learning_day,
                hour=self.config.weekly_learning_hour,
            ),
            id="weekly_learning",
            name="Weekly Learning Cycle",
            replace_existing=True,
        )
        
        # Health check
        self.scheduler.add_job(
            self._run_health_check,
            IntervalTrigger(minutes=self.config.health_check_interval),
            id="health_check",
            name="Health Check",
            replace_existing=True,
        )
        
        # Event listeners
        self.scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED,
        )
        self.scheduler.add_listener(
            self._on_job_error,
            EVENT_JOB_ERROR,
        )
        self.scheduler.add_listener(
            self._on_job_missed,
            EVENT_JOB_MISSED,
        )
    
    def _setup_health_checks(self):
        """Register health checks."""
        self.health_monitor.register_check("database", self._check_database)
        self.health_monitor.register_check("api_keys", self._check_api_keys)
        self.health_monitor.register_check("rate_limits", self._check_rate_limits)
    
    async def _check_database(self) -> bool:
        """Check database connectivity."""
        try:
            from src.data.database import get_db_session
            async with get_db_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _check_api_keys(self) -> bool:
        """Check API key configuration."""
        return bool(settings.google_api_key)
    
    def _check_rate_limits(self) -> bool:
        """Check rate limit status."""
        stats = self.rate_limiter.get_stats()
        # Flag if any provider is over 80% of limit
        for provider, data in stats.items():
            if provider == "global":
                continue
            limit = getattr(self.config.rate_limits, f"{provider}_rpm", 60)
            if data["rpm"] > limit * 0.8:
                return False
        return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=30, max=300),
        retry=retry_if_exception_type(Exception),
    )
    async def _run_daily_discovery(self):
        """Execute the daily discovery loop with retries."""
        job_id = f"daily_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        job_result = JobResult(
            job_id=job_id,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.current_jobs[job_id] = job_result
        
        try:
            logger.info(f"Starting daily discovery: {job_id}")
            
            # Check rate limits
            if not await self.rate_limiter.wait_and_acquire("gemini"):
                raise Exception("Rate limited - cannot start daily discovery")
            
            # Run the discovery pipeline
            from src.orchestrator.engine import growth_engine
            result = await growth_engine.run_full_pipeline(
                include_learning=False,  # Learning runs weekly
            )
            
            job_result.status = JobStatus.COMPLETED
            job_result.result = result
            
            logger.info(f"Daily discovery completed: {job_id}")
            
        except Exception as e:
            job_result.status = JobStatus.FAILED
            job_result.error = str(e)
            logger.error(f"Daily discovery failed: {e}")
            raise
        
        finally:
            job_result.completed_at = datetime.utcnow()
            job_result.duration_seconds = (
                job_result.completed_at - job_result.started_at
            ).total_seconds()
            
            self.job_history.append(job_result)
            del self.current_jobs[job_id]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=60, max=600),
        retry=retry_if_exception_type(Exception),
    )
    async def _run_weekly_learning(self):
        """Execute the weekly learning cycle with retries."""
        job_id = f"learning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        job_result = JobResult(
            job_id=job_id,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.current_jobs[job_id] = job_result
        
        try:
            logger.info(f"Starting weekly learning: {job_id}")
            
            # Run learning cycle
            from src.intelligence.learning import run_weekly_learning
            result = await run_weekly_learning()
            
            job_result.status = JobStatus.COMPLETED
            job_result.result = result.model_dump() if hasattr(result, 'model_dump') else result
            
            logger.info(f"Weekly learning completed: {job_id}")
            
        except Exception as e:
            job_result.status = JobStatus.FAILED
            job_result.error = str(e)
            logger.error(f"Weekly learning failed: {e}")
            raise
        
        finally:
            job_result.completed_at = datetime.utcnow()
            job_result.duration_seconds = (
                job_result.completed_at - job_result.started_at
            ).total_seconds()
            
            self.job_history.append(job_result)
            del self.current_jobs[job_id]
    
    async def _run_health_check(self):
        """Run health monitoring check."""
        results = await self.health_monitor.run_checks()
        
        if not all(results.values()):
            unhealthy = [k for k, v in results.items() if not v]
            logger.warning(f"Health check failures: {unhealthy}")
    
    def _on_job_executed(self, event: JobExecutionEvent):
        """Handle successful job execution."""
        logger.info(f"Job executed: {event.job_id}")
    
    def _on_job_error(self, event: JobExecutionEvent):
        """Handle job execution error."""
        logger.error(f"Job failed: {event.job_id} - {event.exception}")
    
    def _on_job_missed(self, event: JobExecutionEvent):
        """Handle missed job execution."""
        logger.warning(f"Job missed: {event.job_id}")
    
    def start(self):
        """Start the scheduler."""
        logger.info("Starting Growth Engine Scheduler")
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping Growth Engine Scheduler")
        self.scheduler.shutdown()
    
    def trigger_job(self, job_id: str):
        """Manually trigger a job."""
        job = self.scheduler.get_job(job_id)
        if job:
            self.scheduler.modify_job(job_id, next_run_time=datetime.utcnow())
            logger.info(f"Triggered job: {job_id}")
        else:
            logger.error(f"Job not found: {job_id}")
    
    def get_status(self) -> dict[str, Any]:
        """Get scheduler status."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            })
        
        return {
            "running": self.scheduler.running,
            "jobs": jobs,
            "current_jobs": {
                k: {
                    "status": v.status.value,
                    "started_at": v.started_at.isoformat(),
                }
                for k, v in self.current_jobs.items()
            },
            "recent_history": [
                {
                    "job_id": j.job_id,
                    "status": j.status.value,
                    "duration": j.duration_seconds,
                    "error": j.error,
                }
                for j in self.job_history[-10:]
            ],
            "health": self.health_monitor.get_status(),
            "rate_limits": self.rate_limiter.get_stats(),
        }


# Global scheduler instance
_scheduler: Optional[GrowthEngineScheduler] = None


def get_scheduler() -> GrowthEngineScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = GrowthEngineScheduler()
    return _scheduler


async def start_scheduler():
    """Start the scheduler and run indefinitely."""
    scheduler = get_scheduler()
    scheduler.start()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        scheduler.stop()


# CLI integration
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Growth Engine Scheduler")
    parser.add_argument("--trigger", type=str, help="Trigger a specific job")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    
    args = parser.parse_args()
    
    scheduler = get_scheduler()
    
    if args.status:
        import json
        print(json.dumps(scheduler.get_status(), indent=2, default=str))
    elif args.trigger:
        scheduler.start()
        scheduler.trigger_job(args.trigger)
        asyncio.run(asyncio.sleep(5))
        scheduler.stop()
    else:
        asyncio.run(start_scheduler())
