"""
Storage Service - File storage for generated images (S3/R2/Local).
"""

import io
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


class StorageResult:
    """Result of a storage operation."""

    def __init__(
        self,
        success: bool,
        url: str | None = None,
        thumbnail_url: str | None = None,
        key: str | None = None,
        error_message: str | None = None,
    ):
        self.success = success
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.key = key
        self.error_message = error_message


class BaseStorageProvider(ABC):
    """Abstract base class for storage providers."""

    @abstractmethod
    async def upload_image(
        self,
        image_data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        create_thumbnail: bool = True,
    ) -> StorageResult:
        """Upload an image and optionally create a thumbnail."""
        pass

    @abstractmethod
    async def delete_image(self, key: str) -> bool:
        """Delete an image by key."""
        pass

    @abstractmethod
    async def download_from_url(self, url: str) -> bytes | None:
        """Download image data from a URL."""
        pass


class LocalStorageProvider(BaseStorageProvider):
    """Local filesystem storage provider (for development)."""

    def __init__(self):
        self.storage_path = Path(settings.local_storage_path)
        self.base_url = settings.local_storage_url

        # Create directories
        (self.storage_path / "images").mkdir(parents=True, exist_ok=True)
        (self.storage_path / "thumbnails").mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, extension: str = "png") -> str:
        """Generate a unique filename."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:12]
        return f"{timestamp}_{unique_id}.{extension}"

    def _create_thumbnail(self, image_data: bytes, max_size: tuple = (256, 256)) -> bytes:
        """Create a thumbnail from image data."""
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    async def upload_image(
        self,
        image_data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        create_thumbnail: bool = True,
    ) -> StorageResult:
        """Upload image to local storage."""
        try:
            filename = filename or self._generate_filename()

            # Save main image
            image_path = self.storage_path / "images" / filename
            with open(image_path, "wb") as f:
                f.write(image_data)

            image_url = f"{self.base_url}/images/{filename}"
            thumbnail_url = None

            # Create and save thumbnail
            if create_thumbnail:
                try:
                    thumbnail_data = self._create_thumbnail(image_data)
                    thumbnail_path = self.storage_path / "thumbnails" / filename
                    with open(thumbnail_path, "wb") as f:
                        f.write(thumbnail_data)
                    thumbnail_url = f"{self.base_url}/thumbnails/{filename}"
                except Exception as e:
                    logger.warning(f"Failed to create thumbnail: {e}")

            return StorageResult(
                success=True,
                url=image_url,
                thumbnail_url=thumbnail_url,
                key=filename,
            )

        except Exception as e:
            logger.exception(f"Local storage error: {e}")
            return StorageResult(
                success=False,
                error_message=f"Failed to save image: {str(e)}",
            )

    async def delete_image(self, key: str) -> bool:
        """Delete image from local storage."""
        try:
            image_path = self.storage_path / "images" / key
            thumbnail_path = self.storage_path / "thumbnails" / key

            if image_path.exists():
                image_path.unlink()
            if thumbnail_path.exists():
                thumbnail_path.unlink()

            return True
        except Exception as e:
            logger.error(f"Failed to delete image {key}: {e}")
            return False

    async def download_from_url(self, url: str) -> bytes | None:
        """Download image from URL."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    return response.content
                return None
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None


class S3StorageProvider(BaseStorageProvider):
    """AWS S3 / Cloudflare R2 storage provider."""

    def __init__(self):
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.s3_region
        self.public_url = settings.s3_public_url

        # Create S3 client
        client_kwargs = {
            "aws_access_key_id": settings.s3_access_key,
            "aws_secret_access_key": settings.s3_secret_key,
            "region_name": self.region,
        }

        # Add endpoint URL for R2 or MinIO
        if settings.s3_endpoint_url:
            client_kwargs["endpoint_url"] = settings.s3_endpoint_url

        self.client = boto3.client("s3", **client_kwargs)

    def _generate_key(self, prefix: str, extension: str = "png") -> str:
        """Generate a unique S3 key."""
        timestamp = datetime.now().strftime("%Y/%m/%d")
        unique_id = uuid.uuid4().hex[:12]
        return f"{prefix}/{timestamp}/{unique_id}.{extension}"

    def _create_thumbnail(self, image_data: bytes, max_size: tuple = (256, 256)) -> bytes:
        """Create a thumbnail from image data."""
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    def _get_public_url(self, key: str) -> str:
        """Get public URL for an S3 key."""
        if self.public_url:
            return f"{self.public_url.rstrip('/')}/{key}"
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"

    async def upload_image(
        self,
        image_data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        create_thumbnail: bool = True,
    ) -> StorageResult:
        """Upload image to S3."""
        try:
            # Generate keys
            image_key = self._generate_key("images")

            # Upload main image
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=image_key,
                Body=image_data,
                ContentType=content_type,
            )

            image_url = self._get_public_url(image_key)
            thumbnail_url = None

            # Create and upload thumbnail
            if create_thumbnail:
                try:
                    thumbnail_data = self._create_thumbnail(image_data)
                    thumbnail_key = image_key.replace("images/", "thumbnails/")

                    self.client.put_object(
                        Bucket=self.bucket_name,
                        Key=thumbnail_key,
                        Body=thumbnail_data,
                        ContentType=content_type,
                    )

                    thumbnail_url = self._get_public_url(thumbnail_key)
                except Exception as e:
                    logger.warning(f"Failed to create thumbnail: {e}")

            return StorageResult(
                success=True,
                url=image_url,
                thumbnail_url=thumbnail_url,
                key=image_key,
            )

        except ClientError as e:
            logger.exception(f"S3 upload error: {e}")
            return StorageResult(
                success=False,
                error_message=f"Failed to upload image: {str(e)}",
            )

    async def delete_image(self, key: str) -> bool:
        """Delete image from S3."""
        try:
            # Delete main image
            self.client.delete_object(Bucket=self.bucket_name, Key=key)

            # Delete thumbnail
            thumbnail_key = key.replace("images/", "thumbnails/")
            try:
                self.client.delete_object(Bucket=self.bucket_name, Key=thumbnail_key)
            except:
                pass  # Thumbnail might not exist

            return True
        except Exception as e:
            logger.error(f"Failed to delete S3 object {key}: {e}")
            return False

    async def download_from_url(self, url: str) -> bytes | None:
        """Download image from URL."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    return response.content
                return None
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None


class StorageService:
    """Main storage service that coordinates providers."""

    def __init__(self):
        if settings.storage_provider == "local" or not settings.has_s3_storage:
            logger.info("Using local storage provider")
            self.provider = LocalStorageProvider()
        else:
            logger.info("Using S3 storage provider")
            self.provider = S3StorageProvider()

    async def upload_image(
        self,
        image_data: bytes,
        filename: str | None = None,
        content_type: str = "image/png",
        create_thumbnail: bool = True,
    ) -> StorageResult:
        """Upload an image."""
        return await self.provider.upload_image(
            image_data=image_data,
            filename=filename,
            content_type=content_type,
            create_thumbnail=create_thumbnail,
        )

    async def upload_from_url(
        self,
        url: str,
        create_thumbnail: bool = True,
    ) -> StorageResult:
        """Download image from URL and upload to storage."""
        image_data = await self.provider.download_from_url(url)

        if image_data is None:
            return StorageResult(
                success=False,
                error_message="Failed to download image from URL",
            )

        return await self.provider.upload_image(
            image_data=image_data,
            create_thumbnail=create_thumbnail,
        )

    async def delete_image(self, key: str) -> bool:
        """Delete an image."""
        return await self.provider.delete_image(key)


# Singleton instance
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Get or create StorageService instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
