"""
Document Checklist Service
Business logic for managing document checklists and requirements
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from .document_models import (
    DocumentChecklist, DocumentChecklistFilter, DocumentChecklistStats,
    DocumentChecklistClone, ChecklistStatus, DocumentTemplate,
    DocumentRequirement, DocumentEvaluationContext, EvaluatedRequirement,
    ChecklistEvaluationResult, ConditionalRule, DocumentCondition,
    ConditionOperator, DocumentType, CustomerType
)


class DocumentService:
    """Service for document checklist management"""
    
    def __init__(self):
        """Initialize service"""
        self.checklists_storage: Dict[str, DocumentChecklist] = {}
        self.templates_storage: Dict[str, DocumentTemplate] = {}
    
    # ========================================================================
    # CRUD OPERATIONS - CHECKLISTS
    # ========================================================================
    
    def create_checklist(
        self,
        checklist_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> DocumentChecklist:
        """Create new document checklist"""
        checklist_id = str(uuid.uuid4())
        
        # Check if checklist code already exists
        if any(c.checklist_code == checklist_data.get('checklist_code') 
               for c in self.checklists_storage.values() 
               if c.tenant_id == tenant_id):
            raise ValueError(f"Checklist code {checklist_data.get('checklist_code')} already exists")
        
        # Create checklist
        checklist = DocumentChecklist(
            id=checklist_id,
            tenant_id=tenant_id,
            **checklist_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.checklists_storage[checklist_id] = checklist
        return checklist
    
    def get_checklist(self, checklist_id: str, tenant_id: str) -> DocumentChecklist:
        """Get checklist by ID"""
        checklist = self.checklists_storage.get(checklist_id)
        if not checklist or checklist.tenant_id != tenant_id:
            raise ValueError(f"Checklist {checklist_id} not found")
        return checklist
    
    def get_checklist_by_code(self, checklist_code: str, tenant_id: str) -> DocumentChecklist:
        """Get checklist by code"""
        for checklist in self.checklists_storage.values():
            if checklist.tenant_id == tenant_id and checklist.checklist_code == checklist_code:
                return checklist
        raise ValueError(f"Checklist with code {checklist_code} not found")
    
    def update_checklist(
        self,
        checklist_id: str,
        checklist_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> DocumentChecklist:
        """Update checklist"""
        checklist = self.get_checklist(checklist_id, tenant_id)
        
        for key, value in checklist_data.items():
            if hasattr(checklist, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(checklist, key, value)
        
        checklist.updated_at = datetime.utcnow()
        checklist.updated_by = user_id
        
        self.checklists_storage[checklist_id] = checklist
        return checklist
    
    def delete_checklist(self, checklist_id: str, tenant_id: str) -> None:
        """Delete checklist"""
        checklist = self.get_checklist(checklist_id, tenant_id)
        del self.checklists_storage[checklist_id]
    
    def list_checklists(
        self,
        tenant_id: str,
        filters: Optional[DocumentChecklistFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentChecklist]:
        """List checklists with filters"""
        checklists = [c for c in self.checklists_storage.values() if c.tenant_id == tenant_id]
        
        if filters:
            if filters.status:
                checklists = [c for c in checklists if c.status == filters.status]
            if filters.product_id:
                checklists = [c for c in checklists if c.product_id == filters.product_id]
            if filters.product_code:
                checklists = [c for c in checklists if c.product_code == filters.product_code]
            if filters.search_term:
                term = filters.search_term.lower()
                checklists = [c for c in checklists if 
                            term in c.checklist_code.lower() or 
                            term in c.checklist_name.lower() or 
                            term in c.description.lower()]
        
        checklists.sort(key=lambda c: (c.priority, c.created_at), reverse=False)
        return checklists[skip:skip + limit]
    
    # ========================================================================
    # CHECKLIST OPERATIONS
    # ========================================================================
    
    def clone_checklist(
        self,
        checklist_id: str,
        clone_data: DocumentChecklistClone,
        tenant_id: str,
        user_id: str
    ) -> DocumentChecklist:
        """Clone checklist"""
        original = self.get_checklist(checklist_id, tenant_id)
        
        checklist_data = original.dict(exclude={'id', 'created_at', 'updated_at', 'created_by', 'updated_by'})
        checklist_data['checklist_code'] = clone_data.new_checklist_code
        checklist_data['checklist_name'] = clone_data.new_checklist_name or f"{original.checklist_name} (Copy)"
        if clone_data.new_product_id:
            checklist_data['product_id'] = clone_data.new_product_id
        checklist_data['status'] = ChecklistStatus.DRAFT
        
        return self.create_checklist(checklist_data, tenant_id, user_id)
    
    def activate_checklist(self, checklist_id: str, tenant_id: str, user_id: str) -> DocumentChecklist:
        """Activate checklist"""
        checklist = self.get_checklist(checklist_id, tenant_id)
        checklist.status = ChecklistStatus.ACTIVE
        checklist.updated_at = datetime.utcnow()
        checklist.updated_by = user_id
        self.checklists_storage[checklist_id] = checklist
        return checklist
    
    def deactivate_checklist(self, checklist_id: str, tenant_id: str, user_id: str) -> DocumentChecklist:
        """Deactivate checklist"""
        checklist = self.get_checklist(checklist_id, tenant_id)
        checklist.status = ChecklistStatus.INACTIVE
        checklist.updated_at = datetime.utcnow()
        checklist.updated_by = user_id
        self.checklists_storage[checklist_id] = checklist
        return checklist
    
    # ========================================================================
    # CONDITIONAL LOGIC EVALUATION
    # ========================================================================
    
    def evaluate_checklist(
        self,
        checklist_id: str,
        context: DocumentEvaluationContext,
        tenant_id: str
    ) -> ChecklistEvaluationResult:
        """Evaluate checklist and determine required documents"""
        checklist = self.get_checklist(checklist_id, tenant_id)
        
        evaluated_requirements = []
        required_documents = []
        mandatory_count = 0
        conditional_count = 0
        
        for requirement in checklist.requirements:
            # Check if requirement applies to customer type
            if requirement.customer_types and context.customer_type not in requirement.customer_types:
                continue
            
            # Evaluate conditional requirements
            is_required = True
            reason = "Mandatory requirement"
            
            if requirement.conditional and requirement.conditional_rule:
                is_required = self._evaluate_conditional_rule(requirement.conditional_rule, context)
                reason = "Conditional requirement evaluated"
                conditional_count += 1
            elif requirement.mandatory:
                mandatory_count += 1
            else:
                is_required = False
                reason = "Optional requirement"
            
            evaluated_req = EvaluatedRequirement(
                requirement=requirement,
                is_required=is_required,
                reason=reason
            )
            evaluated_requirements.append(evaluated_req)
            
            if is_required:
                required_documents.append(requirement.document_type)
        
        return ChecklistEvaluationResult(
            checklist_id=checklist.id,
            checklist_code=checklist.checklist_code,
            checklist_name=checklist.checklist_name,
            total_requirements=len(checklist.requirements),
            mandatory_requirements=mandatory_count,
            conditional_requirements=conditional_count,
            evaluated_requirements=evaluated_requirements,
            required_documents=list(set(required_documents))
        )
    
    def _evaluate_conditional_rule(
        self,
        rule: ConditionalRule,
        context: DocumentEvaluationContext
    ) -> bool:
        """Evaluate conditional rule"""
        results = []
        
        for condition in rule.conditions:
            result = self._evaluate_condition(condition, context)
            results.append(result)
        
        if rule.logic == "AND":
            return all(results)
        else:  # OR
            return any(results)
    
    def _evaluate_condition(
        self,
        condition: DocumentCondition,
        context: DocumentEvaluationContext
    ) -> bool:
        """Evaluate single condition"""
        # Get field value from context
        field_value = getattr(context, condition.field, None)
        if field_value is None:
            field_value = context.custom_fields.get(condition.field)
        
        if field_value is None:
            return False
        
        # Evaluate based on operator
        if condition.operator == ConditionOperator.EQUALS:
            return field_value == condition.value
        elif condition.operator == ConditionOperator.NOT_EQUALS:
            return field_value != condition.value
        elif condition.operator == ConditionOperator.IN:
            return field_value in condition.value
        elif condition.operator == ConditionOperator.NOT_IN:
            return field_value not in condition.value
        elif condition.operator == ConditionOperator.GREATER_THAN:
            return float(field_value) > float(condition.value)
        elif condition.operator == ConditionOperator.LESS_THAN:
            return float(field_value) < float(condition.value)
        elif condition.operator == ConditionOperator.CONTAINS:
            return condition.value in str(field_value)
        
        return False
    
    # ========================================================================
    # TEMPLATE MANAGEMENT
    # ========================================================================
    
    def create_template(
        self,
        template_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> DocumentTemplate:
        """Create document template"""
        template_id = str(uuid.uuid4())
        
        template = DocumentTemplate(
            id=template_id,
            tenant_id=tenant_id,
            **template_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.templates_storage[template_id] = template
        return template
    
    def get_template(self, template_id: str, tenant_id: str) -> DocumentTemplate:
        """Get template by ID"""
        template = self.templates_storage.get(template_id)
        if not template or template.tenant_id != tenant_id:
            raise ValueError(f"Template {template_id} not found")
        return template
    
    def list_templates(
        self,
        tenant_id: str,
        document_type: Optional[DocumentType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DocumentTemplate]:
        """List templates"""
        templates = [t for t in self.templates_storage.values() if t.tenant_id == tenant_id]
        
        if document_type:
            templates = [t for t in templates if t.document_type == document_type]
        
        return templates[skip:skip + limit]
    
    def update_template(
        self,
        template_id: str,
        template_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> DocumentTemplate:
        """Update template"""
        template = self.get_template(template_id, tenant_id)
        
        for key, value in template_data.items():
            if hasattr(template, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(template, key, value)
        
        template.updated_at = datetime.utcnow()
        template.updated_by = user_id
        
        self.templates_storage[template_id] = template
        return template
    
    def delete_template(self, template_id: str, tenant_id: str) -> None:
        """Delete template"""
        template = self.get_template(template_id, tenant_id)
        del self.templates_storage[template_id]
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_stats(self, tenant_id: str) -> DocumentChecklistStats:
        """Get statistics"""
        checklists = [c for c in self.checklists_storage.values() if c.tenant_id == tenant_id]
        templates = [t for t in self.templates_storage.values() if t.tenant_id == tenant_id]
        
        active_count = sum(1 for c in checklists if c.status == ChecklistStatus.ACTIVE)
        draft_count = sum(1 for c in checklists if c.status == ChecklistStatus.DRAFT)
        
        checklists_by_product = {}
        for checklist in checklists:
            if checklist.product_code:
                checklists_by_product[checklist.product_code] = checklists_by_product.get(checklist.product_code, 0) + 1
        
        return DocumentChecklistStats(
            total_checklists=len(checklists),
            active_checklists=active_count,
            draft_checklists=draft_count,
            total_templates=len(templates),
            checklists_by_product=checklists_by_product
        )
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate_checklist_data(self, checklist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate checklist data"""
        errors = []
        warnings = []
        
        if not checklist_data.get('checklist_code'):
            errors.append("Checklist code is required")
        if not checklist_data.get('checklist_name'):
            errors.append("Checklist name is required")
        
        requirements = checklist_data.get('requirements', [])
        if len(requirements) == 0:
            warnings.append("No document requirements defined")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# Create service instance
document_service = DocumentService()
