"""
Legal Contract Management - Service Layer
Business logic for contract lifecycle management, renewals, and version control
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import hashlib

from backend.shared.database.legal_models import (
    Contract,
    ContractVersion,
    ContractRenewal,
    ContractDocument,
    ContractParty,
    ContractTemplate,
    ContractType,
    ContractStatus,
    RenewalStatus,
)
from .schemas import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractVersionCreate,
    ContractRenewalCreate,
    ContractRenewalUpdate,
    ContractDocumentCreate,
    ContractPartyCreate,
    ContractPartyUpdate,
    ContractFilterParams,
    ContractStatistics,
)


class ContractService:
    """Service class for contract management operations"""

    @staticmethod
    async def generate_contract_number(
        db: AsyncSession,
        tenant_id: str,
        contract_type: ContractType
    ) -> str:
        """Generate unique contract number"""
        # Format: CT-VENDOR-2024-0001
        prefix = f"CT-{contract_type.value.upper()}"
        year = datetime.utcnow().year
        
        # Get count of contracts for this type and year
        result = await db.execute(
            select(func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.contract_type == contract_type,
                    func.extract('year', Contract.created_at) == year,
                    Contract.is_deleted == False
                )
            )
        )
        count = result.scalar() or 0
        
        return f"{prefix}-{year}-{str(count + 1).zfill(4)}"

    @staticmethod
    def calculate_hash(content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    async def create_contract(
        db: AsyncSession,
        contract_data: ContractCreate,
        tenant_id: str,
        user_id: uuid.UUID
    ) -> Contract:
        """Create a new contract"""
        # Generate contract number
        contract_number = await ContractService.generate_contract_number(
            db, tenant_id, contract_data.contract_type
        )
        
        # Create contract
        contract = Contract(
            tenant_id=tenant_id,
            contract_number=contract_number,
            title=contract_data.title,
            contract_type=contract_data.contract_type,
            description=contract_data.description,
            status=ContractStatus.DRAFT,
            effective_date=contract_data.effective_date,
            expiry_date=contract_data.expiry_date,
            execution_date=contract_data.execution_date,
            contract_value=contract_data.contract_value,
            currency=contract_data.currency,
            is_renewable=contract_data.is_renewable,
            auto_renewal=contract_data.auto_renewal,
            renewal_notice_days=contract_data.renewal_notice_days,
            renewal_status=RenewalStatus.NOT_REQUIRED if not contract_data.is_renewable else RenewalStatus.PENDING,
            document_url=contract_data.document_url,
            tags=contract_data.tags,
            custom_fields=contract_data.custom_fields,
            alert_before_expiry_days=contract_data.alert_before_expiry_days,
            notes=contract_data.notes,
            created_by=user_id,
            current_version=1,
            is_latest=True,
        )
        
        # Calculate document hash if URL provided
        if contract_data.document_url:
            contract.document_hash = ContractService.calculate_hash(contract_data.document_url)
        
        db.add(contract)
        await db.flush()
        
        # Create initial version
        version = ContractVersion(
            contract_id=contract.id,
            version_number=1,
            version_name="Initial Version",
            title=contract_data.title,
            description=contract_data.description,
            contract_value=contract_data.contract_value,
            effective_date=contract_data.effective_date,
            expiry_date=contract_data.expiry_date,
            document_url=contract_data.document_url or "",
            document_hash=contract.document_hash,
            changes_summary="Initial contract creation",
            created_by=user_id,
        )
        db.add(version)
        
        await db.commit()
        await db.refresh(contract)
        
        return contract

    @staticmethod
    async def get_contract(
        db: AsyncSession,
        contract_id: uuid.UUID,
        tenant_id: str
    ) -> Optional[Contract]:
        """Get contract by ID with all relationships"""
        result = await db.execute(
            select(Contract)
            .options(
                selectinload(Contract.versions),
                selectinload(Contract.renewals),
                selectinload(Contract.documents),
                selectinload(Contract.parties),
            )
            .where(
                and_(
                    Contract.id == contract_id,
                    Contract.tenant_id == tenant_id,
                    Contract.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_contract(
        db: AsyncSession,
        contract_id: uuid.UUID,
        tenant_id: str,
        contract_data: ContractUpdate,
        user_id: uuid.UUID
    ) -> Optional[Contract]:
        """Update contract"""
        contract = await ContractService.get_contract(db, contract_id, tenant_id)
        if not contract:
            return None
        
        # Track if major fields changed (requiring new version)
        major_change = False
        changes = []
        
        update_data = contract_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and getattr(contract, field, None) != value:
                if field in ['title', 'contract_value', 'effective_date', 'expiry_date', 'document_url']:
                    major_change = True
                    changes.append(f"{field} updated")
                setattr(contract, field, value)
        
        # Create new version if major change
        if major_change:
            contract.current_version += 1
            version = ContractVersion(
                contract_id=contract.id,
                version_number=contract.current_version,
                version_name=f"Version {contract.current_version}",
                title=contract.title,
                description=contract.description,
                contract_value=contract.contract_value,
                effective_date=contract.effective_date,
                expiry_date=contract.expiry_date,
                document_url=contract.document_url or "",
                document_hash=ContractService.calculate_hash(contract.document_url or ""),
                changes_summary=", ".join(changes),
                change_reason="Contract updated",
                created_by=user_id,
            )
            db.add(version)
        
        await db.commit()
        await db.refresh(contract)
        
        return contract

    @staticmethod
    async def delete_contract(
        db: AsyncSession,
        contract_id: uuid.UUID,
        tenant_id: str,
        user_id: uuid.UUID
    ) -> bool:
        """Soft delete contract"""
        contract = await ContractService.get_contract(db, contract_id, tenant_id)
        if not contract:
            return False
        
        contract.is_deleted = True
        contract.deleted_at = datetime.utcnow()
        contract.deleted_by = user_id
        
        await db.commit()
        return True

    @staticmethod
    async def list_contracts(
        db: AsyncSession,
        tenant_id: str,
        filters: ContractFilterParams
    ) -> Tuple[List[Contract], int]:
        """List contracts with filters and pagination"""
        query = select(Contract).where(
            and_(
                Contract.tenant_id == tenant_id,
                Contract.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.contract_type:
            query = query.where(Contract.contract_type == filters.contract_type)
        
        if filters.status:
            query = query.where(Contract.status == filters.status)
        
        if filters.renewal_status:
            query = query.where(Contract.renewal_status == filters.renewal_status)
        
        if filters.is_renewable is not None:
            query = query.where(Contract.is_renewable == filters.is_renewable)
        
        if filters.expiring_in_days:
            future_date = date.today() + timedelta(days=filters.expiring_in_days)
            query = query.where(
                and_(
                    Contract.expiry_date.isnot(None),
                    Contract.expiry_date <= future_date,
                    Contract.expiry_date >= date.today()
                )
            )
        
        if filters.effective_date_from:
            query = query.where(Contract.effective_date >= filters.effective_date_from)
        
        if filters.effective_date_to:
            query = query.where(Contract.effective_date <= filters.effective_date_to)
        
        if filters.expiry_date_from:
            query = query.where(Contract.expiry_date >= filters.expiry_date_from)
        
        if filters.expiry_date_to:
            query = query.where(Contract.expiry_date <= filters.expiry_date_to)
        
        if filters.min_value:
            query = query.where(Contract.contract_value >= filters.min_value)
        
        if filters.max_value:
            query = query.where(Contract.contract_value <= filters.max_value)
        
        if filters.tags:
            query = query.where(Contract.tags.contains(filters.tags))
        
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.where(
                or_(
                    Contract.contract_number.ilike(search),
                    Contract.title.ilike(search),
                    Contract.description.ilike(search)
                )
            )
        
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0
        
        # Apply sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(getattr(Contract, filters.sort_by)))
        else:
            query = query.order_by(desc(getattr(Contract, filters.sort_by)))
        
        # Apply pagination
        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)
        
        # Load relationships
        query = query.options(
            selectinload(Contract.parties),
            selectinload(Contract.documents),
            selectinload(Contract.versions),
            selectinload(Contract.renewals),
        )
        
        result = await db.execute(query)
        contracts = result.scalars().all()
        
        return list(contracts), total

    @staticmethod
    async def add_contract_party(
        db: AsyncSession,
        contract_id: uuid.UUID,
        tenant_id: str,
        party_data: ContractPartyCreate
    ) -> Optional[ContractParty]:
        """Add party to contract"""
        contract = await ContractService.get_contract(db, contract_id, tenant_id)
        if not contract:
            return None
        
        party = ContractParty(
            contract_id=contract_id,
            **party_data.dict()
        )
        
        db.add(party)
        await db.commit()
        await db.refresh(party)
        
        return party

    @staticmethod
    async def add_contract_document(
        db: AsyncSession,
        contract_id: uuid.UUID,
        tenant_id: str,
        document_data: ContractDocumentCreate,
        user_id: uuid.UUID
    ) -> Optional[ContractDocument]:
        """Add document to contract"""
        contract = await ContractService.get_contract(db, contract_id, tenant_id)
        if not contract:
            return None
        
        document = ContractDocument(
            contract_id=contract_id,
            uploaded_by=user_id,
            **document_data.dict()
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        return document

    @staticmethod
    async def create_renewal(
        db: AsyncSession,
        contract_id: uuid.UUID,
        tenant_id: str,
        renewal_data: ContractRenewalCreate,
        user_id: uuid.UUID
    ) -> Optional[ContractRenewal]:
        """Create contract renewal"""
        contract = await ContractService.get_contract(db, contract_id, tenant_id)
        if not contract:
            return None
        
        # Get renewal number
        result = await db.execute(
            select(func.count(ContractRenewal.id))
            .where(ContractRenewal.contract_id == contract_id)
        )
        renewal_number = (result.scalar() or 0) + 1
        
        renewal = ContractRenewal(
            contract_id=contract_id,
            renewal_number=renewal_number,
            renewal_status=RenewalStatus.PENDING,
            requested_by=user_id,
            **renewal_data.dict()
        )
        
        db.add(renewal)
        
        # Update contract renewal status
        contract.renewal_status = RenewalStatus.IN_PROGRESS
        
        await db.commit()
        await db.refresh(renewal)
        
        return renewal

    @staticmethod
    async def update_renewal(
        db: AsyncSession,
        renewal_id: uuid.UUID,
        tenant_id: str,
        renewal_data: ContractRenewalUpdate,
        user_id: uuid.UUID
    ) -> Optional[ContractRenewal]:
        """Update contract renewal"""
        result = await db.execute(
            select(ContractRenewal)
            .join(Contract)
            .where(
                and_(
                    ContractRenewal.id == renewal_id,
                    Contract.tenant_id == tenant_id
                )
            )
        )
        renewal = result.scalar_one_or_none()
        if not renewal:
            return None
        
        update_data = renewal_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(renewal, field, value)
        
        # If renewal completed, update contract
        if renewal.renewal_status == RenewalStatus.COMPLETED:
            contract = await db.get(Contract, renewal.contract_id)
            if contract and renewal.new_expiry_date:
                contract.expiry_date = renewal.new_expiry_date
                contract.renewal_status = RenewalStatus.COMPLETED
            if renewal.new_contract_value:
                contract.contract_value = renewal.new_contract_value
            renewal.approved_by = user_id
            renewal.approval_date = datetime.utcnow()
        
        await db.commit()
        await db.refresh(renewal)
        
        return renewal

    @staticmethod
    async def get_contract_statistics(
        db: AsyncSession,
        tenant_id: str
    ) -> ContractStatistics:
        """Get contract statistics"""
        # Total contracts
        total_result = await db.execute(
            select(func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.is_deleted == False
                )
            )
        )
        total_contracts = total_result.scalar() or 0
        
        # Active contracts
        active_result = await db.execute(
            select(func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.status == ContractStatus.ACTIVE,
                    Contract.is_deleted == False
                )
            )
        )
        active_contracts = active_result.scalar() or 0
        
        # Expired contracts
        expired_result = await db.execute(
            select(func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.status == ContractStatus.EXPIRED,
                    Contract.is_deleted == False
                )
            )
        )
        expired_contracts = expired_result.scalar() or 0
        
        # Expiring soon (within 30 days)
        future_date = date.today() + timedelta(days=30)
        expiring_result = await db.execute(
            select(func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.expiry_date.isnot(None),
                    Contract.expiry_date <= future_date,
                    Contract.expiry_date >= date.today(),
                    Contract.is_deleted == False
                )
            )
        )
        expiring_soon = expiring_result.scalar() or 0
        
        # Pending renewals
        renewal_result = await db.execute(
            select(func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.renewal_status == RenewalStatus.PENDING,
                    Contract.is_deleted == False
                )
            )
        )
        pending_renewals = renewal_result.scalar() or 0
        
        # Total contract value
        value_result = await db.execute(
            select(func.sum(Contract.contract_value))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.is_deleted == False
                )
            )
        )
        total_value = value_result.scalar() or Decimal(0)
        
        # Contracts by type
        type_result = await db.execute(
            select(Contract.contract_type, func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.is_deleted == False
                )
            )
            .group_by(Contract.contract_type)
        )
        contracts_by_type = {str(row[0]): row[1] for row in type_result.all()}
        
        # Contracts by status
        status_result = await db.execute(
            select(Contract.status, func.count(Contract.id))
            .where(
                and_(
                    Contract.tenant_id == tenant_id,
                    Contract.is_deleted == False
                )
            )
            .group_by(Contract.status)
        )
        contracts_by_status = {str(row[0]): row[1] for row in status_result.all()}
        
        return ContractStatistics(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expired_contracts=expired_contracts,
            expiring_soon=expiring_soon,
            pending_renewals=pending_renewals,
            total_contract_value=total_value,
            contracts_by_type=contracts_by_type,
            contracts_by_status=contracts_by_status,
            average_contract_value=total_value / total_contracts if total_contracts > 0 else Decimal(0),
            renewal_completion_rate=0.0,  # TODO: Calculate from renewal history
        )
