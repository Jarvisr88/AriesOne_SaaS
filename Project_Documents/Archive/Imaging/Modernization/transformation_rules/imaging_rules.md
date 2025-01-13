# Imaging Components Transformation Rules

## Overview
This document defines the transformation rules for converting the legacy Imaging components to a modern web-based system using FastAPI and cloud storage.

## Component Mapping

### 1. ImagingHelper Class

#### HTTP Operations to FastAPI
```python
# Legacy
public class ImagingHelper
{
    private readonly Uri uriget;
    private readonly Uri uriput;
    private readonly Uri uridel;
}

# Modern
class ImageService:
    def __init__(self, storage_client: StorageClient):
        self.storage = storage_client
        
    async def upload_image(self, data: UploadImageRequest) -> ImageResponse:
        pass
        
    async def get_image(self, image_id: str) -> ImageResponse:
        pass
        
    async def delete_image(self, image_id: str) -> None:
        pass
```

#### Image Upload
```python
# Legacy
public void PutImage(string company, int imageIndex, Stream imageData)
{
    using (MemoryStream stream = new MemoryStream())
    {
        HttpHelper helper = new HttpHelper(stream);
        helper.AppendParameter("company", company);
        helper.AppendParameter("index", imageIndex.ToString());
        helper.AppendParameter("image", "image.jpg", imageData);
        helper.CloseRequest();
        // ... HTTP request code
    }
}

# Modern
async def upload_image(
    self,
    company: str,
    image_data: UploadFile,
    metadata: ImageMetadata
) -> ImageResponse:
    """Upload image to storage."""
    try:
        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        # Upload to cloud storage
        blob_path = f"{company}/{image_id}"
        await self.storage.upload_blob(
            blob_path,
            image_data.file,
            content_type=image_data.content_type
        )
        
        # Save metadata
        await self.save_metadata(ImageMetadata(
            id=image_id,
            company=company,
            filename=image_data.filename,
            content_type=image_data.content_type,
            size=image_data.size,
            created_at=datetime.utcnow()
        ))
        
        return ImageResponse(
            id=image_id,
            url=await self.storage.get_url(blob_path)
        )
    except Exception as e:
        raise ImageUploadError(str(e))
```

#### Image Download
```python
# Legacy
public Stream GetImage(string company, int imageIndex)
{
    using (MemoryStream stream = new MemoryStream())
    {
        HttpHelper helper = new HttpHelper(stream);
        helper.AppendParameter("company", company);
        helper.AppendParameter("index", imageIndex.ToString());
        helper.CloseRequest();
        // ... HTTP request code
    }
}

# Modern
async def get_image(
    self,
    company: str,
    image_id: str
) -> ImageResponse:
    """Get image from storage."""
    try:
        # Get metadata
        metadata = await self.get_metadata(company, image_id)
        if not metadata:
            raise ImageNotFoundError()
            
        # Get signed URL
        blob_path = f"{company}/{image_id}"
        url = await self.storage.get_signed_url(
            blob_path,
            expiry=timedelta(minutes=15)
        )
        
        return ImageResponse(
            id=image_id,
            url=url,
            metadata=metadata
        )
    except Exception as e:
        raise ImageRetrievalError(str(e))
```

### 2. MIME Type Configuration

#### Configuration Models
```python
# Legacy
public class MimeTypeElement : ConfigurationElement
{
    public string Extension { get; set; }
    public string MimeType { get; set; }
    public string Description { get; set; }
}

# Modern
class MimeTypeConfig(BaseModel):
    """MIME type configuration."""
    
    extension: str
    mime_type: str
    description: Optional[str] = None
    
    class Config:
        orm_mode = True
```

#### Collection Management
```python
# Legacy
public class MimeTypeElementCollection : ConfigurationElementCollection
{
    public MimeTypeElement this[int index] { get; }
    public void Add(MimeTypeElement element);
    public void Remove(string name);
}

# Modern
class MimeTypeService:
    """Service for managing MIME types."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_mime_type(self, mime_type: MimeTypeCreate) -> MimeType:
        """Add new MIME type."""
        db_mime_type = MimeType(**mime_type.dict())
        self.session.add(db_mime_type)
        await self.session.commit()
        return db_mime_type
    
    async def get_mime_types(self) -> List[MimeType]:
        """Get all MIME types."""
        result = await self.session.execute(select(MimeType))
        return result.scalars().all()
```

### 3. API Endpoints

#### Image Operations
```python
# Modern FastAPI Routes
@router.post(
    "/images",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image",
    description="Upload new image to storage"
)
async def upload_image(
    company: str = Path(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service)
) -> ImageResponse:
    """Upload new image."""
    if not await service.has_company_access(current_user, company):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
        
    return await service.upload_image(company, image)

@router.get(
    "/images/{image_id}",
    response_model=ImageResponse,
    summary="Get image",
    description="Get image by ID"
)
async def get_image(
    company: str = Path(...),
    image_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    service: ImageService = Depends(get_image_service)
) -> ImageResponse:
    """Get image by ID."""
    if not await service.has_company_access(current_user, company):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
        
    return await service.get_image(company, image_id)
```

### 4. Storage Integration

#### Cloud Storage Client
```python
class StorageClient:
    """Client for cloud storage operations."""
    
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.client = boto3.client('s3')
    
    async def upload_blob(
        self,
        path: str,
        data: BinaryIO,
        content_type: str
    ) -> None:
        """Upload blob to storage."""
        await self.client.upload_fileobj(
            data,
            self.bucket,
            path,
            ExtraArgs={'ContentType': content_type}
        )
    
    async def get_signed_url(
        self,
        path: str,
        expiry: timedelta
    ) -> str:
        """Get signed URL for blob."""
        return await self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': path
            },
            ExpiresIn=int(expiry.total_seconds())
        )
```

## Validation Rules

### 1. Input Validation
- Validate image size and format
- Check MIME type against allowed list
- Verify company access
- Sanitize filenames

### 2. Error Handling
- Use custom exception classes
- Include error details
- Log all errors
- Return appropriate status codes

## Security Rules

### 1. Authentication
- Use JWT tokens
- Verify company access
- Implement role-based access
- Rate limit requests

### 2. Storage Security
- Use signed URLs
- Set appropriate CORS
- Enable encryption
- Implement backup strategy

## Testing Rules

### 1. Service Tests
- Test all CRUD operations
- Verify error handling
- Check validation rules
- Test concurrent access

### 2. API Tests
- Test all endpoints
- Verify authentication
- Check response formats
- Test error responses

### 3. Storage Tests
- Test upload/download
- Verify cleanup
- Check performance
- Test error cases
