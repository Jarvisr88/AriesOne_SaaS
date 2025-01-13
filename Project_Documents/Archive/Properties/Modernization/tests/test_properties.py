"""Properties tests."""
import base64
from io import BytesIO
import pytest
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..models.properties_models import (
    ResourceType,
    ResourceCreate,
    ResourceUpdate,
    SettingCreate,
    SettingUpdate
)
from ..services.properties_service import (
    ResourceService,
    SettingService
)


@pytest.fixture
def resource_service(session: AsyncSession) -> ResourceService:
    """Resource service fixture."""
    return ResourceService(session)


@pytest.fixture
def setting_service(session: AsyncSession) -> SettingService:
    """Setting service fixture."""
    return SettingService(session)


@pytest.fixture
def test_image() -> bytes:
    """Test image fixture."""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.mark.asyncio
async def test_create_string_resource(
    resource_service: ResourceService,
    user_id: int
):
    """Test creating string resource."""
    data = ResourceCreate(
        name="welcome_message",
        type=ResourceType.STRING,
        value="Welcome to DMEWorks",
        culture="en-US"
    )
    
    resource = await resource_service.create_resource(data, user_id)
    
    assert resource.name == "welcome_message"
    assert resource.type == ResourceType.STRING
    assert resource.string_value == "Welcome to DMEWorks"
    assert resource.culture == "en-US"
    assert resource.binary_value is None


@pytest.mark.asyncio
async def test_create_image_resource(
    resource_service: ResourceService,
    user_id: int,
    test_image: bytes
):
    """Test creating image resource."""
    data = ResourceCreate(
        name="logo",
        type=ResourceType.IMAGE,
        value=base64.b64encode(test_image).decode(),
        metadata={'alt': 'Company Logo'}
    )
    
    resource = await resource_service.create_resource(data, user_id)
    
    assert resource.name == "logo"
    assert resource.type == ResourceType.IMAGE
    assert resource.binary_value == test_image
    assert resource.string_value is None
    assert resource.metadata['alt'] == 'Company Logo'
    assert 'width' in resource.metadata
    assert 'height' in resource.metadata
    assert 'format' in resource.metadata


@pytest.mark.asyncio
async def test_update_resource(
    resource_service: ResourceService,
    user_id: int
):
    """Test updating resource."""
    # Create initial resource
    create_data = ResourceCreate(
        name="welcome_message",
        type=ResourceType.STRING,
        value="Welcome to DMEWorks",
        culture="en-US"
    )
    resource = await resource_service.create_resource(
        create_data,
        user_id
    )
    
    # Update resource
    update_data = ResourceUpdate(
        name="welcome_message",
        type=ResourceType.STRING,
        value="¡Bienvenido a DMEWorks!",
        culture="es-ES",
        reason="Spanish translation"
    )
    updated = await resource_service.update_resource(
        "welcome_message",
        update_data,
        user_id
    )
    
    assert updated.string_value == "¡Bienvenido a DMEWorks!"
    assert updated.culture == "es-ES"
    
    # Check history
    history = await resource_service.get_resource_history("welcome_message")
    assert len(history) == 1
    assert history[0].string_value == "Welcome to DMEWorks"
    assert history[0].culture == "en-US"
    assert history[0].reason == "Spanish translation"


@pytest.mark.asyncio
async def test_invalid_culture(
    resource_service: ResourceService,
    user_id: int
):
    """Test invalid culture code."""
    data = ResourceCreate(
        name="welcome_message",
        type=ResourceType.STRING,
        value="Welcome",
        culture="invalid"
    )
    
    with pytest.raises(HTTPException) as exc:
        await resource_service.create_resource(data, user_id)
    
    assert exc.value.status_code == 400
    assert "Invalid culture code" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_invalid_image(
    resource_service: ResourceService,
    user_id: int
):
    """Test invalid image data."""
    data = ResourceCreate(
        name="logo",
        type=ResourceType.IMAGE,
        value="invalid_base64"
    )
    
    with pytest.raises(HTTPException) as exc:
        await resource_service.create_resource(data, user_id)
    
    assert exc.value.status_code == 400
    assert "Invalid image" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_create_setting(
    setting_service: SettingService,
    user_id: int
):
    """Test creating setting."""
    data = SettingCreate(
        key="max_items",
        type="integer",
        value=100,
        validation="positive_integer",
        description="Maximum number of items"
    )
    
    setting = await setting_service.create_setting(data, user_id)
    
    assert setting.key == "max_items"
    assert setting.value == 100
    assert setting.type == "integer"
    assert setting.validation == "positive_integer"
    assert setting.description == "Maximum number of items"


@pytest.mark.asyncio
async def test_update_setting(
    setting_service: SettingService,
    user_id: int
):
    """Test updating setting."""
    # Create initial setting
    create_data = SettingCreate(
        key="max_items",
        type="integer",
        value=100,
        validation="positive_integer"
    )
    setting = await setting_service.create_setting(
        create_data,
        user_id
    )
    
    # Update setting
    update_data = SettingUpdate(
        value=200,
        reason="Increased limit"
    )
    updated = await setting_service.update_setting(
        "max_items",
        update_data,
        user_id
    )
    
    assert updated.value == 200
    
    # Check history
    history = await setting_service.get_setting_history("max_items")
    assert len(history) == 1
    assert history[0].value == 100
    assert history[0].reason == "Increased limit"


@pytest.mark.asyncio
async def test_invalid_setting_value(
    setting_service: SettingService,
    user_id: int
):
    """Test invalid setting value."""
    data = SettingCreate(
        key="max_items",
        type="integer",
        value=-1,
        validation="positive_integer"
    )
    
    with pytest.raises(HTTPException) as exc:
        await setting_service.create_setting(data, user_id)
    
    assert exc.value.status_code == 400
    assert "must be a positive integer" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_setting_not_found(
    setting_service: SettingService,
    user_id: int
):
    """Test setting not found."""
    data = SettingUpdate(value=100)
    
    with pytest.raises(HTTPException) as exc:
        await setting_service.update_setting(
            "non_existent",
            data,
            user_id
        )
    
    assert exc.value.status_code == 404
    assert "Setting not found" in str(exc.value.detail)
