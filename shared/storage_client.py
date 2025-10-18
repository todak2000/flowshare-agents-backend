"""
Firebase Storage client for file uploads
"""
import firebase_admin
from firebase_admin import storage
from datetime import timedelta
import os
from typing import Optional
from .config import config
from .logger import logger


class StorageClient:
    """Firebase Storage client for managing file uploads"""

    def __init__(self):
        """Initialize Storage client"""
        # Ensure Firebase is initialized
        if not firebase_admin._apps:
            raise RuntimeError("Firebase must be initialized before using StorageClient")

        # Get storage bucket
        self.bucket = storage.bucket(config.PROJECT_ID + ".appspot.com")
        logger.info("Storage client initialized", bucket=self.bucket.name)

    def upload_file(
        self,
        local_path: str,
        storage_path: str,
        content_type: Optional[str] = None,
        public: bool = False
    ) -> str:
        """
        Upload a file to Firebase Storage

        Args:
            local_path: Path to local file
            storage_path: Destination path in storage bucket
            content_type: MIME type of the file
            public: Whether to make the file publicly accessible

        Returns:
            Public URL or signed URL to the uploaded file
        """
        try:
            # Check if file exists
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"File not found: {local_path}")

            # Create blob
            blob = self.bucket.blob(storage_path)

            # Set content type if provided
            if content_type:
                blob.content_type = content_type

            # Upload file
            blob.upload_from_filename(local_path)

            logger.info(
                "File uploaded to storage",
                local_path=local_path,
                storage_path=storage_path,
                content_type=content_type
            )

            # Return appropriate URL
            if public:
                blob.make_public()
                return blob.public_url
            else:
                # Generate signed URL (valid for 7 days)
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(days=7),
                    method="GET"
                )
                return url

        except Exception as e:
            logger.error(
                "Failed to upload file",
                local_path=local_path,
                storage_path=storage_path,
                error=str(e)
            )
            raise

    def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from Firebase Storage

        Args:
            storage_path: Path to file in storage bucket

        Returns:
            True if deleted successfully
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()

            logger.info("File deleted from storage", storage_path=storage_path)
            return True

        except Exception as e:
            logger.error(
                "Failed to delete file",
                storage_path=storage_path,
                error=str(e)
            )
            return False

    def file_exists(self, storage_path: str) -> bool:
        """
        Check if a file exists in storage

        Args:
            storage_path: Path to file in storage bucket

        Returns:
            True if file exists
        """
        blob = self.bucket.blob(storage_path)
        return blob.exists()


# Singleton instance
storage_client = StorageClient()
