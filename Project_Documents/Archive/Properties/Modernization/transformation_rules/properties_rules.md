# Properties Transformation Rules

## Overview
This document defines the transformation rules for converting the legacy Properties components to a modern web-based system using FastAPI and React.

## Component Mapping

### 1. Resources

#### Resource Manager to Service
```python
# Legacy
internal class Resources
{
    private static ResourceManager resourceMan;
    private static CultureInfo resourceCulture;

    internal static ResourceManager ResourceManager
    {
        get
        {
            resourceMan ??= new ResourceManager(
                "DMEWorks.Properties.Resources",
                typeof(Resources).Assembly
            );
            return resourceMan;
        }
    }
}

# Modern
class ResourceService:
    """Resource service."""
    
    def __init__(self, settings: Settings):
        """Initialize service."""
        self.settings = settings
        self.cache = ResourceCache()
        self.culture = "en-US"
    
    async def get_resource(
        self,
        name: str,
        culture: Optional[str] = None
    ) -> Any:
        """Get resource by name."""
        key = f"{name}:{culture or self.culture}"
        
        # Check cache
        if cached := self.cache.get(key):
            return cached
        
        # Load resource
        resource = await self._load_resource(name, culture)
        self.cache.set(key, resource)
        return resource
```

#### Culture Management
```python
# Legacy
internal static CultureInfo Culture
{
    get => resourceCulture;
    set => resourceCulture = value;
}

# Modern
class CultureService:
    """Culture service."""
    
    def __init__(self, settings: Settings):
        """Initialize service."""
        self.settings = settings
        self.default_culture = "en-US"
        self._current_culture = self.default_culture
    
    @property
    def current_culture(self) -> str:
        """Get current culture."""
        return self._current_culture
    
    async def set_culture(self, culture: str) -> None:
        """Set current culture."""
        if not is_valid_culture(culture):
            raise ValueError(f"Invalid culture: {culture}")
        
        self._current_culture = culture
        await self.settings.save_culture(culture)
```

#### Image Resources
```typescript
// Legacy
internal static Bitmap Checked =>
    (Bitmap) ResourceManager.GetObject("Checked", resourceCulture);

// Modern
const ImageResource: React.FC<Props> = ({
  name,
  culture,
  fallback
}) => {
  const [src, setSrc] = useState<string>();
  const [error, setError] = useState<boolean>(false);
  
  useEffect(() => {
    const loadImage = async () => {
      try {
        const response = await api.get(
          `/resources/images/${name}`,
          { params: { culture } }
        );
        setSrc(response.data.url);
      } catch (err) {
        setError(true);
      }
    };
    
    loadImage();
  }, [name, culture]);
  
  if (error && fallback) {
    return <img src={fallback} alt={name} />;
  }
  
  return src ? <img src={src} alt={name} /> : null;
};
```

## Models

### 1. Resource Models
```python
class ResourceType(str, Enum):
    """Resource type."""
    STRING = "string"
    IMAGE = "image"
    BINARY = "binary"


class Resource(BaseModel):
    """Resource model."""
    name: str
    type: ResourceType
    culture: Optional[str]
    value: Any
    
    @validator('name')
    def validate_name(cls, v):
        """Validate resource name."""
        if not re.match(r'^[A-Za-z0-9_]+$', v):
            raise ValueError("Invalid resource name")
        return v


class ImageResource(Resource):
    """Image resource model."""
    type: Literal[ResourceType.IMAGE] = ResourceType.IMAGE
    value: str  # Base64 encoded image
    width: Optional[int]
    height: Optional[int]
    format: str


class StringResource(Resource):
    """String resource model."""
    type: Literal[ResourceType.STRING] = ResourceType.STRING
    value: str
    format: Optional[str]
```

### 2. Settings Models
```python
class Setting(BaseModel):
    """Setting model."""
    key: str
    value: Any
    type: str
    description: Optional[str]
    validation: Optional[str]
    
    @validator('key')
    def validate_key(cls, v):
        """Validate setting key."""
        if not re.match(r'^[A-Za-z0-9_.]+$', v):
            raise ValueError("Invalid setting key")
        return v


class SettingUpdate(BaseModel):
    """Setting update model."""
    value: Any
    description: Optional[str]
    validation: Optional[str]
```

## Validation Rules

### 1. Resource Validation
```python
def validate_resource_name(name: str) -> None:
    """Validate resource name."""
    if not name:
        raise ValueError("Resource name is required")
        
    if not re.match(r'^[A-Za-z0-9_]+$', name):
        raise ValueError("Invalid resource name format")

def validate_culture(culture: str) -> None:
    """Validate culture code."""
    try:
        locale.setlocale(locale.LC_ALL, culture)
    except locale.Error:
        raise ValueError(f"Invalid culture code: {culture}")
```

### 2. Image Validation
```python
def validate_image(image: bytes) -> None:
    """Validate image data."""
    try:
        img = Image.open(BytesIO(image))
        
        if img.format not in {'PNG', 'JPEG', 'GIF'}:
            raise ValueError("Unsupported image format")
            
        if img.size[0] > 2000 or img.size[1] > 2000:
            raise ValueError("Image too large")
            
    except Exception as e:
        raise ValueError(f"Invalid image: {str(e)}")
```

## Security Rules

### 1. Access Control
```python
def verify_resource_access(user: User, resource: str) -> bool:
    """Verify user has access to resource."""
    return (
        user.has_permission('resources.access') and
        not resource.startswith('_')
    )

def verify_settings_access(user: User) -> bool:
    """Verify user can access settings."""
    return user.has_permission('settings.access')
```

### 2. Validation
```python
def validate_setting_update(
    user: User,
    setting: Setting,
    value: Any
) -> None:
    """Validate setting update."""
    if not verify_settings_access(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
        
    if setting.validation:
        validate_value(value, setting.validation)
```

## Testing Rules

### 1. Service Tests
```python
@pytest.mark.asyncio
async def test_resource_loading():
    """Test resource loading."""
    service = ResourceService(settings)
    
    # Test string resource
    result = await service.get_resource("welcome_message")
    assert isinstance(result, str)
    assert result == "Welcome"
    
    # Test image resource
    result = await service.get_resource("logo")
    assert isinstance(result, bytes)
    assert Image.open(BytesIO(result))
```

### 2. API Tests
```python
async def test_resource_endpoints():
    """Test resource API."""
    # Get resource
    response = await client.get("/resources/welcome_message")
    assert response.status_code == 200
    assert response.json()["value"] == "Welcome"
    
    # Set culture
    response = await client.put(
        "/resources/culture",
        json={"culture": "es-ES"}
    )
    assert response.status_code == 200
    
    # Get localized resource
    response = await client.get(
        "/resources/welcome_message",
        params={"culture": "es-ES"}
    )
    assert response.json()["value"] == "Bienvenido"
```

### 3. UI Tests
```typescript
describe('ImageResource', () => {
  it('loads and displays image', async () => {
    render(
      <ImageResource
        name="logo"
        fallback="/images/default.png"
      />
    );
    
    // Wait for image load
    const img = await screen.findByRole('img');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src');
  });
  
  it('shows fallback on error', async () => {
    server.use(
      rest.get('/resources/images/logo', (req, res, ctx) =>
        res(ctx.status(404))
      )
    );
    
    render(
      <ImageResource
        name="logo"
        fallback="/images/default.png"
      />
    );
    
    const img = await screen.findByRole('img');
    expect(img).toHaveAttribute('src', '/images/default.png');
  });
});
