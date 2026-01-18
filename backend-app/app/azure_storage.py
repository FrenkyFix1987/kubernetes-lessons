"""Azure Blob Storage service for file uploads."""
import os
import uuid
from datetime import datetime
from typing import Optional
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv

load_dotenv()

# Azure Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "financial-photos")

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}


class AzureBlobStorageService:
    """Service for handling Azure Blob Storage operations."""
    
    def __init__(self):
        """Initialize Azure Blob Storage client."""
        if not AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = AZURE_STORAGE_CONTAINER_NAME
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Create container if it doesn't exist."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container(public_access='blob')
        except Exception as e:
            raise RuntimeError(f"Failed to ensure container exists: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        # Check content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename or '')[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    async def upload_photo(self, file: UploadFile, item_id: int) -> str:
        """
        Upload photo to Azure Blob Storage.
        
        Args:
            file: The uploaded file
            item_id: The ID of the item this photo belongs to
        
        Returns:
            The URL of the uploaded blob
        """
        # Validate file
        self._validate_file(file)
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
        
        # Generate unique blob name: {item_id}_{timestamp}.{ext}
        file_ext = os.path.splitext(file.filename or '')[1].lower()
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        blob_name = f"{item_id}_{timestamp}{file_ext}"
        
        try:
            # Upload to Azure Blob Storage
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Set content type for proper browser display
            content_settings = ContentSettings(content_type=file.content_type)
            
            blob_client.upload_blob(
                content,
                overwrite=True,
                content_settings=content_settings
            )
            
            # Return the blob URL
            return blob_client.url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to Azure Blob Storage: {str(e)}"
            )
    
    async def delete_photo(self, photo_url: str) -> bool:
        """
        Delete photo from Azure Blob Storage.
        
        Args:
            photo_url: The URL of the photo to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Extract blob name from URL
            blob_name = photo_url.split('/')[-1]
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            return True
            
        except Exception:
            # Log error but don't raise - blob might already be deleted
            return False


# Global instance
_blob_service: Optional[AzureBlobStorageService] = None


def get_blob_service() -> AzureBlobStorageService:
    """Get or create Azure Blob Storage service instance."""
    global _blob_service
    if _blob_service is None:
        _blob_service = AzureBlobStorageService()
    return _blob_service
