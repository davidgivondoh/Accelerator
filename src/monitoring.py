"""
Monitoring & Alerting System

Provides comprehensive monitoring for the Growth Engine:
- Structured logging with context
- Metrics collection and aggregation
- Alert management with multiple channels
- Performance tracking
"""

import asyncio
import json
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
from contextlib import contextmanager
import time

from rich.console import Console
from rich.logging import RichHandler


# ==================== Structured Logging ====================

class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogContext:
    """Context for structured logging"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    job_id: Optional[str] = None
    agent_name: Optional[str] = None
    extra: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        result = {
            k: v for k, v in {
                "request_id": self.request_id,
                "user_id": self.user_id,
                "session_id": self.session_id,
                "job_id": self.job_id,
                "agent_name": self.agent_name,
            }.items() if v is not None
        }
        result.update(self.extra)
        return result


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add context if available
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # Add extra fields
        for key in ["request_id", "user_id", "session_id", "job_id", "agent_name"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        
        return json.dumps(log_data)


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that adds context to all logs"""
    
    def __init__(self, logger: logging.Logger, context: LogContext = None):
        super().__init__(logger, {})
        self.context = context or LogContext()
    
    def process(self, msg, kwargs):
        kwargs["extra"] = kwargs.get("extra", {})
        kwargs["extra"]["context"] = self.context.to_dict()
        
        # Copy context fields to extra for easy access
        for key, value in self.context.to_dict().items():
            kwargs["extra"][key] = value
        
        return msg, kwargs
    
    def with_context(self, **kwargs) -> "ContextLogger":
        """Create new logger with additional context"""
        new_context = LogContext(
            request_id=kwargs.get("request_id", self.context.request_id),
            user_id=kwargs.get("user_id", self.context.user_id),
            session_id=kwargs.get("session_id", self.context.session_id),
            job_id=kwargs.get("job_id", self.context.job_id),
            agent_name=kwargs.get("agent_name", self.context.agent_name),
            extra={**self.context.extra, **kwargs.get("extra", {})},
        )
        return ContextLogger(self.logger, new_context)


def setup_logging(
    level: str = "INFO",
    format: str = "structured",  # "structured" or "rich"
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Setup logging with structured output.
    
    Args:
        level: Log level
        format: Output format ("structured" for JSON, "rich" for pretty)
        log_file: Optional file path for logging
    
    Returns:
        Configured logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    if format == "rich":
        # Rich console output for development
        console_handler = RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_path=True,
        )
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
    else:
        # Structured JSON for production
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(StructuredFormatter())
        stream_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(stream_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str, context: LogContext = None) -> ContextLogger:
    """Get a context-aware logger."""
    return ContextLogger(logging.getLogger(name), context)


# ==================== Metrics Collection ====================

