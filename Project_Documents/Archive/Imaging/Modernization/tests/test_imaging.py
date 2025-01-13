"""Test cases for image operations."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from fastapi import UploadFile, HTTPException

from ..models.imaging_models import (
    ImageMetadata,
    ImageResponse,
    ImageUploadRequest,
    ImageListResponse
)
from ..services.imaging_service import ImageService, StorageClient


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_storage():
    """Create mock storage client."""
    return AsyncMock(spec=StorageClient)


@pytest.fixture
def image_service(mock_session, mock_storage):
    """Create image service with mocks."""
    return ImageService(mock_session, mock_storage)


@pytest.fixture
def mock_image():
    """Create mock upload file."""
    return AsyncMock(
        spec=UploadFile,
        filename="test.jpg",
        content_type="image/jpeg",
        size=1024
    )


@pytest.mark.asyncio
async def test_upload_image_success(image_service, mock_image):
    """Test successful image upload."""
    # Setup
    company = "test_company"
    metadata = ImageUploadRequest(
        company=company,
        filename=mock_image.filename,
        content_type=mock_image.content_type,
        size=mock_image.size
    )
    
    # Mock storage operations
    image_service.storage.upload_blob = AsyncMock()
    image_service.storage.get_signed_url = AsyncMock(
        return_value="https://storage.test/image.jpg"
    )
    
    # Execute
    response = await image_service.upload_image(company, mock_image, metadata)
    
    # Verify
    assert isinstance(response, ImageResponse)
    assert response.url == "https://storage.test/image.jpg"
    assert response.metadata is not None
    assert response.metadata.company == company
    assert response.metadata.filename == mock_image.filename


@pytest.mark.asyncio
async def test_upload_image_storage_error(image_service, mock_image):
    """Test image upload with storage error."""
    # Setup
    company = "test_company"
    metadata = ImageUploadRequest(
        company=company,
        filename=mock_image.filename,
        content_type=mock_image.content_type,
        size=mock_image.size
    )
    
    # Mock storage error
    image_service.storage.upload_blob = AsyncMock(
        side_effect=Exception("Storage error")
    )
    
    # Execute and verify
    with pytest.raises(HTTPException) as exc:
        await image_service.upload_image(company, mock_image, metadata)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_get_image_success(image_service):
    """Test successful image retrieval."""
    # Setup
    company = "test_company"
    image_id = "test_image"
    mock_metadata = ImageMetadata(
        id=image_id,
        company=company,
        filename="test.jpg",
        content_type="image/jpeg",
        size=1024,
        created_at=datetime.utcnow()
    )
    
    # Mock database query
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_metadata
    image_service.session.execute = AsyncMock(return_value=mock_result)
    
    # Mock storage URL
    image_service.storage.get_signed_url = AsyncMock(
        return_value="https://storage.test/image.jpg"
    )
    
    # Execute
    response = await image_service.get_image(company, image_id)
    
    # Verify
    assert isinstance(response, ImageResponse)
    assert response.id == image_id
    assert response.url == "https://storage.test/image.jpg"
    assert response.metadata == mock_metadata


@pytest.mark.asyncio
async def test_get_image_not_found(image_service):
    """Test image retrieval when not found."""
    # Setup
    company = "test_company"
    image_id = "test_image"
    
    # Mock database query returning None
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    image_service.session.execute = AsyncMock(return_value=mock_result)
    
    # Execute and verify
    with pytest.raises(HTTPException) as exc:
        await image_service.get_image(company, image_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_image_success(image_service):
    """Test successful image deletion."""
    # Setup
    company = "test_company"
    image_id = "test_image"
    mock_metadata = ImageMetadata(
        id=image_id,
        company=company,
        filename="test.jpg",
        content_type="image/jpeg",
        size=1024,
        created_at=datetime.utcnow()
    )
    
    # Mock database query
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_metadata
    image_service.session.execute = AsyncMock(return_value=mock_result)
    
    # Mock storage deletion
    image_service.storage.delete_blob = AsyncMock()
    
    # Execute
    await image_service.delete_image(company, image_id)
    
    # Verify
    assert mock_metadata.deleted_at is not None
    image_service.storage.delete_blob.assert_called_once()


@pytest.mark.asyncio
async def test_list_images_success(image_service):
    """Test successful image listing."""
    # Setup
    company = "test_company"
    mock_images = [
        ImageMetadata(
            id=f"image_{i}",
            company=company,
            filename=f"test_{i}.jpg",
            content_type="image/jpeg",
            size=1024,
            created_at=datetime.utcnow()
        )
        for i in range(3)
    ]
    
    # Mock database queries
    image_service.session.scalar = AsyncMock(return_value=len(mock_images))
    mock_result = AsyncMock()
    mock_result.scalars().all.return_value = mock_images
    image_service.session.execute = AsyncMock(return_value=mock_result)
    
    # Execute
    response = await image_service.list_images(company)
    
    # Verify
    assert isinstance(response, ImageListResponse)
    assert len(response.images) == 3
    assert response.total == 3
    assert response.page == 1
    assert response.page_size == 20
