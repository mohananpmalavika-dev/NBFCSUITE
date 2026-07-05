"""
Master Data Service
Business logic for master data CRUD operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List, Type, TypeVar
from uuid import UUID
import uuid

from backend.shared.database.master_data_models import (
    Country, State, City, Pincode,
    Bank, BankBranch,
    Currency, InterestRateType, LoanProductType,
    DocumentType, Occupation, Industry, LoanPurpose,
    RelationshipType, Holiday, FinancialYear
)
from backend.shared.middleware.error_handler import NotFoundError, ConflictError


T = TypeVar('T')


class MasterDataService:
    """Master data service with generic CRUD operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def get_list(
        self,
        model: Type[T],
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[T], int]:
        """
        Get paginated list of records
        
        Args:
            model: SQLAlchemy model class
            page: Page number (1-indexed)
            page_size: Records per page
            search: Search term (searches in name field)
            is_active: Filter by active status
            
        Returns:
            Tuple of (records, total_count)
        """
        # Build query
        query = select(model).where(
            and_(
                model.tenant_id == self.tenant_id,
                model.is_deleted == False
            )
        )
        
        # Add search filter
        if search and hasattr(model, 'name'):
            query = query.where(
                model.name.ilike(f"%{search}%")
            )
        
        # Add active filter
        if is_active is not None and hasattr(model, 'is_active'):
            query = query.where(model.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Add pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return records, total
    
    async def get_by_id(self, model: Type[T], id: UUID) -> T:
        """
        Get record by ID
        
        Args:
            model: SQLAlchemy model class
            id: Record ID
            
        Returns:
            Record
            
        Raises:
            NotFoundError: Record not found
        """
        result = await self.db.execute(
            select(model).where(
                and_(
                    model.id == id,
                    model.tenant_id == self.tenant_id,
                    model.is_deleted == False
                )
            )
        )
        record = result.scalar_one_or_none()
        
        if not record:
            raise NotFoundError(f"{model.__name__} not found")
        
        return record
    
    async def create(self, model: Type[T], data: dict) -> T:
        """
        Create new record
        
        Args:
            model: SQLAlchemy model class
            data: Record data
            
        Returns:
            Created record
        """
        # Add tenant_id and id
        data['id'] = uuid.uuid4()
        data['tenant_id'] = self.tenant_id
        
        # Create record
        record = model(**data)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        
        return record
    
    async def update(self, model: Type[T], id: UUID, data: dict) -> T:
        """
        Update existing record
        
        Args:
            model: SQLAlchemy model class
            id: Record ID
            data: Updated data
            
        Returns:
            Updated record
            
        Raises:
            NotFoundError: Record not found
        """
        record = await self.get_by_id(model, id)
        
        # Update fields
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        await self.db.commit()
        await self.db.refresh(record)
        
        return record
    
    async def delete(self, model: Type[T], id: UUID) -> bool:
        """
        Soft delete record
        
        Args:
            model: SQLAlchemy model class
            id: Record ID
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: Record not found
        """
        record = await self.get_by_id(model, id)
        record.is_deleted = True
        
        await self.db.commit()
        return True
    
    async def search_by_code(self, model: Type[T], code: str) -> Optional[T]:
        """
        Search record by code
        
        Args:
            model: SQLAlchemy model class
            code: Code to search
            
        Returns:
            Record or None
        """
        if not hasattr(model, 'code'):
            return None
        
        result = await self.db.execute(
            select(model).where(
                and_(
                    model.code == code,
                    model.tenant_id == self.tenant_id,
                    model.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def search_ifsc(self, ifsc_code: str) -> Optional[BankBranch]:
        """
        Search bank branch by IFSC code
        
        Args:
            ifsc_code: IFSC code
            
        Returns:
            Bank branch or None
        """
        result = await self.db.execute(
            select(BankBranch).where(
                and_(
                    BankBranch.ifsc_code == ifsc_code,
                    BankBranch.tenant_id == self.tenant_id,
                    BankBranch.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def search_pincode(self, pincode: str) -> List[Pincode]:
        """
        Search by pincode
        
        Args:
            pincode: Pincode to search
            
        Returns:
            List of matching pincodes
        """
        result = await self.db.execute(
            select(Pincode).where(
                and_(
                    Pincode.pincode == pincode,
                    Pincode.tenant_id == self.tenant_id,
                    Pincode.is_deleted == False
                )
            )
        )
        return result.scalars().all()
    
    async def get_stats(self) -> dict:
        """
        Get master data statistics
        
        Returns:
            Dictionary with counts of each master data type
        """
        stats = {}
        
        models = [
            ('countries', Country),
            ('states', State),
            ('cities', City),
            ('pincodes', Pincode),
            ('banks', Bank),
            ('bank_branches', BankBranch),
            ('currencies', Currency),
            ('document_types', DocumentType),
            ('occupations', Occupation),
            ('industries', Industry),
        ]
        
        for name, model in models:
            result = await self.db.execute(
                select(func.count()).select_from(model).where(
                    and_(
                        model.tenant_id == self.tenant_id,
                        model.is_deleted == False
                    )
                )
            )
            stats[name] = result.scalar()
        
        return stats