@dataclass
class Metric:
    """Single metric value"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
        }


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution
    TIMER = "timer"          # Duration measurements


class MetricsCollector:
    """
    Collects and aggregates metrics.
    """
    
    def __init__(self, flush_interval_seconds: int = 60):
        self.flush_interval = flush_interval_seconds
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._last_flush = datetime.utcnow()
        self._handlers: list[Callable[[list[Metric]], None]] = []
    
    def add_handler(self, handler: Callable[[list[Metric]], None]):
        """Add a metrics handler (e.g., for sending to external service)"""
        self._handlers.append(handler)
    
    def increment(self, name: str, value: float = 1, tags: dict = None):
        """Increment a counter"""
        key = self._make_key(name, tags)
        self._counters[key] += value
    
    def gauge(self, name: str, value: float, tags: dict = None):
        """Set a gauge value"""
        key = self._make_key(name, tags)
        self._gauges[key] = value
    
    def histogram(self, name: str, value: float, tags: dict = None):
        """Record a histogram value"""
        key = self._make_key(name, tags)
        self._histograms[key].append(value)
    
    def timer(self, name: str, duration_ms: float, tags: dict = None):
        """Record a timer value"""
        key = self._make_key(name, tags)
        self._timers[key].append(duration_ms)
    
    @contextmanager
    def time(self, name: str, tags: dict = None):
        """Context manager for timing operations"""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.timer(name, duration_ms, tags)
    
    def _make_key(self, name: str, tags: dict = None) -> str:
        """Create a unique key for a metric"""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{name}:{tag_str}"
        return name
    
    def _parse_key(self, key: str) -> tuple[str, dict]:
        """Parse a metric key back to name and tags"""
        if ":" in key:
            name, tag_str = key.split(":", 1)
            tags = dict(item.split("=") for item in tag_str.split(","))
            return name, tags
        return key, {}
    
    def flush(self) -> list[Metric]:
        """Flush and return all metrics"""
        metrics = []
        now = datetime.utcnow()
        
        # Counters
        for key, value in self._counters.items():
            name, tags = self._parse_key(key)
            metrics.append(Metric(
                name=f"{name}_total",
                value=value,
                timestamp=now,
                tags={**tags, "type": "counter"},
            ))
        
        # Gauges
        for key, value in self._gauges.items():
            name, tags = self._parse_key(key)
            metrics.append(Metric(
                name=name,
                value=value,
                timestamp=now,
                tags={**tags, "type": "gauge"},
            ))
        
        # Histograms - compute percentiles
        for key, values in self._histograms.items():
            if not values:
                continue
            name, tags = self._parse_key(key)
            sorted_vals = sorted(values)
            
            for pct, suffix in [(50, "_p50"), (90, "_p90"), (99, "_p99")]:
                idx = int(len(sorted_vals) * pct / 100)
                metrics.append(Metric(
                    name=f"{name}{suffix}",
                    value=sorted_vals[min(idx, len(sorted_vals)-1)],
                    timestamp=now,
                    tags={**tags, "type": "histogram"},
                ))
            
            metrics.append(Metric(
                name=f"{name}_count",
                value=len(values),
                timestamp=now,
                tags={**tags, "type": "histogram"},
            ))
        
        # Timers - similar to histograms
        for key, values in self._timers.items():
            if not values:
                continue
            name, tags = self._parse_key(key)
            sorted_vals = sorted(values)
            
            for pct, suffix in [(50, "_p50"), (90, "_p90"), (99, "_p99")]:
                idx = int(len(sorted_vals) * pct / 100)
                metrics.append(Metric(
                    name=f"{name}{suffix}_ms",
                    value=sorted_vals[min(idx, len(sorted_vals)-1)],
                    timestamp=now,
                    tags={**tags, "type": "timer"},
                ))
            
            metrics.append(Metric(
                name=f"{name}_count",
                value=len(values),
                timestamp=now,
                tags={**tags, "type": "timer"},
            ))
        
        # Clear histogram and timer buffers
        self._histograms.clear()
        self._timers.clear()
        self._last_flush = now
        
        # Send to handlers
        for handler in self._handlers:
            try:
                handler(metrics)
            except Exception as e:
                logging.error(f"Metrics handler error: {e}")
        
        return metrics
    
    def get_stats(self) -> dict[str, Any]:
        """Get current metrics summary"""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histogram_counts": {k: len(v) for k, v in self._histograms.items()},
            "timer_counts": {k: len(v) for k, v in self._timers.items()},
            "last_flush": self._last_flush.isoformat(),
        }


# Global metrics collector
_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


# ==================== Alerting ====================

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """An alert to be sent"""
    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "growth-engine"
    tags: dict = field(default_factory=dict)
    resolved: bool = False
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "tags": self.tags,
            "resolved": self.resolved,
        }


class AlertChannel:
    """Base class for alert channels"""
    
    async def send(self, alert: Alert) -> bool:
        """Send an alert. Returns True if successful."""
        raise NotImplementedError


class ConsoleAlertChannel(AlertChannel):
    """Prints alerts to console"""
    
    def __init__(self):
        self.console = Console(stderr=True)
    
    async def send(self, alert: Alert) -> bool:
        style_map = {
            AlertSeverity.INFO: "blue",
            AlertSeverity.WARNING: "yellow",
            AlertSeverity.ERROR: "red",
            AlertSeverity.CRITICAL: "bold red",
        }
        style = style_map.get(alert.severity, "white")
        
        self.console.print(f"\n🚨 [{alert.severity.value.upper()}] {alert.title}", style=style)
        self.console.print(f"   {alert.message}")
        self.console.print(f"   Time: {alert.timestamp.isoformat()}")
        
        return True


class WebhookAlertChannel(AlertChannel):
    """Sends alerts to a webhook (Slack, Discord, etc.)"""
    
    def __init__(self, webhook_url: str, format: str = "slack"):
        self.webhook_url = webhook_url
        self.format = format
    
    async def send(self, alert: Alert) -> bool:
        import httpx
        
        if self.format == "slack":
            payload = {
                "text": f"*[{alert.severity.value.upper()}] {alert.title}*\n{alert.message}",
                "attachments": [{
                    "color": {
                        AlertSeverity.INFO: "#36a64f",
                        AlertSeverity.WARNING: "#ffcc00",
                        AlertSeverity.ERROR: "#ff6600",
                        AlertSeverity.CRITICAL: "#ff0000",
                    }.get(alert.severity, "#808080"),
                    "fields": [
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Time", "value": alert.timestamp.isoformat(), "short": True},
                    ]
                }]
            }
        else:
            payload = alert.to_dict()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logging.error(f"Webhook alert failed: {e}")
            return False


class EmailAlertChannel(AlertChannel):
    """Sends alerts via email"""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: list[str],
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
    
    async def send(self, alert: Alert) -> bool:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)
            msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
Alert: {alert.title}
Severity: {alert.severity.value}
Time: {alert.timestamp.isoformat()}
Source: {alert.source}

{alert.message}

Tags: {json.dumps(alert.tags)}
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            # Send in thread pool to not block
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, msg)
            
            return True
        except Exception as e:
            logging.error(f"Email alert failed: {e}")
            return False
    
    def _send_email(self, msg):
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


class AlertManager:
    """
    Manages alert routing and deduplication.
    """
    
    def __init__(
        self,
        dedup_window_seconds: int = 300,  # Don't repeat same alert for 5 min
    ):
        self.channels: list[AlertChannel] = []
        self.dedup_window = timedelta(seconds=dedup_window_seconds)
        self.recent_alerts: dict[str, datetime] = {}
        self.alert_history: list[Alert] = []
    
    def add_channel(self, channel: AlertChannel):
        """Add an alert channel"""
        self.channels.append(channel)
    
    def _get_alert_key(self, alert: Alert) -> str:
        """Generate deduplication key for alert"""
        return f"{alert.title}:{alert.severity.value}"
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        tags: dict = None,
        force: bool = False,
    ) -> bool:
        """
        Send an alert through all channels.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Severity level
            tags: Additional tags
            force: Skip deduplication
        
        Returns:
            True if alert was sent
        """
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            tags=tags or {},
        )
        
        # Check deduplication
        key = self._get_alert_key(alert)
        now = datetime.utcnow()
        
        if not force and key in self.recent_alerts:
            if now - self.recent_alerts[key] < self.dedup_window:
                logging.debug(f"Alert deduplicated: {title}")
                return False
        
        self.recent_alerts[key] = now
        self.alert_history.append(alert)
        
        # Send to all channels
        success = False
        for channel in self.channels:
            try:
                if await channel.send(alert):
                    success = True
            except Exception as e:
                logging.error(f"Alert channel error: {e}")
        
        return success
    
    async def resolve_alert(self, title: str):
        """Mark an alert as resolved"""
        for alert in reversed(self.alert_history):
            if alert.title == title and not alert.resolved:
                alert.resolved = True
                
                # Send resolution notification
                await self.send_alert(
                    title=f"Resolved: {title}",
                    message="This alert has been resolved.",
                    severity=AlertSeverity.INFO,
                    force=True,
                )
                break
    
    def get_active_alerts(self) -> list[Alert]:
        """Get all unresolved alerts"""
        return [a for a in self.alert_history if not a.resolved]
    
    def cleanup_old_alerts(self, days: int = 7):
        """Remove old alerts from history"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.alert_history = [a for a in self.alert_history if a.timestamp > cutoff]
        self.recent_alerts = {
            k: v for k, v in self.recent_alerts.items()
            if v > cutoff
        }


