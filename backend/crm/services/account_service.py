"""
CRM Account Management Service
Business logic for account operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from backend.shared.database.crm_account_models import (
    CRMAccount, CRMContact, CRMAccountRelationship, CRMActivity
)
from backend.shared.schemas.crm_account_schemas import (
    CRMAccountCreate, CRMAccountUpdate,
    CRMContactCreate, CRMContactUpdate,
    CRMAccountRelationshipCreate, CRMAccountRelationshipUpdate
)


def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary with proper serialization"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, UUID):
            result[column.name] = str(value)
        elif isinstance(value, datetime):
            result[column.name] = value.isoformat()
        elif hasattr(value, 'value'):  # Enum
            result[column.name] = value.value
        else:
            result[column.name] = value
    return result


class CRMAccountService:
    """Service for CRM Account operations"""
    
    @staticmethod
    def generate_account_number(db: Session, tenant_id: str) -> str:
        """Generate unique account number"""
        count = db.query(func.count(CRMAccount.id)).filter(
            CRMAccount.tenant_id == tenant_id,
            CRMAccount.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        account_number = f"ACC-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(CRMAccount).filter(
            CRMAccount.tenant_id == tenant_id,
            CRMAccount.account_number == account_number
        ).first():
            count += 1
            account_number = f"ACC-{today}-{str(count + 1).zfill(4)}"
        
        return account_number
    
    @staticmethod
    def create_account(
        db: Session,
        account_data: CRMAccountCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new CRM account"""
        try:
            account_number = CRMAccountService.generate_account_number(db, tenant_id)
            
            account = CRMAccount(
                tenant_id=tenant_id,
                account_number=account_number,
                **account_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(account)
            db.commit()
            db.refresh(account)
            
            return {
                "success": True,
                "message": "Account created successfully",
                "data": model_to_dict(account)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_CREATE_FAILED",
                    "message": f"Failed to create account: {str(e)}"
                }
            }
    
    @staticmethod
    def get_account(
        db: Session,
        account_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get account by ID"""
        try:
            account = db.query(CRMAccount).filter(
                CRMAccount.id == account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not account:
                return {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_NOT_FOUND",
                        "message": "Account not found"
                    }
                }
            
            return {
                "success": True,
                "data": model_to_dict(account)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_GET_FAILED",
                    "message": f"Failed to get account: {str(e)}"
                }
            }
    
    @staticmethod
    def get_account_360_view(
        db: Session,
        account_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get complete 360 view of an account"""
        try:
            account = db.query(CRMAccount).filter(
                CRMAccount.id == account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not account:
                return {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_NOT_FOUND",
                        "message": "Account not found"
                    }
                }
            
            contacts = db.query(CRMContact).filter(
                CRMContact.account_id == account_id,
                CRMContact.tenant_id == tenant_id,
                CRMContact.is_deleted == False
            ).all()
            
            relationships = db.query(CRMAccountRelationship).filter(
                or_(
                    CRMAccountRelationship.primary_account_id == account_id,
                    CRMAccountRelationship.related_account_id == account_id
                ),
                CRMAccountRelationship.tenant_id == tenant_id,
                CRMAccountRelationship.is_deleted == False
            ).all()
            
            activities = db.query(CRMActivity).filter(
                CRMActivity.account_id == account_id,
                CRMActivity.tenant_id == tenant_id,
                CRMActivity.is_deleted == False
            ).order_by(CRMActivity.activity_date.desc()).limit(10).all()
            
            child_accounts = db.query(CRMAccount).filter(
                CRMAccount.parent_account_id == account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).all()
            
            account_360 = {
                "account": model_to_dict(account),
                "contacts": [model_to_dict(c) for c in contacts],
                "relationships": [model_to_dict(r) for r in relationships],
                "recent_activities": [model_to_dict(a) for a in activities],
                "child_accounts": [model_to_dict(c) for c in child_accounts],
                "metrics": {
                    "total_contacts": len(contacts),
                    "total_relationships": len(relationships),
                    "total_child_accounts": len(child_accounts),
                    "opportunities_count": int(account.total_opportunities or 0),
                    "total_revenue": float(account.total_revenue or 0)
                }
            }
            
            return {
                "success": True,
                "data": account_360
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_360_FAILED",
                    "message": f"Failed to get account 360 view: {str(e)}"
                }
            }
    
    @staticmethod
    def list_accounts(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        status: Optional[str] = None,
        account_type: Optional[str] = None,
        account_owner_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """List accounts with filters and pagination"""
        try:
            query = db.query(CRMAccount).filter(
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        CRMAccount.account_name.ilike(search_filter),
                        CRMAccount.account_number.ilike(search_filter),
                        CRMAccount.email.ilike(search_filter),
                        CRMAccount.phone.ilike(search_filter)
                    )
                )
            
            if status:
                query = query.filter(CRMAccount.status == status)
            
            if account_type:
                query = query.filter(CRMAccount.account_type == account_type)
            
            if account_owner_id:
                query = query.filter(CRMAccount.account_owner_id == account_owner_id)
            
            total = query.count()
            accounts = query.order_by(CRMAccount.created_at.desc()).offset(skip).limit(limit).all()
            
            return {
                "success": True,
                "data": {
                    "accounts": [model_to_dict(a) for a in accounts],
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_LIST_FAILED",
                    "message": f"Failed to list accounts: {str(e)}"
                }
            }
    
    @staticmethod
    def update_account(
        db: Session,
        account_id: UUID,
        account_data: CRMAccountUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update account"""
        try:
            account = db.query(CRMAccount).filter(
                CRMAccount.id == account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not account:
                return {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_NOT_FOUND",
                        "message": "Account not found"
                    }
                }
            
            update_data = account_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(account, field, value)
            
            account.updated_by = user_id
            account.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(account)
            
            return {
                "success": True,
                "message": "Account updated successfully",
                "data": model_to_dict(account)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_UPDATE_FAILED",
                    "message": f"Failed to update account: {str(e)}"
                }
            }
    
    @staticmethod
    def delete_account(
        db: Session,
        account_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Soft delete account"""
        try:
            account = db.query(CRMAccount).filter(
                CRMAccount.id == account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not account:
                return {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_NOT_FOUND",
                        "message": "Account not found"
                    }
                }
            
            account.is_deleted = True
            account.deleted_at = datetime.utcnow()
            account.deleted_by = user_id
            
            db.commit()
            
            return {
                "success": True,
                "message": "Account deleted successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "ACCOUNT_DELETE_FAILED",
                    "message": f"Failed to delete account: {str(e)}"
                }
            }


