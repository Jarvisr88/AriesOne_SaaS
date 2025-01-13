# Misc Components Transformation Rules

## Overview
This document defines the transformation rules for converting the legacy Misc components to a modern web-based system using FastAPI and React.

## Component Mapping

### 1. DialogDeposit

#### Wizard to React Steps
```typescript
// Legacy
public class DialogDeposit : DmeForm
{
    private readonly BaseStage stageWelcome;
    private readonly BaseStage stageCustomer;
    private readonly BaseStage stageDeposit;
    private readonly BaseStage stageAmounts;
    private readonly BaseStage stageReview;
    private readonly BaseStage stageResult;
}

// Modern
const DepositWizard: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const steps = [
    'Welcome',
    'Customer',
    'Deposit',
    'Amounts',
    'Review',
    'Result'
  ];
  
  return (
    <Stepper activeStep={activeStep}>
      {steps.map((label) => (
        <Step key={label}>
          <StepLabel>{label}</StepLabel>
        </Step>
      ))}
    </Stepper>
  );
};
```

#### Deposit Data Model
```python
# Modern Pydantic Models
class DepositCreate(BaseModel):
    """Request model for creating deposit."""
    customer_id: int
    order_id: Optional[int]
    amount: Decimal
    payment_method: str
    reference: Optional[str]
    notes: Optional[str]

class DepositResponse(BaseModel):
    """Response model for deposit operations."""
    id: int
    customer_id: int
    order_id: Optional[int]
    amount: Decimal
    payment_method: str
    reference: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

class DepositStatus(BaseModel):
    """Deposit status update model."""
    status: str
    reason: Optional[str]
```

### 2. DialogVoidSubmission

#### Dialog to React Component
```typescript
// Legacy
public class DialogVoidSubmission : Form
{
    private RadioButton rbAction_Void;
    private RadioButton rbAction_Replacement;
    private TextBox txtClaimNumber;
}

// Modern
const VoidSubmissionDialog: React.FC = () => {
  const [action, setAction] = useState<'void' | 'replace'>('void');
  const [claimNumber, setClaimNumber] = useState('');
  
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Void Submission</DialogTitle>
      <DialogContent>
        <RadioGroup value={action} onChange={(e) => setAction(e.target.value)}>
          <FormControlLabel value="void" control={<Radio />} label="Void" />
          <FormControlLabel value="replace" control={<Radio />} label="Replace" />
        </RadioGroup>
        <TextField
          label="Claim Number"
          value={claimNumber}
          onChange={(e) => setClaimNumber(e.target.value)}
        />
      </DialogContent>
    </Dialog>
  );
};
```

#### Void Submission Models
```python
class VoidSubmissionRequest(BaseModel):
    """Request model for voiding submission."""
    claim_number: str
    action: Literal['void', 'replace']
    reason: str
    replacement_claim: Optional[str]

class VoidSubmissionResponse(BaseModel):
    """Response model for void submission."""
    claim_number: str
    action: str
    status: str
    processed_at: datetime
    replacement_claim: Optional[str]
```

### 3. FormReceivePurchaseOrder

#### Form to React Component
```typescript
// Legacy
public class FormReceivePurchaseOrder : DmeForm
{
    private TextBox txtBarcode;
    private FilteredGrid filteredGrid1;
}

// Modern
const ReceivePurchaseOrder: React.FC<{ orderId: number }> = ({ orderId }) => {
  const [barcode, setBarcode] = useState('');
  const [items, setItems] = useState<OrderItem[]>([]);
  
  const handleScan = async (code: string) => {
    try {
      const response = await api.post(`/purchase-orders/${orderId}/scan`, {
        barcode: code
      });
      setItems(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Scan error:', error);
    }
  };
  
  return (
    <Box>
      <TextField
        label="Scan Barcode"
        value={barcode}
        onChange={(e) => setBarcode(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      <DataGrid
        rows={items}
        columns={columns}
        pageSize={10}
        autoHeight
      />
    </Box>
  );
};
```

#### Purchase Order Models
```python
class OrderItem(BaseModel):
    """Order item model."""
    id: int
    order_id: int
    product_id: int
    barcode: str
    quantity: int
    received_quantity: int
    status: str

class ScanRequest(BaseModel):
    """Request model for barcode scan."""
    barcode: str
    quantity: int = 1

class ScanResponse(BaseModel):
    """Response model for barcode scan."""
    item: OrderItem
    message: str
    status: str
```

## Validation Rules

### 1. Deposit Validation
```python
def validate_deposit(deposit: DepositCreate) -> None:
    """Validate deposit request."""
    if deposit.amount <= 0:
        raise ValueError("Deposit amount must be positive")
        
    if not is_valid_payment_method(deposit.payment_method):
        raise ValueError("Invalid payment method")
        
    if deposit.order_id and not order_exists(deposit.order_id):
        raise ValueError("Invalid order ID")
```

### 2. Void Submission Validation
```python
def validate_void_submission(request: VoidSubmissionRequest) -> None:
    """Validate void submission request."""
    if not is_valid_claim_number(request.claim_number):
        raise ValueError("Invalid claim number")
        
    if request.action == 'replace' and not request.replacement_claim:
        raise ValueError("Replacement claim required")
```

### 3. Purchase Order Validation
```python
def validate_scan(request: ScanRequest, order: Order) -> None:
    """Validate barcode scan."""
    item = get_item_by_barcode(request.barcode)
    if not item:
        raise ValueError("Invalid barcode")
        
    if item.order_id != order.id:
        raise ValueError("Item not in order")
        
    if item.received_quantity + request.quantity > item.quantity:
        raise ValueError("Quantity exceeds order amount")
```

## Security Rules

### 1. Authentication
- Use JWT tokens
- Verify company access
- Implement role-based access
- Rate limit requests

### 2. Authorization
```python
def verify_deposit_access(user: User, company_id: int) -> bool:
    """Verify user has access to make deposits."""
    return (
        user.has_permission('deposits.create') and
        user.has_company_access(company_id)
    )

def verify_void_access(user: User, claim: Claim) -> bool:
    """Verify user can void claims."""
    return (
        user.has_permission('claims.void') and
        user.has_company_access(claim.company_id)
    )
```

## Testing Rules

### 1. Service Tests
```python
@pytest.mark.asyncio
async def test_create_deposit():
    """Test deposit creation."""
    deposit = DepositCreate(
        customer_id=1,
        amount=Decimal('100.00'),
        payment_method='credit_card'
    )
    response = await service.create_deposit(deposit)
    assert response.status == 'pending'
    assert response.amount == deposit.amount

@pytest.mark.asyncio
async def test_void_claim():
    """Test claim voiding."""
    request = VoidSubmissionRequest(
        claim_number='CLM123',
        action='void',
        reason='Test void'
    )
    response = await service.void_claim(request)
    assert response.status == 'voided'
```

### 2. API Tests
```python
async def test_deposit_endpoint():
    """Test deposit API endpoint."""
    response = await client.post(
        '/deposits',
        json={
            'customer_id': 1,
            'amount': '100.00',
            'payment_method': 'credit_card'
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data['status'] == 'pending'
```

### 3. UI Tests
```typescript
describe('DepositWizard', () => {
  it('completes deposit flow', async () => {
    render(<DepositWizard />);
    
    // Step 1: Welcome
    expect(screen.getByText('Welcome')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Next'));
    
    // Step 2: Customer
    await userEvent.type(
      screen.getByLabelText('Customer ID'),
      '12345'
    );
    fireEvent.click(screen.getByText('Next'));
    
    // Verify completion
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});
```
