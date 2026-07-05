"""
File Upload Schemas
Pydantic models for file upload operations
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class FileUploadResponse(BaseModel):
    """Response model for uploaded file"""
    id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    """Metadata for file upload"""
    document_type: str = Field(..., description="Type of document")
    document_number: Optional[str] = Field(None, description="Document reference number")
    entity_type: Optional[str] = Field(None, description="Entity type (customer, loan, etc.)")
    entity_id: Optional[str] = Field(None, description="Entity ID")
    remarks: Optional[str] = Field(None, description="Additional notes")

    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = [
            'PAN Card', 'Aadhaar Card', 'Passport', 'Driving License', 'Voter ID',
            'Bank Statement', 'Salary Slip', 'ITR', 'Form 16',
            'Business Registration', 'GST Certificate', 'Financial Statements',
            'Property Documents', 'Valuation Report', 'Photograph', 'Other'
        ]
        if v not in allowed_types:
            raise ValueError(f'Document type must be one of: {", ".join(allowed_types)}')
        return v


class FileDeletionResponse(BaseModel):
    """Response model for file deletion"""
    success: bool
    message: str


class FileListResponse(BaseModel):
    """Response model for file listing"""
    files: List[FileUploadResponse]
    total: int
