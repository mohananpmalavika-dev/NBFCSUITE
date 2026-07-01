from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, ForeignKeyConstraint, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class AssetCategory(Base):
    __tablename__ = "asset_categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "category_code", name="uq_asset_categories_scope"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    category_code = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("tenant_id", "asset_code", name="uq_assets_tenant_asset_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    asset_code = Column(String, index=True, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_category = Column(String, nullable=True, index=True)
    asset_class = Column(String, nullable=True, index=True)
    asset_type = Column(String, nullable=True, index=True)
    serial_number = Column(String, nullable=True)
    qr_code = Column(String, nullable=True)
    barcode = Column(String, nullable=True)
    location = Column(String, nullable=True)
    branch_id = Column(String, nullable=True, index=True)
    department_id = Column(String, nullable=True, index=True)
    custodian = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    acquisition_date = Column(DateTime, nullable=True)
    acquisition_cost = Column(Float, default=0.0)
    book_value = Column(Float, default=0.0)
    accumulated_depreciation = Column(Float, default=0.0)
    net_book_value = Column(Float, default=0.0)
    capitalization_date = Column(DateTime, nullable=True)
    commissioning_date = Column(DateTime, nullable=True)
    disposal_date = Column(DateTime, nullable=True)
    disposal_reason = Column(String, nullable=True)
    status = Column(String, default="draft", index=True)
    lifecycle_stage = Column(String, default="planning", index=True)
    currency = Column(String, default="INR")
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "asset_category"],
            ["asset_categories.tenant_id", "asset_categories.category_code"],
        ),
    )

    category = relationship(
        "AssetCategory",
        primaryjoin="and_(Asset.tenant_id == AssetCategory.tenant_id, Asset.asset_category == AssetCategory.category_code)",
        viewonly=True,
    )
    acquisition_cost = Column(Float, default=0.0)
    book_value = Column(Float, default=0.0)
    accumulated_depreciation = Column(Float, default=0.0)
    net_book_value = Column(Float, default=0.0)
    capitalization_date = Column(DateTime, nullable=True)
    commissioning_date = Column(DateTime, nullable=True)
    disposal_date = Column(DateTime, nullable=True)
    disposal_reason = Column(String, nullable=True)
    status = Column(String, default="draft", index=True)
    lifecycle_stage = Column(String, default="planning", index=True)
    currency = Column(String, default="INR")
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    category = relationship(
        "AssetCategory",
        primaryjoin="and_(Asset.tenant_id == AssetCategory.tenant_id, Asset.asset_category == AssetCategory.category_code)",
        viewonly=True,
    )


class AssetDepreciation(Base):
    __tablename__ = "asset_depreciations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    book_type = Column(String, nullable=False, default="primary")
    depreciation_method = Column(String, nullable=True)
    depreciation_amount = Column(Float, nullable=False)
    accumulated_depreciation = Column(Float, nullable=False)
    period = Column(String, nullable=True)
    status = Column(String, default="posted", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset")


class AssetTransfer(Base):
    __tablename__ = "asset_transfers"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    from_location = Column(String, nullable=True)
    to_location = Column(String, nullable=True)
    from_department_id = Column(String, nullable=True)
    to_department_id = Column(String, nullable=True)
    transfer_date = Column(DateTime, default=datetime.utcnow)
    reason = Column(String, nullable=True)
    status = Column(String, default="completed", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset")


class AssetVerification(Base):
    __tablename__ = "asset_verifications"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    verified_by = Column(String, nullable=True)
    verification_date = Column(DateTime, default=datetime.utcnow)
    remarks = Column(String, nullable=True)
    status = Column(String, default="verified", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset")


class AssetDisposal(Base):
    __tablename__ = "asset_disposals"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, index=True)
    disposal_date = Column(DateTime, default=datetime.utcnow)
    disposal_reason = Column(String, nullable=True)
    disposal_value = Column(Float, nullable=True)
    status = Column(String, default="disposed", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset")