# Global alert manager
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get global alert manager"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
        _alert_manager.add_channel(ConsoleAlertChannel())
    return _alert_manager


async def send_alert(
    title: str,
    message: str,
    severity: AlertSeverity = AlertSeverity.WARNING,
    tags: dict = None,
) -> bool:
    """Convenience function to send an alert"""
    return await get_alert_manager().send_alert(title, message, severity, tags)


# ==================== Performance Tracking ====================

class PerformanceTracker:
    """
    Tracks performance metrics for agents and operations.
    """
    
    def __init__(self, metrics: MetricsCollector = None):
        self.metrics = metrics or get_metrics()
        self._active_spans: dict[str, dict] = {}
    
    def start_span(self, name: str, tags: dict = None) -> str:
        """Start tracking an operation"""
        import uuid
        span_id = str(uuid.uuid4())[:8]
        
        self._active_spans[span_id] = {
            "name": name,
            "tags": tags or {},
            "start_time": time.perf_counter(),
        }
        
        return span_id
    
    def end_span(self, span_id: str, success: bool = True, error: str = None):
        """End tracking an operation"""
        if span_id not in self._active_spans:
            return
        
        span = self._active_spans.pop(span_id)
        duration_ms = (time.perf_counter() - span["start_time"]) * 1000
        
        tags = {**span["tags"], "success": str(success).lower()}
        
        self.metrics.timer(f"{span['name']}_duration", duration_ms, tags)
        self.metrics.increment(f"{span['name']}_total", tags=tags)
        
        if not success:
            self.metrics.increment(f"{span['name']}_errors", tags=tags)
    
    @contextmanager
    def track(self, name: str, tags: dict = None):
        """Context manager for tracking operations"""
        span_id = self.start_span(name, tags)
        success = True
        error = None
        
        try:
            yield span_id
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            self.end_span(span_id, success, error)
    
    async def track_async(self, name: str, coro, tags: dict = None):
        """Track an async operation"""
        span_id = self.start_span(name, tags)
        success = True
        error = None
        
        try:
            return await coro
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            self.end_span(span_id, success, error)


# Global performance tracker
_tracker: Optional[PerformanceTracker] = None


def get_tracker() -> PerformanceTracker:
    """Get global performance tracker"""
    global _tracker
    if _tracker is None:
        _tracker = PerformanceTracker()
    return _tracker
