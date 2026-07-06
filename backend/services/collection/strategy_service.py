"""
Collection Strategy Service
Manages collection strategies, templates, and automated action execution
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.collection_models import (
    CollectionStrategy,
    CommunicationTemplate,
    CollectionAction,
    ActionType,
    ActionStatus,
    TemplateType
)
from backend.shared.database.loan_models import LoanAccount


class CollectionStrategyService:
    """Service for managing collection strategies and actions"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # STRATEGY MANAGEMENT
    # ========================================================================
    
    async def create_strategy(
        self,
        strategy_name: str,
        strategy_code: str,
        dpd_min: int,
        dpd_max: int,
        action_type: ActionType,
        frequency_days: int = 1,
        max_attempts: int = 3,
        template_id: Optional[int] = None,
        escalation_rules: Optional[Dict] = None,
        escalate_after_days: Optional[int] = None,
        escalate_to_strategy_id: Optional[int] = None,
        description: Optional[str] = None,
        priority: int = 1
    ) -> CollectionStrategy:
        """
        Create a new collection strategy
        """
        # Validate DPD range
        if dpd_min > dpd_max:
            raise ValueError("DPD min cannot be greater than DPD max")
        
        # Check for overlapping strategies
        overlap_query = select(CollectionStrategy).where(
            and_(
                CollectionStrategy.tenant_id == self.tenant_id,
                CollectionStrategy.is_deleted == False,
                CollectionStrategy.is_active == True,
                or_(
                    and_(
                        CollectionStrategy.dpd_min <= dpd_min,
                        CollectionStrategy.dpd_max >= dpd_min
                    ),
                    and_(
                        CollectionStrategy.dpd_min <= dpd_max,
                        CollectionStrategy.dpd_max >= dpd_max
                    )
                )
            )
        )
        overlap_result = await self.db.execute(overlap_query)
        if overlap_result.scalar_one_or_none():
            raise ValueError("Strategy DPD range overlaps with existing strategy")
        
        # Create strategy
        strategy = CollectionStrategy(
            tenant_id=self.tenant_id,
            strategy_name=strategy_name,
            strategy_code=strategy_code,
            description=description,
            dpd_min=dpd_min,
            dpd_max=dpd_max,
            action_type=action_type,
            frequency_days=frequency_days,
            max_attempts=max_attempts,
            template_id=template_id,
            escalation_rules=escalation_rules,
            escalate_after_days=escalate_after_days,
            escalate_to_strategy_id=escalate_to_strategy_id,
            priority=priority,
            created_by=self.user_id
        )
        
        self.db.add(strategy)
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return strategy
    
    async def get_strategy(self, strategy_id: int) -> Optional[CollectionStrategy]:
        """Get strategy by ID"""
        query = select(CollectionStrategy).where(
            and_(
                CollectionStrategy.id == strategy_id,
                CollectionStrategy.tenant_id == self.tenant_id,
                CollectionStrategy.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_strategies_for_dpd(self, dpd: int) -> List[CollectionStrategy]:
        """Get all active strategies applicable for given DPD"""
        query = select(CollectionStrategy).where(
            and_(
                CollectionStrategy.tenant_id == self.tenant_id,
                CollectionStrategy.is_deleted == False,
                CollectionStrategy.is_active == True,
                CollectionStrategy.dpd_min <= dpd,
                CollectionStrategy.dpd_max >= dpd
            )
        ).order_by(CollectionStrategy.priority)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def list_strategies(
        self,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List all strategies with pagination"""
        conditions = [
            CollectionStrategy.tenant_id == self.tenant_id,
            CollectionStrategy.is_deleted == False
        ]
        
        if is_active is not None:
            conditions.append(CollectionStrategy.is_active == is_active)
        
        # Count total
        count_query = select(func.count(CollectionStrategy.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get strategies
        query = select(CollectionStrategy).where(and_(*conditions)).order_by(
            CollectionStrategy.dpd_min,
            CollectionStrategy.priority
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        strategies = result.scalars().all()
        
        return {
            "strategies": strategies,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
    
    async def update_strategy(
        self,
        strategy_id: int,
        **updates
    ) -> Optional[CollectionStrategy]:
        """Update strategy"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return None
        
        for key, value in updates.items():
            if hasattr(strategy, key) and value is not None:
                setattr(strategy, key, value)
        
        strategy.updated_by = self.user_id
        strategy.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return strategy
    
    async def delete_strategy(self, strategy_id: int) -> bool:
        """Soft delete strategy"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return False
        
        strategy.is_deleted = True
        strategy.updated_by = self.user_id
        strategy.updated_at = datetime.now()
        
        await self.db.commit()
        return True
    
    # ========================================================================
    # TEMPLATE MANAGEMENT
    # ========================================================================
    
    async def create_template(
        self,
        template_code: str,
        template_name: str,
        template_type: TemplateType,
        content: str,
        variables: Optional[List[str]] = None,
        subject: Optional[str] = None,
        language: str = "en",
        dpd_bucket: Optional[str] = None,
        category: Optional[str] = None
    ) -> CommunicationTemplate:
        """Create communication template"""
        template = CommunicationTemplate(
            tenant_id=self.tenant_id,
            template_code=template_code,
            template_name=template_name,
            template_type=template_type,
            content=content,
            variables=variables or [],
            subject=subject,
            language=language,
            dpd_bucket=dpd_bucket,
            category=category,
            created_by=self.user_id
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template
    
    async def get_template(self, template_id: int) -> Optional[CommunicationTemplate]:
        """Get template by ID"""
        query = select(CommunicationTemplate).where(
            and_(
                CommunicationTemplate.id == template_id,
                CommunicationTemplate.tenant_id == self.tenant_id,
                CommunicationTemplate.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_templates(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List templates with filters"""
        conditions = [
            CommunicationTemplate.tenant_id == self.tenant_id,
            CommunicationTemplate.is_deleted == False
        ]
        
        if template_type:
            conditions.append(CommunicationTemplate.template_type == template_type)
        if category:
            conditions.append(CommunicationTemplate.category == category)
        
        # Count total
        count_query = select(func.count(CommunicationTemplate.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get templates
        query = select(CommunicationTemplate).where(and_(*conditions)).order_by(
            CommunicationTemplate.template_type,
            CommunicationTemplate.template_name
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        return {
            "templates": templates,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
    
    def render_template(self, template: CommunicationTemplate, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        content = template.content
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"  # {{variable_name}}
            content = content.replace(placeholder, str(value))
        
        return content
    
    # ========================================================================
    # ACTION EXECUTION
    # ========================================================================
    
    async def execute_strategies(
        self,
        loan_account_id: Optional[int] = None,
        force_execution: bool = False
    ) -> Dict[str, Any]:
        """
        Execute collection strategies for overdue loans
        
        Args:
            loan_account_id: Execute for specific loan (if None, all overdue loans)
            force_execution: Execute even if frequency not met
        """
        # Get overdue loan accounts
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False,
            LoanAccount.status.in_(["overdue", "npa"]),
            LoanAccount.dpd > 0
        ]
        
        if loan_account_id:
            conditions.append(LoanAccount.id == loan_account_id)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        actions_created = 0
        actions_skipped = 0
        
        for account in accounts:
            # Get applicable strategies
            strategies = await self.get_strategies_for_dpd(account.dpd)
            
            for strategy in strategies:
                # Check if action should be executed
                if not force_execution:
                    should_execute = await self._should_execute_action(
                        account.id,
                        strategy.id,
                        strategy.frequency_days,
                        strategy.max_attempts
                    )
                    
                    if not should_execute:
                        actions_skipped += 1
                        continue
                
                # Create action
                await self._create_action(account, strategy)
                actions_created += 1
        
        return {
            "accounts_processed": len(accounts),
            "actions_created": actions_created,
            "actions_skipped": actions_skipped,
            "execution_time": datetime.now().isoformat()
        }
    
    async def _should_execute_action(
        self,
        loan_account_id: int,
        strategy_id: int,
        frequency_days: int,
        max_attempts: int
    ) -> bool:
        """Check if action should be executed based on frequency and attempts"""
        # Get last action for this loan and strategy
        last_action_query = select(CollectionAction).where(
            and_(
                CollectionAction.tenant_id == self.tenant_id,
                CollectionAction.loan_account_id == loan_account_id,
                CollectionAction.strategy_id == strategy_id,
                CollectionAction.is_deleted == False
            )
        ).order_by(desc(CollectionAction.action_date)).limit(1)
        
        result = await self.db.execute(last_action_query)
        last_action = result.scalar_one_or_none()
        
        # No previous action - execute
        if not last_action:
            return True
        
        # Check frequency
        days_since_last = (datetime.now().date() - last_action.action_date.date()).days
        if days_since_last < frequency_days:
            return False
        
        # Check max attempts
        attempts_query = select(func.count(CollectionAction.id)).where(
            and_(
                CollectionAction.tenant_id == self.tenant_id,
                CollectionAction.loan_account_id == loan_account_id,
                CollectionAction.strategy_id == strategy_id,
                CollectionAction.is_deleted == False
            )
        )
        attempts_result = await self.db.execute(attempts_query)
        attempts = attempts_result.scalar()
        
        if attempts >= max_attempts:
            return False
        
        return True
    
    async def _create_action(
        self,
        account: LoanAccount,
        strategy: CollectionStrategy
    ) -> CollectionAction:
        """Create collection action"""
        action = CollectionAction(
            tenant_id=self.tenant_id,
            loan_account_id=account.id,
            customer_id=account.customer_id,
            strategy_id=strategy.id,
            template_id=strategy.template_id,
            action_type=strategy.action_type,
            action_date=datetime.now(),
            scheduled_date=datetime.now(),
            status=ActionStatus.PENDING,
            created_by=self.user_id
        )
        
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        
        return action
    
    async def get_pending_actions(
        self,
        action_type: Optional[ActionType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get pending collection actions"""
        conditions = [
            CollectionAction.tenant_id == self.tenant_id,
            CollectionAction.is_deleted == False,
            CollectionAction.status == ActionStatus.PENDING
        ]
        
        if action_type:
            conditions.append(CollectionAction.action_type == action_type)
        
        # Count total
        count_query = select(func.count(CollectionAction.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get actions
        query = select(CollectionAction).where(and_(*conditions)).order_by(
            CollectionAction.scheduled_date
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        actions = result.scalars().all()
        
        return {
            "actions": actions,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
    
    async def update_action_status(
        self,
        action_id: int,
        status: ActionStatus,
        response_details: Optional[str] = None,
        next_action_date: Optional[datetime] = None,
        next_action_type: Optional[ActionType] = None
    ) -> Optional[CollectionAction]:
        """Update collection action status"""
        query = select(CollectionAction).where(
            and_(
                CollectionAction.id == action_id,
                CollectionAction.tenant_id == self.tenant_id,
                CollectionAction.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        action = result.scalar_one_or_none()
        
        if not action:
            return None
        
        action.status = status
        if response_details:
            action.response_details = response_details
            action.response_received = True
            action.response_time = datetime.now()
        
        if next_action_date:
            action.next_action_date = next_action_date
        if next_action_type:
            action.next_action_type = next_action_type
        
        await self.db.commit()
        await self.db.refresh(action)
        
        return action
    
    async def get_action_history(
        self,
        loan_account_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get action history for a loan account"""
        conditions = [
            CollectionAction.tenant_id == self.tenant_id,
            CollectionAction.loan_account_id == loan_account_id,
            CollectionAction.is_deleted == False
        ]
        
        # Count total
        count_query = select(func.count(CollectionAction.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get actions
        query = select(CollectionAction).where(and_(*conditions)).order_by(
            desc(CollectionAction.action_date)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        actions = result.scalars().all()
        
        return {
            "actions": actions,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
