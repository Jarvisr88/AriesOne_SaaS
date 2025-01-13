# Price Utilities Transformation Rules

## Overview
This document defines the transformation rules for converting the legacy Price Utilities components to a modern web-based system using FastAPI and React.

## Component Mapping

### 1. FormPriceListEditor

#### Grid to React Component
```typescript
// Legacy
public class FormPriceListEditor : DmeForm
{
    private DataGridView grid;
    private TablePriceList F_Table;
}

// Modern
const PriceListEditor: React.FC = () => {
  const [data, setData] = useState<PriceItem[]>([]);
  const [selectedList, setSelectedList] = useState<string>();
  
  return (
    <DataGrid
      rows={data}
      columns={[
        { field: 'billingCode', headerName: 'Billing Code' },
        { field: 'rentAllowable', headerName: 'Rent Allowable' },
        { field: 'rentBillable', headerName: 'Rent Billable' },
        { field: 'saleAllowable', headerName: 'Sale Allowable' },
        { field: 'saleBillable', headerName: 'Sale Billable' }
      ]}
      editable
      onEditCommit={handleEdit}
    />
  );
};
```

#### Price List Models
```python
class PriceItem(BaseModel):
    """Price item model."""
    id: int
    list_id: int
    billing_code: str
    rent_allowable: Decimal
    rent_billable: Decimal
    sale_allowable: Decimal
    sale_billable: Decimal
    
    @validator('billing_code')
    def validate_code(cls, v):
        if not re.match(r'^[A-Z0-9]{5,10}$', v):
            raise ValueError("Invalid billing code format")
        return v

class PriceListUpdate(BaseModel):
    """Price list update model."""
    items: List[PriceItem]
    update_orders: bool = False
    reason: Optional[str]
```

### 2. FormPriceUpdater

#### File Upload Component
```typescript
// Legacy
private void btnChooseCVS_Click(object sender, EventArgs e)
{
    using (OpenFileDialog dialog = new OpenFileDialog())
    {
        dialog.Filter = "Text Files (*.txt, *.csv)|*.txt;*.csv";
        // ... file handling
    }
}

// Modern
const PriceUploader: React.FC = () => {
  const onDrop = useCallback((files: File[]) => {
    const file = files[0];
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      const text = e.target?.result;
      const rows = parseCSV(text as string);
      await uploadPrices(rows);
    };
    
    reader.readAsText(file);
  }, []);
  
  return (
    <Dropzone onDrop={onDrop}>
      {({getRootProps, getInputProps}) => (
        <Box {...getRootProps()}>
          <input {...getInputProps()} accept=".csv,.txt" />
          <Typography>
            Drag & drop a price file, or click to select
          </Typography>
        </Box>
      )}
    </Dropzone>
  );
};
```

#### Update Models
```python
class PriceUpdateFile(BaseModel):
    """Price update file model."""
    filename: str
    content: str
    column_map: Dict[str, str]
    price_list: str
    update_orders: bool = False

class UpdateResult(BaseModel):
    """Update result model."""
    total_rows: int
    updated_items: int
    errors: List[str]
    warnings: List[str]
```

### 3. ICD9 Updates

#### Update Component
```typescript
// Legacy
public class FormUpdateICD9 : DmeForm
{
    private void UpdateCodes()
    {
        // ... update logic
    }
}

// Modern
const ICD9Updater: React.FC = () => {
  const [codes, setCodes] = useState<ICD9Code[]>([]);
  const [updating, setUpdating] = useState(false);
  
  const handleUpdate = async () => {
    setUpdating(true);
    try {
      const result = await api.post('/icd9-codes/update', {
        codes: codes
      });
      showSuccess('Codes updated successfully');
    } catch (error) {
      showError('Failed to update codes');
    } finally {
      setUpdating(false);
    }
  };
  
  return (
    <Box>
      <DataGrid
        rows={codes}
        columns={columns}
        checkboxSelection
        onSelectionChange={handleSelection}
      />
      <LoadingButton
        loading={updating}
        onClick={handleUpdate}
      >
        Update Selected Codes
      </LoadingButton>
    </Box>
  );
};
```

