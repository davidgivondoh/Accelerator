"""
Repository for Opportunity database operations.

Provides async CRUD operations for opportunities using SQLAlchemy.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models import OpportunityORM
from src.models import Opportunity, OpportunityCreate, OpportunityTier, OpportunityUpdate


class OpportunityRepository:
    """Repository for opportunity CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
    
    async def create(self, opportunity: OpportunityCreate) -> OpportunityORM:
        """
        Create a new opportunity.
        
        Args:
            opportunity: Opportunity data to create
            
        Returns:
            Created opportunity ORM object
        """
        db_opp = OpportunityORM(
            title=opportunity.title,
            organization=opportunity.organization,
            description=opportunity.description,
            opportunity_type=opportunity.opportunity_type.value,
            url=str(opportunity.url),
            source=opportunity.source.value,
            summary=opportunity.summary,
            location=opportunity.location,
            is_remote=opportunity.is_remote,
            application_url=str(opportunity.application_url) if opportunity.application_url else None,
            posted_date=opportunity.posted_date,
            deadline=opportunity.deadline,
            requirements=opportunity.requirements.model_dump() if opportunity.requirements else {},
            compensation=opportunity.compensation.model_dump() if opportunity.compensation else {},
            tags=opportunity.tags,
            source_query=opportunity.source_query,
            raw_data=opportunity.raw_data,
        )
        
        self.session.add(db_opp)
        await self.session.flush()
        return db_opp
    
    async def get_by_id(self, opportunity_id: str) -> OpportunityORM | None:
        """Get opportunity by ID."""
        result = await self.session.execute(
            select(OpportunityORM).where(OpportunityORM.id == opportunity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_url(self, url: str) -> OpportunityORM | None:
        """Get opportunity by URL (for deduplication)."""
        result = await self.session.execute(
            select(OpportunityORM).where(OpportunityORM.url == url)
        )
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        tier: OpportunityTier | None = None,
    ) -> list[OpportunityORM]:
        """
        List opportunities with optional filtering.
        
        Args:
            limit: Maximum number to return
            offset: Number to skip
            tier: Optional tier filter
            
        Returns:
            List of opportunities
        """
        query = select(OpportunityORM).order_by(OpportunityORM.discovered_at.desc())
        
        if tier:
            query = query.where(OpportunityORM.tier == tier.value)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def list_tier_1(self, limit: int = 50) -> list[OpportunityORM]:
        """Get top-tier opportunities."""
        return await self.list_all(limit=limit, tier=OpportunityTier.TIER_1)
    
    async def list_upcoming_deadlines(self, days: int = 7) -> list[OpportunityORM]:
        """Get opportunities with deadlines in the next N days."""
        cutoff = datetime.utcnow()
        future = datetime.utcnow().replace(day=cutoff.day + days)
        
        result = await self.session.execute(
            select(OpportunityORM)
            .where(OpportunityORM.deadline >= cutoff)
            .where(OpportunityORM.deadline <= future)
            .order_by(OpportunityORM.deadline.asc())
        )
        return list(result.scalars().all())
    
    async def update(
        self,
        opportunity_id: str,
        updates: OpportunityUpdate,
    ) -> OpportunityORM | None:
        """
        Update an opportunity.
        
        Args:
            opportunity_id: ID of opportunity to update
            updates: Fields to update
            
        Returns:
            Updated opportunity or None if not found
        """
        update_data = updates.model_dump(exclude_none=True)
        
        if not update_data:
            return await self.get_by_id(opportunity_id)
        
        # Handle nested objects
        if "score" in update_data:
            update_data["score"] = update_data["score"]
            if update_data["score"]:
                update_data["fit_score"] = update_data["score"].get("fit_score")
        
        if "tier" in update_data:
            update_data["tier"] = update_data["tier"]
        
        await self.session.execute(
            update(OpportunityORM)
            .where(OpportunityORM.id == opportunity_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        
        return await self.get_by_id(opportunity_id)
    
    async def delete(self, opportunity_id: str) -> bool:
        """Delete an opportunity."""
        result = await self.session.execute(
            delete(OpportunityORM).where(OpportunityORM.id == opportunity_id)
        )
        return result.rowcount > 0
    
    async def bulk_create(
        self,
        opportunities: list[OpportunityCreate],
        skip_duplicates: bool = True,
    ) -> list[OpportunityORM]:
        """
        Create multiple opportunities.
        
        Args:
            opportunities: List of opportunities to create
            skip_duplicates: Skip opportunities with duplicate URLs
            
        Returns:
            List of created opportunities
        """
        created = []
        
        for opp in opportunities:
            if skip_duplicates:
                existing = await self.get_by_url(str(opp.url))
                if existing:
                    continue
            
            db_opp = await self.create(opp)
            created.append(db_opp)
        
        return created
    
    async def count_by_tier(self) -> dict[str, int]:
        """Get count of opportunities by tier."""
        from sqlalchemy import func
        
        result = await self.session.execute(
            select(
                OpportunityORM.tier,
                func.count(OpportunityORM.id)
            ).group_by(OpportunityORM.tier)
        )
        
        return {row[0]: row[1] for row in result.all()}
    
    async def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[OpportunityORM]:
        """
        Search opportunities by title or organization.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Matching opportunities
        """
        search_pattern = f"%{query}%"
        
        result = await self.session.execute(
            select(OpportunityORM)
            .where(
                (OpportunityORM.title.ilike(search_pattern)) |
                (OpportunityORM.organization.ilike(search_pattern)) |
                (OpportunityORM.description.ilike(search_pattern))
            )
            .order_by(OpportunityORM.fit_score.desc().nulls_last())
            .limit(limit)
        )
        
        return list(result.scalars().all())
