"""
Strategy Service

Service for managing decision strategies - configuration of thresholds,
rules, and behavior for instant decisions.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.shared.database.decision_models import DecisionStrategy
from backend.services.decision.schemas import (
    DecisionStrategyCreate,
    DecisionStrategyUpdate,
    DecisionStrategyResponse,
    DecisionType
)


class StrategyService:
    """Service for managing decision strategies"""

    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    async def create_strategy(
        self,
        data: DecisionStrategyCreate
    ) -> DecisionStrategy:
        """Create a new decision strategy"""
        # Check if code already exists
        existing = await self.get_strategy_by_code(data.strategy_code)
        if existing:
            raise ValueError(f"Strategy with code '{data.strategy_code}' already exists")
        
        # If this is marked as default, unset other defaults for this decision type
        if data.is_default:
            await self._unset_defaults(data.decision_type.value)
        
        strategy = DecisionStrategy(
            strategy_code=data.strategy_code,
            strategy_name=data.strategy_name,
            decision_type=data.decision_type.value,
            description=data.description,
            strategy_config=data.strategy_config.dict(),
            auto_approve_threshold=data.auto_approve_threshold,
            manual_review_threshold=data.manual_review_threshold,
            auto_reject_threshold=data.auto_reject_threshold,
            max_amount_auto_approve=data.max_amount_auto_approve,
            min_amount=data.min_amount,
            priority=data.priority,
            is_active=data.is_active,
            is_default=data.is_default,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(strategy)
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return strategy

    async def update_strategy(
        self,
        strategy_id: int,
        data: DecisionStrategyUpdate
    ) -> DecisionStrategy:
        """Update an existing strategy"""
        strategy = await self.get_strategy(strategy_id)
        
        if not strategy:
            raise ValueError("Strategy not found")
        
        # If marking as default, unset other defaults
        if data.is_default and not strategy.is_default:
            await self._unset_defaults(strategy.decision_type)
        
        # Update fields
        if data.strategy_name is not None:
            strategy.strategy_name = data.strategy_name
        if data.description is not None:
            strategy.description = data.description
        if data.strategy_config is not None:
            strategy.strategy_config = data.strategy_config.dict()
        if data.auto_approve_threshold is not None:
            strategy.auto_approve_threshold = data.auto_approve_threshold
        if data.manual_review_threshold is not None:
            strategy.manual_review_threshold = data.manual_review_threshold
        if data.auto_reject_threshold is not None:
            strategy.auto_reject_threshold = data.auto_reject_threshold
        if data.max_amount_auto_approve is not None:
            strategy.max_amount_auto_approve = data.max_amount_auto_approve
        if data.min_amount is not None:
            strategy.min_amount = data.min_amount
        if data.priority is not None:
            strategy.priority = data.priority
        if data.is_active is not None:
            strategy.is_active = data.is_active
        if data.is_default is not None:
            strategy.is_default = data.is_default
        
        strategy.updated_by = self.user_id
        strategy.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return strategy

    async def get_strategy(self, strategy_id: int) -> Optional[DecisionStrategy]:
        """Get strategy by ID"""
        query = select(DecisionStrategy).where(
            and_(
                DecisionStrategy.id == strategy_id,
                DecisionStrategy.tenant_id == self.tenant_id,
                DecisionStrategy.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_strategy_by_code(self, strategy_code: str) -> Optional[DecisionStrategy]:
        """Get strategy by code"""
        query = select(DecisionStrategy).where(
            and_(
                DecisionStrategy.strategy_code == strategy_code,
                DecisionStrategy.tenant_id == self.tenant_id,
                DecisionStrategy.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_strategies(
        self,
        decision_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[DecisionStrategy], int]:
        """List strategies with filters"""
        conditions = [
            DecisionStrategy.tenant_id == self.tenant_id,
            DecisionStrategy.is_deleted == False
        ]
        
        if decision_type:
            conditions.append(DecisionStrategy.decision_type == decision_type)
        
        if is_active is not None:
            conditions.append(DecisionStrategy.is_active == is_active)
        
        # Count query
        count_query = select(func.count(DecisionStrategy.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Data query
        query = select(DecisionStrategy).where(
            and_(*conditions)
        ).order_by(
            DecisionStrategy.priority.asc(),
            DecisionStrategy.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        strategies = list(result.scalars().all())
        
        return strategies, total

    async def delete_strategy(self, strategy_id: int) -> bool:
        """Soft delete a strategy"""
        strategy = await self.get_strategy(strategy_id)
        
        if not strategy:
            return False
        
        strategy.is_deleted = True
        strategy.is_active = False
        strategy.updated_by = self.user_id
        strategy.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return True

    async def activate_strategy(self, strategy_id: int) -> DecisionStrategy:
        """Activate a strategy"""
        strategy = await self.get_strategy(strategy_id)
        
        if not strategy:
            raise ValueError("Strategy not found")
        
        strategy.is_active = True
        strategy.updated_by = self.user_id
        strategy.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return strategy

    async def deactivate_strategy(self, strategy_id: int) -> DecisionStrategy:
        """Deactivate a strategy"""
        strategy = await self.get_strategy(strategy_id)
        
        if not strategy:
            raise ValueError("Strategy not found")
        
        strategy.is_active = False
        strategy.updated_by = self.user_id
        strategy.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return strategy

    async def get_strategy_stats(self, strategy_code: str) -> Dict[str, Any]:
        """Get performance statistics for a strategy"""
        strategy = await self.get_strategy_by_code(strategy_code)
        
        if not strategy:
            raise ValueError("Strategy not found")
        
        approval_rate = 0.0
        if strategy.total_executions > 0:
            approval_rate = (strategy.total_approvals / strategy.total_executions) * 100
        
        rejection_rate = 0.0
        if strategy.total_executions > 0:
            rejection_rate = (strategy.total_rejections / strategy.total_executions) * 100
        
        return {
            "strategy_code": strategy.strategy_code,
            "strategy_name": strategy.strategy_name,
            "total_executions": strategy.total_executions,
            "total_approvals": strategy.total_approvals,
            "total_rejections": strategy.total_rejections,
            "approval_rate": round(approval_rate, 2),
            "rejection_rate": round(rejection_rate, 2),
            "avg_execution_time_ms": strategy.avg_execution_time_ms,
            "is_active": strategy.is_active
        }

    async def update_strategy_stats(
        self,
        strategy_id: int,
        execution_time_ms: int,
        decision_result: str
    ):
        """Update strategy statistics after execution"""
        strategy = await self.get_strategy(strategy_id)
        
        if not strategy:
            return
        
        strategy.total_executions += 1
        
        if decision_result == "approved":
            strategy.total_approvals += 1
        elif decision_result == "rejected":
            strategy.total_rejections += 1
        
        # Update average execution time
        if strategy.avg_execution_time_ms == 0:
            strategy.avg_execution_time_ms = execution_time_ms
        else:
            # Weighted average
            strategy.avg_execution_time_ms = int(
                (strategy.avg_execution_time_ms * (strategy.total_executions - 1) + execution_time_ms) / 
                strategy.total_executions
            )
        
        await self.db.commit()

    async def _unset_defaults(self, decision_type: str):
        """Unset default flag for other strategies of same decision type"""
        await self.db.execute(
            update(DecisionStrategy).where(
                and_(
                    DecisionStrategy.decision_type == decision_type,
                    DecisionStrategy.tenant_id == self.tenant_id,
                    DecisionStrategy.is_default == True
                )
            ).values(is_default=False)
        )
        await self.db.commit()