#### ICD9 Models
```python
class ICD9Code(BaseModel):
    """ICD-9 code model."""
    code: str
    description: str
    effective_date: date
    end_date: Optional[date]
    replaced_by: Optional[str]
    
    @validator('code')
    def validate_code(cls, v):
        if not re.match(r'^\d{3}(\.\d{1,2})?$', v):
            raise ValueError("Invalid ICD-9 code format")
        return v

class ICD9Update(BaseModel):
    """ICD-9 update model."""
    codes: List[ICD9Code]
    update_existing: bool = True
    track_changes: bool = True
```

## Validation Rules

### 1. Price Validation
```python
def validate_price(price: Decimal) -> None:
    """Validate price value."""
    if price < 0:
        raise ValueError("Price cannot be negative")
        
    if price.as_tuple().exponent < -2:
        raise ValueError("Price cannot have more than 2 decimal places")

def validate_price_item(item: PriceItem) -> None:
    """Validate price item."""
    validate_price(item.rent_allowable)
    validate_price(item.rent_billable)
    validate_price(item.sale_allowable)
    validate_price(item.sale_billable)
    
    if item.rent_billable > item.rent_allowable:
        raise ValueError("Rent billable cannot exceed allowable")
        
    if item.sale_billable > item.sale_allowable:
        raise ValueError("Sale billable cannot exceed allowable")
```

### 2. File Validation
```python
def validate_csv_file(content: str) -> None:
    """Validate CSV file content."""
    try:
        reader = csv.reader(StringIO(content))
        header = next(reader)
        
        required_columns = {
            'billing_code',
            'price'
        }
        
        if not required_columns.issubset(header):
            raise ValueError("Missing required columns")
            
    except csv.Error as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")
```

## Security Rules

### 1. Authentication
```python
def verify_price_access(user: User, price_list: str) -> bool:
    """Verify user has access to price list."""
    return (
        user.has_permission('prices.edit') and
        user.has_company_access(price_list)
    )

def verify_bulk_update_access(user: User) -> bool:
    """Verify user can perform bulk updates."""
    return user.has_permission('prices.bulk_update')
```

### 2. Validation
```python
def validate_update_request(
    user: User,
    request: PriceUpdateFile
) -> None:
    """Validate price update request."""
    if not verify_price_access(user, request.price_list):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
        
    if request.update_orders and not user.has_permission('orders.update'):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
```

## Testing Rules

### 1. Service Tests
```python
@pytest.mark.asyncio
async def test_price_update():
    """Test price update operation."""
    update = PriceListUpdate(
        items=[
            PriceItem(
                billing_code="A1234",
                rent_allowable=Decimal("100.00"),
                rent_billable=Decimal("90.00"),
                sale_allowable=Decimal("500.00"),
                sale_billable=Decimal("450.00")
            )
        ],
        update_orders=True
    )
    
    result = await service.update_prices(update)
    assert result.updated_items == 1
    assert len(result.errors) == 0
```

### 2. API Tests
```python
async def test_bulk_update_endpoint():
    """Test bulk update API."""
    response = await client.post(
        "/price-lists/bulk-update",
        files={
            'file': ('prices.csv', csv_content)
        },
        data={
            'price_list': 'default',
            'update_orders': 'true'
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total_rows'] > 0
```

### 3. UI Tests
```typescript
describe('PriceListEditor', () => {
  it('handles price updates', async () => {
    render(<PriceListEditor />);
    
    // Edit price
    const cell = screen.getByRole('cell', { name: '100.00' });
    fireEvent.doubleClick(cell);
    await userEvent.type(screen.getByRole('textbox'), '150.00');
    fireEvent.keyPress(screen.getByRole('textbox'), { key: 'Enter' });
    
    // Verify update
    expect(await screen.findByText('Price updated')).toBeInTheDocument();
  });
});
