"""
Rule Management Service

Handles business rule and category management including:
- Rule CRUD operations
- Category management
- Rule validation
- Version management
- Rule activation/deactivation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json

from backend.shared.database.rules_models import (
    RuleCategory,
    BusinessRule,
    RuleCondition,
    RuleAction,
    RuleVersion
)
from backend.shared.common.response import CustomException
from .schemas import (
    RuleCategoryCreate,
    RuleCategoryUpdate,
    BusinessRuleCreate,
    BusinessRuleUpdate,
    RuleDefinition,
    ConditionOperator,
    DataType
)


class RuleService:
    """Service for managing business rules and categories"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CATEGORY MANAGEMENT ====================
    
    def create_category(self, category_data: RuleCategoryCreate) -> RuleCategory:
        """
        Create a new rule category
        
        Args:
            category_data: Category creation data
            
        Returns:
            Created category
        """
        # Check for duplicate category code
        existing = self.db.query(RuleCategory).filter(
            and_(
                RuleCategory.category_code == category_data.category_code,
                RuleCategory.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Category with code '{category_data.category_code}' already exists"
            )
        
        # Validate parent category if provided
        if category_data.parent_category_id:
            parent = self.db.query(RuleCategory).filter(
                and_(
                    RuleCategory.id == category_data.parent_category_id,
                    RuleCategory.tenant_id == self.tenant_id
                )
            ).first()
            
            if not parent:
                raise CustomException(
                    status_code=404,
                    message="Parent category not found"
                )
        
        # Create category
        category = RuleCategory(
            category_code=category_data.category_code,
            category_name=category_data.category_name,
            description=category_data.description,
            parent_category_id=category_data.parent_category_id,
            is_active=category_data.is_active,
            tenant_id=self.tenant_id
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_category(self, category_id: int) -> RuleCategory:
        """Get category by ID"""
        category = self.db.query(RuleCategory).filter(
            and_(
                RuleCategory.id == category_id,
                RuleCategory.tenant_id == self.tenant_id
            )
        ).first()
        
        if not category:
            raise CustomException(status_code=404, message="Category not found")
        
        return category
    
    def list_categories(
        self,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RuleCategory]:
        """List categories with filters"""
        query = self.db.query(RuleCategory).filter(
            RuleCategory.tenant_id == self.tenant_id
        )
        
        if parent_id is not None:
            query = query.filter(RuleCategory.parent_category_id == parent_id)
        
        if is_active is not None:
            query = query.filter(RuleCategory.is_active == is_active)
        
        query = query.order_by(RuleCategory.category_name)
        
        return query.offset(skip).limit(limit).all()
    
    def update_category(
        self,
        category_id: int,
        category_data: RuleCategoryUpdate
    ) -> RuleCategory:
        """Update category"""
        category = self.get_category(category_id)
        
        # Update fields
        update_data = category_data.dict(exclude_unset=True)
        
        # Validate parent if being updated
        if 'parent_category_id' in update_data and update_data['parent_category_id']:
            if update_data['parent_category_id'] == category_id:
                raise CustomException(
                    status_code=400,
                    message="Category cannot be its own parent"
                )
            
            parent = self.get_category(update_data['parent_category_id'])
            if not parent:
                raise CustomException(
                    status_code=404,
                    message="Parent category not found"
                )
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category (if no rules associated)"""
        category = self.get_category(category_id)
        
        # Check if category has rules
        rule_count = self.db.query(func.count(BusinessRule.id)).filter(
            and_(
                BusinessRule.category_id == category_id,
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_deleted == False
            )
        ).scalar()
        
        if rule_count > 0:
            raise CustomException(
                status_code=400,
                message=f"Cannot delete category with {rule_count} associated rules"
            )
        
        self.db.delete(category)
        self.db.commit()
        
        return True
    
    # ==================== RULE MANAGEMENT ====================
    
    def create_rule(self, rule_data: BusinessRuleCreate) -> BusinessRule:
        """
        Create a new business rule
        
        Args:
            rule_data: Rule creation data
            
        Returns:
            Created rule
        """
        # Check for duplicate rule code
        existing = self.db.query(BusinessRule).filter(
            and_(
                BusinessRule.rule_code == rule_data.rule_code,
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_deleted == False
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Rule with code '{rule_data.rule_code}' already exists"
            )
        
        # Validate category
        category = self.get_category(rule_data.category_id)
        
        # Validate rule definition
        self._validate_rule_definition(rule_data.rule_definition)
        
        # Create rule
        rule = BusinessRule(
            rule_code=rule_data.rule_code,
            rule_name=rule_data.rule_name,
            category_id=rule_data.category_id,
            rule_type=rule_data.rule_type.value,
            description=rule_data.description,
            priority=rule_data.priority,
            rule_definition=rule_data.rule_definition.dict(),
            evaluation_strategy=rule_data.evaluation_strategy.value,
            version=1,
            is_active=False,  # New rules start as inactive
            effective_from=rule_data.effective_from,
            effective_to=rule_data.effective_to,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(rule)
        self.db.flush()
        
        # Create initial version
        self._create_version(rule, "Initial version")
        
        # Parse and store conditions
        self._store_conditions(rule, rule_data.rule_definition)
        
        # Parse and store actions
        self._store_actions(rule, rule_data.rule_definition)
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def get_rule(self, rule_id: int) -> BusinessRule:
        """Get rule by ID"""
        rule = self.db.query(BusinessRule).filter(
            and_(
                BusinessRule.id == rule_id,
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_deleted == False
            )
        ).first()
        
        if not rule:
            raise CustomException(status_code=404, message="Rule not found")
        
        return rule
    
    def get_rule_by_code(self, rule_code: str) -> Optional[BusinessRule]:
        """Get rule by code"""
        return self.db.query(BusinessRule).filter(
            and_(
                BusinessRule.rule_code == rule_code,
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_deleted == False
            )
        ).first()
    
    def list_rules(
        self,
        category_id: Optional[int] = None,
        rule_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BusinessRule]:
        """List rules with filters"""
        query = self.db.query(BusinessRule).filter(
            and_(
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_deleted == False
            )
        )
        
        if category_id:
            query = query.filter(BusinessRule.category_id == category_id)
        
        if rule_type:
            query = query.filter(BusinessRule.rule_type == rule_type)
        
        if is_active is not None:
            query = query.filter(BusinessRule.is_active == is_active)
        
        if search:
            query = query.filter(
                or_(
                    BusinessRule.rule_code.ilike(f"%{search}%"),
                    BusinessRule.rule_name.ilike(f"%{search}%"),
                    BusinessRule.description.ilike(f"%{search}%")
                )
            )
        
        # Check effective dates
        today = date.today()
        query = query.filter(
            or_(
                BusinessRule.effective_from.is_(None),
                BusinessRule.effective_from <= today
            )
        ).filter(
            or_(
                BusinessRule.effective_to.is_(None),
                BusinessRule.effective_to >= today
            )
        )
        
        query = query.order_by(BusinessRule.priority, BusinessRule.rule_name)
        
        return query.offset(skip).limit(limit).all()
    
    def update_rule(
        self,
        rule_id: int,
        rule_data: BusinessRuleUpdate
    ) -> BusinessRule:
        """Update rule"""
        rule = self.get_rule(rule_id)
        
        # Check if rule is active - create new version if so
        if rule.is_active and rule_data.rule_definition:
            raise CustomException(
                status_code=400,
                message="Cannot modify active rule definition. Deactivate first or create new version."
            )
        
        update_data = rule_data.dict(exclude_unset=True)
        
        # Track changes for version history
        changes = []
        
        for field, value in update_data.items():
            if field == 'rule_definition' and value:
                # Validate new definition
                self._validate_rule_definition(RuleDefinition(**value))
                
                # Update definition
                setattr(rule, field, value)
                changes.append(f"Updated rule definition")
                
                # Update conditions and actions
                self._delete_conditions(rule)
                self._delete_actions(rule)
                self._store_conditions(rule, RuleDefinition(**value))
                self._store_actions(rule, RuleDefinition(**value))
            else:
                old_value = getattr(rule, field)
                if old_value != value:
                    setattr(rule, field, value)
                    changes.append(f"Changed {field} from {old_value} to {value}")
        
        rule.updated_by = self.user_id
        rule.version += 1
        
        # Create version snapshot
        if changes:
            change_summary = "; ".join(changes)
            self._create_version(rule, change_summary)
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """Soft delete rule"""
        rule = self.get_rule(rule_id)
        
        if rule.is_active:
            raise CustomException(
                status_code=400,
                message="Cannot delete active rule. Deactivate first."
            )
        
        rule.is_deleted = True
        rule.updated_by = self.user_id
        
        self.db.commit()
        
        return True
    
    # ==================== RULE ACTIVATION ====================
    
    def activate_rule(self, rule_id: int) -> BusinessRule:
        """Activate a rule"""
        rule = self.get_rule(rule_id)
        
        if rule.is_active:
            raise CustomException(
                status_code=400,
                message="Rule is already active"
            )
        
        # Validate rule before activation
        self._validate_rule_definition(RuleDefinition(**rule.rule_definition))
        
        rule.is_active = True
        rule.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def deactivate_rule(self, rule_id: int) -> BusinessRule:
        """Deactivate a rule"""
        rule = self.get_rule(rule_id)
        
        if not rule.is_active:
            raise CustomException(
                status_code=400,
                message="Rule is already inactive"
            )
        
        rule.is_active = False
        rule.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    # ==================== RULE CLONING ====================
    
    def clone_rule(
        self,
        rule_id: int,
        new_code: str,
        new_name: str,
        copy_version_history: bool = False
    ) -> BusinessRule:
        """Clone an existing rule"""
        source_rule = self.get_rule(rule_id)
        
        # Check new code is unique
        if self.get_rule_by_code(new_code):
            raise CustomException(
                status_code=400,
                message=f"Rule with code '{new_code}' already exists"
            )
        
        # Create cloned rule
        cloned_rule = BusinessRule(
            rule_code=new_code,
            rule_name=new_name,
            category_id=source_rule.category_id,
            rule_type=source_rule.rule_type,
            description=f"Cloned from {source_rule.rule_code}: {source_rule.description or ''}",
            priority=source_rule.priority,
            rule_definition=source_rule.rule_definition,
            evaluation_strategy=source_rule.evaluation_strategy,
            version=1,
            is_active=False,
            effective_from=source_rule.effective_from,
            effective_to=source_rule.effective_to,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(cloned_rule)
        self.db.flush()
        
        # Clone conditions
        for condition in source_rule.conditions:
            cloned_condition = RuleCondition(
                rule_id=cloned_rule.id,
                condition_group=condition.condition_group,
                sequence=condition.sequence,
                field_path=condition.field_path,
                operator=condition.operator,
                value=condition.value,
                data_type=condition.data_type,
                is_negated=condition.is_negated,
                tenant_id=self.tenant_id
            )
            self.db.add(cloned_condition)
        
        # Clone actions
        for action in source_rule.actions:
            cloned_action = RuleAction(
                rule_id=cloned_rule.id,
                action_type=action.action_type,
                action_config=action.action_config,
                execution_order=action.execution_order,
                tenant_id=self.tenant_id
            )
            self.db.add(cloned_action)
        
        # Create initial version
        self._create_version(cloned_rule, f"Cloned from rule {source_rule.rule_code}")
        
        # Copy version history if requested
        if copy_version_history:
            for version in source_rule.versions:
                cloned_version = RuleVersion(
                    rule_id=cloned_rule.id,
                    version_number=version.version_number,
                    rule_snapshot=version.rule_snapshot,
                    change_summary=f"Cloned: {version.change_summary}",
                    tenant_id=self.tenant_id,
                    changed_by=self.user_id
                )
                self.db.add(cloned_version)
        
        self.db.commit()
        self.db.refresh(cloned_rule)
        
        return cloned_rule
    
    # ==================== VERSION MANAGEMENT ====================
    
    def get_rule_versions(self, rule_id: int) -> List[RuleVersion]:
        """Get version history for a rule"""
        rule = self.get_rule(rule_id)
        
        return self.db.query(RuleVersion).filter(
            and_(
                RuleVersion.rule_id == rule_id,
                RuleVersion.tenant_id == self.tenant_id
            )
        ).order_by(RuleVersion.version_number.desc()).all()
    
    def revert_to_version(self, rule_id: int, version_number: int) -> BusinessRule:
        """Revert rule to a specific version"""
        rule = self.get_rule(rule_id)
        
        if rule.is_active:
            raise CustomException(
                status_code=400,
                message="Cannot revert active rule. Deactivate first."
            )
        
        # Find version
        version = self.db.query(RuleVersion).filter(
            and_(
                RuleVersion.rule_id == rule_id,
                RuleVersion.version_number == version_number,
                RuleVersion.tenant_id == self.tenant_id
            )
        ).first()
        
        if not version:
            raise CustomException(
                status_code=404,
                message=f"Version {version_number} not found"
            )
        
        # Restore from snapshot
        snapshot = version.rule_snapshot
        rule.rule_definition = snapshot.get('rule_definition', rule.rule_definition)
        rule.priority = snapshot.get('priority', rule.priority)
        rule.evaluation_strategy = snapshot.get('evaluation_strategy', rule.evaluation_strategy)
        rule.version += 1
        rule.updated_by = self.user_id
        
        # Recreate conditions and actions
        self._delete_conditions(rule)
        self._delete_actions(rule)
        self._store_conditions(rule, RuleDefinition(**rule.rule_definition))
        self._store_actions(rule, RuleDefinition(**rule.rule_definition))
        
        # Create version entry
        self._create_version(rule, f"Reverted to version {version_number}")
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    # ==================== RULE STATISTICS ====================
    
    def get_rule_stats(self, rule_id: int) -> Dict[str, Any]:
        """Get statistics for a rule"""
        from backend.shared.database.rules_models import RuleEvaluation
        
        rule = self.get_rule(rule_id)
        
        total_evaluations = self.db.query(func.count(RuleEvaluation.id)).filter(
            and_(
                RuleEvaluation.rule_id == rule_id,
                RuleEvaluation.tenant_id == self.tenant_id
            )
        ).scalar() or 0
        
        total_matches = self.db.query(func.count(RuleEvaluation.id)).filter(
            and_(
                RuleEvaluation.rule_id == rule_id,
                RuleEvaluation.matched == True,
                RuleEvaluation.tenant_id == self.tenant_id
            )
        ).scalar() or 0
        
        avg_execution_time = self.db.query(func.avg(RuleEvaluation.execution_time_ms)).filter(
            and_(
                RuleEvaluation.rule_id == rule_id,
                RuleEvaluation.tenant_id == self.tenant_id
            )
        ).scalar() or 0
        
        last_evaluation = self.db.query(RuleEvaluation).filter(
            and_(
                RuleEvaluation.rule_id == rule_id,
                RuleEvaluation.tenant_id == self.tenant_id
            )
        ).order_by(RuleEvaluation.evaluated_at.desc()).first()
        
        return {
            "rule_id": rule_id,
            "rule_code": rule.rule_code,
            "total_evaluations": total_evaluations,
            "total_matches": total_matches,
            "match_rate": (total_matches / total_evaluations * 100) if total_evaluations > 0 else 0,
            "avg_execution_time_ms": float(avg_execution_time) if avg_execution_time else 0,
            "last_evaluated_at": last_evaluation.evaluated_at if last_evaluation else None
        }
    
    # ==================== HELPER METHODS ====================
    
    def _validate_rule_definition(self, rule_def: RuleDefinition) -> bool:
        """Validate rule definition structure"""
        # Check that either conditions or condition_groups is provided
        if not rule_def.conditions and not rule_def.condition_groups:
            raise CustomException(
                status_code=400,
                message="Rule must have either 'conditions' or 'condition_groups'"
            )
        
        # Validate actions
        if not rule_def.actions or len(rule_def.actions) == 0:
            raise CustomException(
                status_code=400,
                message="Rule must have at least one action"
            )
        
        # Validate condition operators and data types
        conditions_to_validate = []
        if rule_def.conditions:
            conditions_to_validate.extend(rule_def.conditions)
        if rule_def.condition_groups:
            for group in rule_def.condition_groups:
                conditions_to_validate.extend(group.conditions)
        
        for condition in conditions_to_validate:
            # Validate operator exists
            if condition.operator not in ConditionOperator.__members__.values():
                raise CustomException(
                    status_code=400,
                    message=f"Invalid operator: {condition.operator}"
                )
            
            # Validate data type exists
            if condition.data_type not in DataType.__members__.values():
                raise CustomException(
                    status_code=400,
                    message=f"Invalid data type: {condition.data_type}"
                )
        
        return True
    
    def _store_conditions(self, rule: BusinessRule, rule_def: RuleDefinition):
        """Store conditions in database"""
        if rule_def.conditions:
            for idx, condition in enumerate(rule_def.conditions):
                db_condition = RuleCondition(
                    rule_id=rule.id,
                    condition_group=1,
                    sequence=idx + 1,
                    field_path=condition.field_path,
                    operator=condition.operator.value,
                    value=json.dumps(condition.value),
                    data_type=condition.data_type.value,
                    is_negated=condition.is_negated,
                    tenant_id=self.tenant_id
                )
                self.db.add(db_condition)
        
        elif rule_def.condition_groups:
            for group in rule_def.condition_groups:
                for idx, condition in enumerate(group.conditions):
                    db_condition = RuleCondition(
                        rule_id=rule.id,
                        condition_group=group.group_id,
                        sequence=idx + 1,
                        field_path=condition.field_path,
                        operator=condition.operator.value,
                        value=json.dumps(condition.value),
                        data_type=condition.data_type.value,
                        is_negated=condition.is_negated,
                        tenant_id=self.tenant_id
                    )
                    self.db.add(db_condition)
    
    def _store_actions(self, rule: BusinessRule, rule_def: RuleDefinition):
        """Store actions in database"""
        for action in rule_def.actions:
            db_action = RuleAction(
                rule_id=rule.id,
                action_type=action.action_type.value,
                action_config=action.action_config,
                execution_order=action.execution_order,
                tenant_id=self.tenant_id
            )
            self.db.add(db_action)
    
    def _delete_conditions(self, rule: BusinessRule):
        """Delete all conditions for a rule"""
        self.db.query(RuleCondition).filter(
            and_(
                RuleCondition.rule_id == rule.id,
                RuleCondition.tenant_id == self.tenant_id
            )
        ).delete()
    
    def _delete_actions(self, rule: BusinessRule):
        """Delete all actions for a rule"""
        self.db.query(RuleAction).filter(
            and_(
                RuleAction.rule_id == rule.id,
                RuleAction.tenant_id == self.tenant_id
            )
        ).delete()
    
    def _create_version(self, rule: BusinessRule, change_summary: str):
        """Create a version snapshot"""
        version = RuleVersion(
            rule_id=rule.id,
            version_number=rule.version,
            rule_snapshot={
                "rule_code": rule.rule_code,
                "rule_name": rule.rule_name,
                "rule_type": rule.rule_type,
                "priority": rule.priority,
                "rule_definition": rule.rule_definition,
                "evaluation_strategy": rule.evaluation_strategy,
                "is_active": rule.is_active
            },
            change_summary=change_summary,
            tenant_id=self.tenant_id,
            changed_by=self.user_id
        )
        
        self.db.add(version)