class CRMContactService:
    """Service for CRM Contact operations"""
    
    @staticmethod
    def generate_contact_number(db: Session, tenant_id: str) -> str:
        """Generate unique contact number"""
        count = db.query(func.count(CRMContact.id)).filter(
            CRMContact.tenant_id == tenant_id,
            CRMContact.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        contact_number = f"CON-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(CRMContact).filter(
            CRMContact.tenant_id == tenant_id,
            CRMContact.contact_number == contact_number
        ).first():
            count += 1
            contact_number = f"CON-{today}-{str(count + 1).zfill(4)}"
        
        return contact_number
    
    @staticmethod
    def create_contact(
        db: Session,
        contact_data: CRMContactCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new contact"""
        try:
            account = db.query(CRMAccount).filter(
                CRMAccount.id == contact_data.account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not account:
                return {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_NOT_FOUND",
                        "message": "Account not found"
                    }
                }
            
            contact_number = CRMContactService.generate_contact_number(db, tenant_id)
            
            full_name = f"{contact_data.first_name}"
            if contact_data.middle_name:
                full_name += f" {contact_data.middle_name}"
            full_name += f" {contact_data.last_name}"
            
            contact = CRMContact(
                tenant_id=tenant_id,
                contact_number=contact_number,
                full_name=full_name,
                **contact_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(contact)
            db.commit()
            db.refresh(contact)
            
            return {
                "success": True,
                "message": "Contact created successfully",
                "data": model_to_dict(contact)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "CONTACT_CREATE_FAILED",
                    "message": f"Failed to create contact: {str(e)}"
                }
            }
    
    @staticmethod
    def get_contact(
        db: Session,
        contact_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get contact by ID"""
        try:
            contact = db.query(CRMContact).filter(
                CRMContact.id == contact_id,
                CRMContact.tenant_id == tenant_id,
                CRMContact.is_deleted == False
            ).first()
            
            if not contact:
                return {
                    "success": False,
                    "error": {
                        "code": "CONTACT_NOT_FOUND",
                        "message": "Contact not found"
                    }
                }
            
            return {
                "success": True,
                "data": model_to_dict(contact)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "CONTACT_GET_FAILED",
                    "message": f"Failed to get contact: {str(e)}"
                }
            }
    
    @staticmethod
    def list_contacts(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        account_id: Optional[UUID] = None,
        status: Optional[str] = None,
        contact_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List contacts with filters and pagination"""
        try:
            query = db.query(CRMContact).filter(
                CRMContact.tenant_id == tenant_id,
                CRMContact.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        CRMContact.full_name.ilike(search_filter),
                        CRMContact.contact_number.ilike(search_filter),
                        CRMContact.email.ilike(search_filter),
                        CRMContact.phone.ilike(search_filter)
                    )
                )
            
            if account_id:
                query = query.filter(CRMContact.account_id == account_id)
            
            if status:
                query = query.filter(CRMContact.status == status)
            
            if contact_type:
                query = query.filter(CRMContact.contact_type == contact_type)
            
            total = query.count()
            contacts = query.order_by(CRMContact.created_at.desc()).offset(skip).limit(limit).all()
            
            return {
                "success": True,
                "data": {
                    "contacts": [model_to_dict(c) for c in contacts],
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "CONTACT_LIST_FAILED",
                    "message": f"Failed to list contacts: {str(e)}"
                }
            }
    
    @staticmethod
    def update_contact(
        db: Session,
        contact_id: UUID,
        contact_data: CRMContactUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update contact"""
        try:
            contact = db.query(CRMContact).filter(
                CRMContact.id == contact_id,
                CRMContact.tenant_id == tenant_id,
                CRMContact.is_deleted == False
            ).first()
            
            if not contact:
                return {
                    "success": False,
                    "error": {
                        "code": "CONTACT_NOT_FOUND",
                        "message": "Contact not found"
                    }
                }
            
            update_data = contact_data.dict(exclude_unset=True)
            
            if any(field in update_data for field in ['first_name', 'middle_name', 'last_name']):
                first_name = update_data.get('first_name', contact.first_name)
                middle_name = update_data.get('middle_name', contact.middle_name)
                last_name = update_data.get('last_name', contact.last_name)
                
                full_name = f"{first_name}"
                if middle_name:
                    full_name += f" {middle_name}"
                full_name += f" {last_name}"
                
                update_data['full_name'] = full_name
            
            for field, value in update_data.items():
                setattr(contact, field, value)
            
            contact.updated_by = user_id
            contact.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(contact)
            
            return {
                "success": True,
                "message": "Contact updated successfully",
                "data": model_to_dict(contact)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "CONTACT_UPDATE_FAILED",
                    "message": f"Failed to update contact: {str(e)}"
                }
            }
    
    @staticmethod
    def delete_contact(
        db: Session,
        contact_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Soft delete contact"""
        try:
            contact = db.query(CRMContact).filter(
                CRMContact.id == contact_id,
                CRMContact.tenant_id == tenant_id,
                CRMContact.is_deleted == False
            ).first()
            
            if not contact:
                return {
                    "success": False,
                    "error": {
                        "code": "CONTACT_NOT_FOUND",
                        "message": "Contact not found"
                    }
                }
            
            contact.is_deleted = True
            contact.deleted_at = datetime.utcnow()
            contact.deleted_by = user_id
            
            db.commit()
            
            return {
                "success": True,
                "message": "Contact deleted successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "CONTACT_DELETE_FAILED",
                    "message": f"Failed to delete contact: {str(e)}"
                }
            }


class CRMRelationshipService:
    """Service for Account Relationship operations"""
    
    @staticmethod
    def create_relationship(
        db: Session,
        relationship_data: CRMAccountRelationshipCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new account relationship"""
        try:
            primary_account = db.query(CRMAccount).filter(
                CRMAccount.id == relationship_data.primary_account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            related_account = db.query(CRMAccount).filter(
                CRMAccount.id == relationship_data.related_account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not primary_account or not related_account:
                return {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_NOT_FOUND",
                        "message": "One or both accounts not found"
                    }
                }
            
            existing = db.query(CRMAccountRelationship).filter(
                CRMAccountRelationship.primary_account_id == relationship_data.primary_account_id,
                CRMAccountRelationship.related_account_id == relationship_data.related_account_id,
                CRMAccountRelationship.relationship_type == relationship_data.relationship_type,
                CRMAccountRelationship.tenant_id == tenant_id,
                CRMAccountRelationship.is_deleted == False
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "error": {
                        "code": "RELATIONSHIP_EXISTS",
                        "message": "Relationship already exists"
                    }
                }
            
            relationship = CRMAccountRelationship(
                tenant_id=tenant_id,
                **relationship_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(relationship)
            db.commit()
            db.refresh(relationship)
            
            return {
                "success": True,
                "message": "Relationship created successfully",
                "data": model_to_dict(relationship)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "RELATIONSHIP_CREATE_FAILED",
                    "message": f"Failed to create relationship: {str(e)}"
                }
            }
    
    @staticmethod
    def list_relationships(
        db: Session,
        tenant_id: str,
        account_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """List relationships"""
        try:
            query = db.query(CRMAccountRelationship).filter(
                CRMAccountRelationship.tenant_id == tenant_id,
                CRMAccountRelationship.is_deleted == False
            )
            
            if account_id:
                query = query.filter(
                    or_(
                        CRMAccountRelationship.primary_account_id == account_id,
                        CRMAccountRelationship.related_account_id == account_id
                    )
                )
            
            total = query.count()
            relationships = query.order_by(CRMAccountRelationship.created_at.desc()).offset(skip).limit(limit).all()
            
            return {
                "success": True,
                "data": {
                    "relationships": [model_to_dict(r) for r in relationships],
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "RELATIONSHIP_LIST_FAILED",
                    "message": f"Failed to list relationships: {str(e)}"
                }
            }
    
    @staticmethod
    def update_relationship(
        db: Session,
        relationship_id: UUID,
        relationship_data: CRMAccountRelationshipUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update relationship"""
        try:
            relationship = db.query(CRMAccountRelationship).filter(
                CRMAccountRelationship.id == relationship_id,
                CRMAccountRelationship.tenant_id == tenant_id,
                CRMAccountRelationship.is_deleted == False
            ).first()
            
            if not relationship:
                return {
                    "success": False,
                    "error": {
                        "code": "RELATIONSHIP_NOT_FOUND",
                        "message": "Relationship not found"
                    }
                }
            
            update_data = relationship_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(relationship, field, value)
            
            relationship.updated_by = user_id
            relationship.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(relationship)
            
            return {
                "success": True,
                "message": "Relationship updated successfully",
                "data": model_to_dict(relationship)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "RELATIONSHIP_UPDATE_FAILED",
                    "message": f"Failed to update relationship: {str(e)}"
                }
            }
    
    @staticmethod
    def delete_relationship(
        db: Session,
        relationship_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Soft delete relationship"""
        try:
            relationship = db.query(CRMAccountRelationship).filter(
                CRMAccountRelationship.id == relationship_id,
                CRMAccountRelationship.tenant_id == tenant_id,
                CRMAccountRelationship.is_deleted == False
            ).first()
            
            if not relationship:
                return {
                    "success": False,
                    "error": {
                        "code": "RELATIONSHIP_NOT_FOUND",
                        "message": "Relationship not found"
                    }
                }
            
            relationship.is_deleted = True
            relationship.deleted_at = datetime.utcnow()
            relationship.deleted_by = user_id
            
            db.commit()
            
            return {
                "success": True,
                "message": "Relationship deleted successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "RELATIONSHIP_DELETE_FAILED",
                    "message": f"Failed to delete relationship: {str(e)}"
                }
            }
