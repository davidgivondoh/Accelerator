"""
Data layer module for the Growth Engine.

Provides PostgreSQL database access via SQLAlchemy with async support.
Recommended hosting: Neon (https://neon.tech) - free tier available.
"""

from src.data.database import (
    Base,
    async_session_maker,
    close_db,
    engine,
    get_session,
    init_db,
)
from src.data.models import (
    ApplicationDraftORM,
    OpportunityORM,
    OutcomeORM,
    ProfileORM,
    ScoringWeightsORM,
)
from src.data.repositories import OpportunityRepository

__all__ = [
    # Database
    "Base",
    "engine",
    "async_session_maker",
    "get_session",
    "init_db",
    "close_db",
    # ORM Models
    "OpportunityORM",
    "ApplicationDraftORM",
    "OutcomeORM",
    "ProfileORM",
    "ScoringWeightsORM",
    # Repositories
    "OpportunityRepository",
]
