# Validation Rules Transformation

## 1. Address Validation

### Field-Level Validation

#### Address Line 1
```python
# Legacy
if (string.IsNullOrEmpty(txtAddress1.Text))
    throw new ArgumentException("Address is required");

# Modern
@validator('address_line1')
def validate_address_line1(cls, v):
    if not v:
        raise ValueError('Address line 1 is required')
    if len(v) > 100:
        raise ValueError('Address line 1 must be 100 characters or less')
    return v.strip()
```

#### State
```python
# Legacy
if (txtState.Text.Length != 2)
    throw new ArgumentException("State must be 2 letters");

# Modern
@validator('state')
def validate_state(cls, v):
    if not v:
        raise ValueError('State is required')
    if not re.match(r'^[A-Z]{2}$', v):
        raise ValueError('State must be 2 uppercase letters')
    return v
```

#### ZIP Code
```python
# Legacy
if (!Regex.IsMatch(txtZip.Text, @"^\d{5}(-\d{4})?$"))
    throw new ArgumentException("Invalid ZIP code");

# Modern
@validator('zip_code')
def validate_zip_code(cls, v):
    if not re.match(r'^\d{5}(-\d{4})?$', v):
        raise ValueError('Invalid ZIP code format')
    return v
```

### Business Rules
1. Required Fields
   ```python
   class Address(BaseModel):
       address_line1: str = Field(..., min_length=1, max_length=100)
       city: str = Field(..., min_length=1, max_length=50)
       state: str = Field(..., min_length=2, max_length=2)
       zip_code: str = Field(..., min_length=5, max_length=10)
   ```

2. Format Standardization
   ```python
   def standardize_address(self, address: Address) -> Address:
       address.city = address.city.title()
       address.state = address.state.upper()
       address.zip_code = self._format_zip(address.zip_code)
       return address
   ```

## 2. Name Validation

### Field-Level Validation

#### First Name
```python
# Legacy
if (string.IsNullOrEmpty(txtFirstName.Text))
    throw new ArgumentException("First name is required");

# Modern
@validator('first_name')
def validate_first_name(cls, v):
    if not v:
        raise ValueError('First name is required')
    if len(v) > 50:
        raise ValueError('First name must be 50 characters or less')
    return v.strip().title()
```

#### Middle Initial
```python
# Legacy
if (txtMiddleName.Text.Length > 1)
    txtMiddleName.Text = txtMiddleName.Text[0].ToString();

# Modern
@validator('middle_initial')
def validate_middle_initial(cls, v):
    if v and len(v) > 1:
        v = v[0]
    return v.upper() if v else None
```

#### Suffix
```python
# Legacy
if (!IsValidSuffix(txtSuffix.Text))
    throw new ArgumentException("Invalid suffix");

# Modern
@validator('suffix')
def validate_suffix(cls, v):
    valid_suffixes = {'Jr.', 'Sr.', 'II', 'III', 'IV'}
    if v and v not in valid_suffixes:
        raise ValueError(f'Invalid suffix. Must be one of {valid_suffixes}')
    return v
```

### Business Rules
1. Required Fields
   ```python
   class Name(BaseModel):
       first_name: str = Field(..., min_length=1, max_length=50)
       last_name: str = Field(..., min_length=1, max_length=50)
       middle_initial: Optional[str] = Field(None, max_length=1)
       suffix: Optional[str] = Field(None)
       courtesy_title: Optional[CourtesyTitle] = Field(None)
   ```

2. Format Standardization
   ```python
   def standardize_name(self, name: Name) -> Name:
       name.first_name = name.first_name.title()
       name.last_name = name.last_name.title()
       if name.middle_initial:
           name.middle_initial = name.middle_initial.upper()
       return name
   ```

## 3. Map Provider Validation

### Provider Configuration
```python
# Legacy
if (provider == null)
    throw new ArgumentNullException("provider");

# Modern
class MapProviderConfig(BaseModel):
    provider: MapProvider
    api_key: Optional[str] = Field(None)
    base_url: HttpUrl
    enabled: bool = True
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not str(v).startswith('https'):
            raise ValueError('Base URL must use HTTPS')
        return v
```

### Search Results
```python
# Legacy
if (searchResult.Confidence < 0.5)
    return null;

# Modern
class MapSearchResult(BaseModel):
    location: MapLocation
    confidence_score: float = Field(..., ge=0, le=1)
    provider: MapProvider
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if v < 0.5:
            raise ValueError('Search result confidence too low')
        return v
```

## 4. Error Response Validation

### Response Format
```python
class ErrorResponse(BaseModel):
    status_code: int = Field(..., ge=100, le=599)
    error: str
    message: str
    details: Optional[Dict[str, List[str]]]
    timestamp: datetime
    
    @validator('error')
    def validate_error(cls, v):
        valid_errors = {
            'ValidationError',
            'NotFoundError',
            'SystemError'
        }
        if v not in valid_errors:
            raise ValueError(f'Invalid error type. Must be one of {valid_errors}')
        return v
```

### Error Mapping
```python
def map_exception_to_error(exc: Exception) -> ErrorResponse:
    if isinstance(exc, ValidationError):
        return ErrorResponse(
            status_code=400,
            error='ValidationError',
            message=str(exc),
            details=exc.errors()
        )
    elif isinstance(exc, NotFoundError):
        return ErrorResponse(
            status_code=404,
            error='NotFoundError',
            message=str(exc)
        )
    else:
        return ErrorResponse(
            status_code=500,
            error='SystemError',
            message='Internal server error'
        )
```
