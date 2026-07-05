"""
File Upload Service
Business logic for file upload operations
"""

import os
import uuid
import mimetypes
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.shared.database.models import FileUpload as FileUploadModel


class FileUploadService:
    """Service for handling file uploads"""

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        '.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', 
        '.xls', '.xlsx', '.txt', '.csv'
    }

    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
        'text/csv'
    }

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        db: AsyncSession,
        user_id: str,
        tenant_id: str,
        upload_dir: str = "uploads"
    ):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File extension {file_ext} not allowed"

        # Check MIME type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            return False, f"File type {file.content_type} not allowed"

        # Check file size (if available)
        if hasattr(file, 'size') and file.size:
            if file.size > self.MAX_FILE_SIZE:
                return False, f"File size exceeds maximum limit of {self.MAX_FILE_SIZE / (1024 * 1024)} MB"

        return True, None

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename with UUID"""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{file_ext}"

    def get_file_path(self, filename: str) -> Path:
        """Get full file path for storing file"""
        # Organize files by tenant and date
        date_folder = datetime.now().strftime("%Y/%m/%d")
        folder_path = self.upload_dir / self.tenant_id / date_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path / filename

    async def upload_file(
        self,
        file: UploadFile,
        document_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        document_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> FileUploadModel:
        """
        Upload file and save metadata to database
        
        Args:
            file: Uploaded file
            document_type: Type of document
            entity_type: Entity type (customer, loan, etc.)
            entity_id: Entity ID
            document_number: Document reference number
            remarks: Additional notes
            
        Returns:
            FileUploadModel: Created file record
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename)
        file_path = self.get_file_path(unique_filename)

        # Read and save file
        try:
            content = await file.read()
            
            # Check actual file size
            if len(content) > self.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE / (1024 * 1024)} MB"
                )

            # Save file to disk
            with open(file_path, 'wb') as f:
                f.write(content)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )

        # Create database record
        file_record = FileUploadModel(
            id=str(uuid.uuid4()),
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type or 'application/octet-stream',
            document_type=document_type,
            document_number=document_number,
            entity_type=entity_type,
            entity_id=entity_id,
            uploaded_by=self.user_id,
            uploaded_at=datetime.utcnow(),
            remarks=remarks,
            tenant_id=self.tenant_id,
            is_active=True
        )

        self.db.add(file_record)
        await self.db.commit()
        await self.db.refresh(file_record)

        return file_record

    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        document_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        document_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> List[FileUploadModel]:
        """
        Upload multiple files
        
        Args:
            files: List of uploaded files
            document_type: Type of document
            entity_type: Entity type
            entity_id: Entity ID
            document_number: Document reference number
            remarks: Additional notes
            
        Returns:
            List[FileUploadModel]: List of created file records
        """
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per upload"
            )

        uploaded_files = []
        for file in files:
            uploaded_file = await self.upload_file(
                file=file,
                document_type=document_type,
                entity_type=entity_type,
                entity_id=entity_id,
                document_number=document_number,
                remarks=remarks
            )
            uploaded_files.append(uploaded_file)

        return uploaded_files

    async def get_file(self, file_id: str) -> Optional[FileUploadModel]:
        """Get file by ID"""
        query = select(FileUploadModel).where(
            and_(
                FileUploadModel.id == file_id,
                FileUploadModel.tenant_id == self.tenant_id,
                FileUploadModel.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_files_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[FileUploadModel], int]:
        """Get files by entity type and ID"""
        query = select(FileUploadModel).where(
            and_(
                FileUploadModel.entity_type == entity_type,
                FileUploadModel.entity_id == entity_id,
                FileUploadModel.tenant_id == self.tenant_id,
                FileUploadModel.is_active == True
            )
        ).order_by(FileUploadModel.uploaded_at.desc())

        # Count total
        count_query = select(FileUploadModel).where(
            and_(
                FileUploadModel.entity_type == entity_type,
                FileUploadModel.entity_id == entity_id,
                FileUploadModel.tenant_id == self.tenant_id,
                FileUploadModel.is_active == True
            )
        )
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Get paginated results
        result = await self.db.execute(query.offset(skip).limit(limit))
        files = result.scalars().all()

        return files, total

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete file (soft delete)
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if deleted successfully
        """
        file_record = await self.get_file(file_id)
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Soft delete in database
        file_record.is_active = False
        await self.db.commit()

        # Optionally delete physical file (commented out for safety)
        # try:
        #     if os.path.exists(file_record.file_path):
        #         os.remove(file_record.file_path)
        # except Exception as e:
        #     print(f"Error deleting physical file: {e}")

        return True

    async def get_file_content(self, file_id: str) -> Tuple[bytes, str, str]:
        """
        Get file content for download
        
        Returns:
            Tuple[bytes, str, str]: (content, mime_type, filename)
        """
        file_record = await self.get_file(file_id)
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Read file from disk
        try:
            with open(file_record.file_path, 'rb') as f:
                content = f.read()
            
            return content, file_record.mime_type, file_record.original_filename
        
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical file not found on server"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file: {str(e)}"
            )
