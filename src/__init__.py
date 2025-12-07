"""
Givondo Growth Engine
=====================

An autonomous multi-agent system for opportunity discovery and application generation.
Built on Google ADK with multi-model support (Gemini, Claude Opus 4.5, GPT-4).

This package provides:
- Multi-agent orchestration for opportunity discovery
- Automated application generation at scale
- Profile-driven narrative consistency
- ML-powered scoring and prioritization
- RESTful API and CLI interfaces
- Production-grade scheduling and monitoring
- Safety guardrails and human-in-the-loop approval
"""

__version__ = "0.1.0"
__author__ = "Givondo"

# Lazy imports to avoid loading heavy modules until accessed
def __getattr__(name):
    """Lazy load heavy modules only when accessed."""
    # Orchestration
    if name in ("GrowthEngine", "growth_engine"):
        from src.orchestrator import GrowthEngine, growth_engine
        return growth_engine if name == "growth_engine" else GrowthEngine
    
    # CLI
    if name == "cli":
        from src import cli as cli_module
        return cli_module
    
    # API
    if name in ("app", "create_app"):
        from src.api import app, create_app
        return create_app if name == "create_app" else app
    
    # Scheduler
    if name in ("EngineScheduler", "start_scheduler"):
        from src.scheduler import EngineScheduler, start_scheduler
        return start_scheduler if name == "start_scheduler" else EngineScheduler
    
    # Monitoring
    if name in ("MonitoringSystem", "create_monitoring_system"):
        from src.monitoring import MonitoringSystem, create_monitoring_system
        return create_monitoring_system if name == "create_monitoring_system" else MonitoringSystem
    
    # Guardrails
    if name in ("GuardrailsSystem", "create_guardrails_system"):
        from src.guardrails import GuardrailsSystem, create_guardrails_system
        return create_guardrails_system if name == "create_guardrails_system" else GuardrailsSystem
    
    # Analytics
    if name == "AnalyticsEngine":
        from src.analytics import AnalyticsEngine
        return AnalyticsEngine
    
    # Learning
    if name == "LearningAgent":
        from src.learning import LearningAgent
        return LearningAgent
    
    # ML Model
    if name == "FitScoreModel":
        from src.ml_model import FitScoreModel
        return FitScoreModel
    
    # Embeddings
    if name == "EmbeddingManager":
        from src.embeddings import EmbeddingManager
        return EmbeddingManager
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

from src.models import (
    Opportunity,
    OpportunityType,
    OpportunityTier,
    ApplicationDraft,
    Profile,
)

__all__ = [
    # Core
    "GrowthEngine",
    "growth_engine",
    
    # Models
    "Opportunity",
    "OpportunityType",
    "OpportunityTier",
    "ApplicationDraft",
    "Profile",
    
    # Interfaces
    "cli",
    "app",
    "create_app",
    
    # Scheduling
    "EngineScheduler",
    "start_scheduler",
    
    # Monitoring
    "MonitoringSystem",
    "create_monitoring_system",
    
    # Guardrails
    "GuardrailsSystem",
    "create_guardrails_system",
    
    # Intelligence
    "AnalyticsEngine",
    "LearningAgent",
    "FitScoreModel",
    "EmbeddingManager",
]