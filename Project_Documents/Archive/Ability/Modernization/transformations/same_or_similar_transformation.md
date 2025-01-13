# Same or Similar Form Transformation Rules

## Overview
This document defines the transformation rules for converting the C# Windows Forms `FormSameOrSimilar` to a modern Python web API.

## Source (C#)
```csharp
namespace DMEWorks.Ability
{
    public partial class FormSameOrSimilar : Form
    {
        private System.Windows.Forms.ComboBox cboNPI;
        private System.Windows.Forms.ComboBox cboBillingCode;
        private System.Windows.Forms.TextBox txtPolicyNumber;
        private System.Windows.Forms.Button btnCheck;
        private System.Windows.Forms.DataGridView gridResults;
        // ... other Windows Forms controls
    }
}
```

## Target (Python)
The Windows Forms application is transformed into:
1. FastAPI endpoints
2. Service layer
3. Repository layer
4. Modern web interface

## Component Mappings

### Form Controls to API Models
1. ComboBox (NPI) → NPIEntry model
```python
class NPIEntry(BaseModel):
    npi: str
    state: str
    description: str
```

2. ComboBox (Billing Code) → String list endpoint
```python
@router.get("/billing-codes")
async def get_billing_codes() -> List[str]
```

3. TextBox (Policy Number) → Request model field
```python
class SameOrSimilarRequest(BaseModel):
    npi: str
    billing_code: str
    policy_number: str
```

4. DataGridView → Response model
```python
class SameOrSimilarResponse(BaseModel):
    success: bool
    claims: List[ClaimInfo]
```

### Event Handlers to Endpoints

#### Load Form → GET Endpoints
```python
@router.get("/npis")
async def get_npis() -> List[NPIEntry]

@router.get("/billing-codes")
async def get_billing_codes() -> List[str]
```

#### Check Button → POST Endpoint
```python
@router.post("/check")
async def check_same_or_similar(
    request: SameOrSimilarRequest,
    certificate: UploadFile
) -> Dict[str, Any]
```

## Data Flow Transformation

### Windows Forms to Web API
1. Form Load
   - C#: `FormSameOrSimilar_Load`
   - Python: Separate GET endpoints for initial data

2. Button Click
   - C#: `btnCheck_Click`
   - Python: POST endpoint with request validation

3. Grid Update
   - C#: Direct DataGridView manipulation
   - Python: JSON response for frontend rendering

## Security Transformation

### Windows Forms Security
- Windows authentication
- Local certificate store
- Direct database access

### Web API Security
1. Token-based authentication
2. Certificate upload validation
3. Database access through repository
4. Input validation with Pydantic
5. CORS and rate limiting

## Error Handling Transformation

### Windows Forms Errors
- MessageBox.Show
- Try-catch blocks
- Application.Exit

### Web API Errors
1. HTTP status codes
2. Structured error responses
3. Validation errors
4. Logging middleware
5. Global exception handler

## Usage Example
```python
# Frontend API call
async def check_claims(
    npi: str,
    billing_code: str,
    policy_number: str,
    certificate: bytes
) -> Dict[str, Any]:
    url = "/api/v1/same-or-similar/check"
    files = {
        "certificate": ("cert.pem", certificate, "application/x-pem-file")
    }
    data = {
        "npi": npi,
        "billing_code": billing_code,
        "policy_number": policy_number
    }
    response = await http_client.post(url, data=data, files=files)
    return response.json()
```

## Implementation Notes
1. All Windows Forms UI logic is moved to frontend
2. Business logic is isolated in service layer
3. Data access is abstracted through repository
4. Async operations replace synchronous calls
5. Validation happens at multiple levels
6. Error handling is more granular
7. Security is enhanced for web context
