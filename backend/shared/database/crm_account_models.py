"""
CRM Account Management Models
Includes Account, Contact, and Relationship models
"""

from sqlalchemy import Column, String, Text, Numeric, Date, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.models import BaseModel


class AccountType(str, enum.Enum):
    """Account type enumeration"""
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    PARTNER = "partner"
    VENDOR = "vendor"
    COMPETITOR = "competitor"
    OTHER = "other"


class AccountStatus(str, enum.Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    DORMANT = "dormant"
    CLOSED = "closed"


class IndustryType(str, enum.Enum):
    """Industry type enumeration"""
    AGRICULTURE = "agriculture"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    HOSPITALITY = "hospitality"
    TRANSPORTATION = "transportation"
    CONSTRUCTION = "construction"
    PROFESSIONAL_SERVICES = "professional_services"
    OTHER = "other"


class ContactType(str, enum.Enum):
    """Contact type enumeration"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BILLING = "billing"
    TECHNICAL = "technical"
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    OTHER = "other"


class ContactStatus(str, enum.Enum):
    """Contact status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DO_NOT_CONTACT = "do_not_contact"


class RelationshipType(str, enum.Enum):
    """Relationship type enumeration"""
    PARENT_CHILD = "parent_child"
    SUBSIDIARY = "subsidiary"
    PARTNER = "partner"
    COMPETITOR = "competitor"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    REFERRAL = "referral"
    OTHER = "other"


class CRMAccount(BaseModel):
    """
    CRM Account Model
    Represents a business account or organization
    """
    __tablename__ = "crm_accounts"
    
    # Basic Information
    account_number = Column(String(50), nullable=False, index=True)
    account_name = Column(String(200), nullable=False, index=True)
    account_type = Column(SQLEnum(AccountType), nullable=False, default=AccountType.BUSINESS)
    status = Column(SQLEnum(AccountStatus), nullable=False, default=AccountStatus.PROSPECT, index=True)
    
    # Business Details
    industry = Column(SQLEnum(IndustryType), nullable=True)
    annual_revenue = Column(Numeric(15, 2), nullable=True)
    employee_count = Column(String(50), nullable=True)  # e.g., "50-100", "500+"
    
    # Tax & Registration
    pan_number = Column(String(20), nullable=True)
    gst_number = Column(String(20), nullable=True)
    cin_number = Column(String(30), nullable=True)
    registration_number = Column(String(50), nullable=True)
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Address
    billing_address_line1 = Column(String(200), nullable=True)
    billing_address_line2 = Column(String(200), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_pincode = Column(String(10), nullable=True)
    billing_country = Column(String(100), default="India")
    
    shipping_address_line1 = Column(String(200), nullable=True)
    shipping_address_line2 = Column(String(200), nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_state = Column(String(100), nullable=True)
    shipping_pincode = Column(String(10), nullable=True)
    shipping_country = Column(String(100), default="India")
    same_as_billing = Column(String(10), default="no")  # yes/no
    
    # Relationship Management
    parent_account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=True, index=True)
    account_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # User who manages this account
    
    # Business Metrics
    customer_since = Column(Date, nullable=True)
    last_activity_date = Column(Date, nullable=True)
    next_followup_date = Column(Date, nullable=True)
    total_opportunities = Column(Numeric(15, 2), default=0)
    total_revenue = Column(Numeric(15, 2), default=0)
    
    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Social Media
    linkedin_url = Column(String(200), nullable=True)
    facebook_url = Column(String(200), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    
    # Rating & Classification
    rating = Column(String(20), nullable=True)  # Hot, Warm, Cold
    priority = Column(String(20), nullable=True)  # High, Medium, Low
    
    # Relationships
    contacts = relationship("CRMContact", back_populates="account", foreign_keys="CRMContact.account_id")
    child_accounts = relationship("CRMAccount", backref="parent_account", remote_side="CRMAccount.id")
    
    # Unique constraint: account_number per tenant
    __table_args__ = (
        Index('idx_tenant_account_number', 'tenant_id', 'account_number', unique=True),
        Index('idx_account_name', 'tenant_id', 'account_name'),
        Index('idx_account_owner', 'tenant_id', 'account_owner_id'),
        Index('idx_account_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<CRMAccount(id={self.id}, account_number={self.account_number}, account_name={self.account_name})>"


class CRMContact(BaseModel):
    """
    CRM Contact Model
    Represents an individual contact associated with an account
    """
    __tablename__ = "crm_contacts"
    
    # Account Relationship
    account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=False, index=True)
    
    # Basic Information
    contact_number = Column(String(50), nullable=False, index=True)
    salutation = Column(String(10), nullable=True)  # Mr, Ms, Dr, etc.
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(300), nullable=False, index=True)
    
    # Contact Type & Status
    contact_type = Column(SQLEnum(ContactType), nullable=False, default=ContactType.PRIMARY)
    status = Column(SQLEnum(ContactStatus), nullable=False, default=ContactStatus.ACTIVE, index=True)
    
    # Job Information
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)  # Decision Maker, Influencer, User
    
    # Contact Information
    email = Column(String(100), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    fax = Column(String(20), nullable=True)
    
    # Address (if different from account)
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Personal Details
    date_of_birth = Column(Date, nullable=True)
    anniversary_date = Column(Date, nullable=True)
    
    # Preferences
    preferred_contact_method = Column(String(20), nullable=True)  # email, phone, mobile
    best_time_to_call = Column(String(50), nullable=True)
    email_opt_out = Column(String(10), default="no")
    
    # Relationship Management
    reports_to_contact_id = Column(UUID(as_uuid=True), ForeignKey('crm_contacts.id'), nullable=True)
    contact_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # User who manages this contact
    
    # Activity Tracking
    last_contacted_date = Column(Date, nullable=True)
    next_followup_date = Column(Date, nullable=True)
    
    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    
    # Social Media
    linkedin_url = Column(String(200), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    
    # Relationships
    account = relationship("CRMAccount", back_populates="contacts", foreign_keys=[account_id])
    subordinates = relationship("CRMContact", backref="reports_to", remote_side="CRMContact.id")
    
    # Unique constraint: contact_number per tenant
    __table_args__ = (
        Index('idx_tenant_contact_number', 'tenant_id', 'contact_number', unique=True),
        Index('idx_contact_account', 'tenant_id', 'account_id'),
        Index('idx_contact_name', 'tenant_id', 'full_name'),
        Index('idx_contact_email', 'tenant_id', 'email'),
    )
    
    def __repr__(self):
        return f"<CRMContact(id={self.id}, contact_number={self.contact_number}, full_name={self.full_name})>"


class CRMAccountRelationship(BaseModel):
    """
    CRM Account Relationship Model
    Tracks relationships between accounts
    """
    __tablename__ = "crm_account_relationships"
    
    # Account Relationships
    primary_account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=False, index=True)
    related_account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=False, index=True)
    
    # Relationship Details
    relationship_type = Column(SQLEnum(RelationshipType), nullable=False, default=RelationshipType.OTHER)
    relationship_description = Column(String(200), nullable=True)
    
    # Relationship Strength
    strength = Column(String(20), nullable=True)  # Strong, Medium, Weak
    is_active = Column(String(10), default="yes")
    
    # Dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    
    # Unique constraint: prevent duplicate relationships
    __table_args__ = (
        Index('idx_tenant_account_relationship', 'tenant_id', 'primary_account_id', 'related_account_id', 
              'relationship_type', unique=True),
        Index('idx_primary_account', 'tenant_id', 'primary_account_id'),
        Index('idx_related_account', 'tenant_id', 'related_account_id'),
    )
    
    def __repr__(self):
        return f"<CRMAccountRelationship(id={self.id}, type={self.relationship_type})>"


class CRMActivity(BaseModel):
    """
    CRM Activity Model
    Tracks all activities related to accounts and contacts
    """
    __tablename__ = "crm_activities"
    
    # Activity Type
    activity_type = Column(String(50), nullable=False, index=True)  # call, meeting, email, task, note
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Related Entities
    account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey('crm_contacts.id'), nullable=True, index=True)
    
    # Activity Details
    activity_date = Column(Date, nullable=False, index=True)
    duration_minutes = Column(String(10), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="planned")  # planned, completed, cancelled
    priority = Column(String(20), nullable=True)  # high, medium, low
    
    # Outcome
    outcome = Column(String(50), nullable=True)
    follow_up_required = Column(String(10), default="no")
    follow_up_date = Column(Date, nullable=True)
    
    # Owner
    activity_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    attachments = Column(String(500), nullable=True)  # Comma-separated file IDs
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_account', 'tenant_id', 'account_id'),
        Index('idx_activity_contact', 'tenant_id', 'contact_id'),
        Index('idx_activity_date', 'tenant_id', 'activity_date'),
        Index('idx_activity_type', 'tenant_id', 'activity_type'),
    )
    
    def __repr__(self):
        return f"<CRMActivity(id={self.id}, type={self.activity_type}, subject={self.subject})>"
