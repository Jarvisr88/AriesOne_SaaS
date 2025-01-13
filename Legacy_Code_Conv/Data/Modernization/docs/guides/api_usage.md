# API Usage Guide

## Authentication

### 1. Get Access Token
```python
import requests

def get_token(username: str, password: str) -> str:
    response = requests.post(
        "http://localhost:8000/auth/token",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]

# Usage
token = get_token("admin@example.com", "password123")
headers = {"Authorization": f"Bearer {token}"}
```

### 2. Refresh Token
```python
def refresh_token(refresh_token: str) -> str:
    response = requests.post(
        "http://localhost:8000/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    return response.json()["access_token"]
```

## Company Management

### 1. Create Company
```python
def create_company(token: str, company_data: dict) -> dict:
    response = requests.post(
        "http://localhost:8000/api/v1/companies",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Acme Healthcare",
            "tax_id": "12-3456789",
            "npi": "1234567890",
            "address": "123 Main St, City, State 12345",
            "phone": "555-123-4567",
            "email": "contact@acme.com"
        }
    )
    return response.json()

# Usage
company = create_company(token, company_data)
print(f"Created company: {company['id']}")
```

### 2. Update Company
```python
def update_company(token: str, company_id: str, data: dict) -> dict:
    response = requests.put(
        f"http://localhost:8000/api/v1/companies/{company_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )
    return response.json()

# Usage
updated = update_company(token, "123", {"name": "New Name"})
```

### 3. List Companies
```python
def list_companies(
    token: str,
    page: int = 1,
    size: int = 10,
    active: bool = True
) -> dict:
    response = requests.get(
        "http://localhost:8000/api/v1/companies",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "page": page,
            "size": size,
            "active": active
        }
    )
    return response.json()

# Usage
companies = list_companies(token, page=1, size=10)
for company in companies["items"]:
    print(f"{company['name']} ({company['npi']})")
```

## Location Management

### 1. Create Location
```python
def create_location(token: str, company_id: str, location_data: dict) -> dict:
    response = requests.post(
        f"http://localhost:8000/api/v1/companies/{company_id}/locations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Main Clinic",
            "address": "456 Oak St, City, State 12345",
            "phone": "555-987-6543",
            "is_active": True
        }
    )
    return response.json()
```

### 2. List Locations
```python
def list_locations(token: str, company_id: str) -> list:
    response = requests.get(
        f"http://localhost:8000/api/v1/companies/{company_id}/locations",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["items"]
```

## Error Handling

### 1. Handle API Errors
```python
class APIError(Exception):
    """Custom API error."""
    pass

def handle_response(response: requests.Response) -> dict:
    """Handle API response and errors."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error = response.json()
        raise APIError(
            f"API Error: {error.get('detail', str(e))}"
        )
    except requests.exceptions.RequestException as e:
        raise APIError(f"Request failed: {str(e)}")
```

### 2. Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def api_call_with_retry(func, *args, **kwargs):
    """Execute API call with retry logic."""
    try:
        return func(*args, **kwargs)
    except APIError as e:
        print(f"API call failed: {str(e)}")
        raise
```

## Batch Operations

### 1. Bulk Create Companies
```python
def bulk_create_companies(token: str, companies: list) -> list:
    response = requests.post(
        "http://localhost:8000/api/v1/companies/bulk",
        headers={"Authorization": f"Bearer {token}"},
        json={"items": companies}
    )
    return response.json()["items"]
```

### 2. Bulk Update Companies
```python
def bulk_update_companies(token: str, updates: list) -> list:
    response = requests.put(
        "http://localhost:8000/api/v1/companies/bulk",
        headers={"Authorization": f"Bearer {token}"},
        json={"items": updates}
    )
    return response.json()["items"]
```

## File Operations

### 1. Upload Company Document
```python
def upload_document(token: str, company_id: str, file_path: str) -> dict:
    with open(file_path, "rb") as f:
        response = requests.post(
            f"http://localhost:8000/api/v1/companies/{company_id}/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": f}
        )
    return response.json()
```

### 2. Download Company Document
```python
def download_document(token: str, company_id: str, document_id: str) -> bytes:
    response = requests.get(
        f"http://localhost:8000/api/v1/companies/{company_id}/documents/{document_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.content
```

## Complete Example

### Company Management System
```python
class CompanyManager:
    """Company management system."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
    
    def login(self, username: str, password: str):
        """Login and get token."""
        self.token = get_token(username, password)
    
    @retry(stop=stop_after_attempt(3))
    def create_company_with_location(
        self,
        company_data: dict,
        location_data: dict
    ) -> tuple:
        """Create company with location."""
        # Create company
        company = create_company(self.token, company_data)
        
        # Create location
        location = create_location(
            self.token,
            company["id"],
            location_data
        )
        
        return company, location
    
    def get_company_details(self, company_id: str) -> dict:
        """Get company with locations."""
        company = self.get_company(company_id)
        locations = self.list_locations(company_id)
        return {
            **company,
            "locations": locations
        }

# Usage example
manager = CompanyManager("http://localhost:8000")
manager.login("admin@example.com", "password123")

# Create company with location
company, location = manager.create_company_with_location(
    company_data={
        "name": "Acme Healthcare",
        "tax_id": "12-3456789",
        "npi": "1234567890"
    },
    location_data={
        "name": "Main Clinic",
        "address": "123 Main St"
    }
)

# Get full details
details = manager.get_company_details(company["id"])
print(f"Company: {details['name']}")
print(f"Locations: {len(details['locations'])}")
```

## Best Practices

1. **Authentication**
   - Store tokens securely
   - Refresh before expiration
   - Use environment variables

2. **Error Handling**
   - Implement retry logic
   - Log errors properly
   - Use custom exceptions

3. **Performance**
   - Use connection pooling
   - Implement pagination
   - Cache responses

4. **Security**
   - Validate SSL certificates
   - Sanitize inputs
   - Use latest library versions
