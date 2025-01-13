# Reports Transformation Rules

## Overview
This document defines the transformation rules for converting the legacy Reports components to a modern web-based system using FastAPI and React.

## Component Mapping

### 1. Report Base Class
```python
# Legacy
public class Report
{
    public string FileName { get; set; }
    public bool IsSystem { get; set; }
    public string Name { get; set; }
    public string Category { get; set; }
}

# Modern
class Report(BaseModel):
    """Report base model."""
    id: int
    name: str
    category: str
    file_name: str
    is_system: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    version: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True
```

### 2. Custom Report
```python
# Legacy
public class CustomReport
{
    [XmlAttribute]
    public string FileName { get; set; }
    
    [XmlIgnore]
    public bool IsDeleted { get; set; }
    
    [XmlAttribute]
    public string Category { get; set; }
    
    [XmlText]
    public string Name { get; set; }
}

# Modern
class CustomReport(Report):
    """Custom report model."""
    template_id: Optional[int]
    parameters: Dict[str, Any]
    is_deleted: bool = False
    deleted_at: Optional[datetime]
    deleted_by: Optional[int]
    
    class Config:
        """Pydantic config."""
        orm_mode = True
```

### 3. Default Report
```python
# Legacy
public class DefaultReport
{
    [XmlAttribute]
    public string FileName { get; set; }
    
    [XmlIgnore]
    public bool IsSystem { get; set; }
    
    [XmlAttribute]
    public string Category { get; set; }
    
    [XmlText]
    public string Name { get; set; }
}

# Modern
class ReportTemplate(BaseModel):
    """Report template model."""
    id: int
    name: str
    category: str
    file_name: str
    is_system: bool
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    version: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True
```

### 4. Data Source Reports
```python
# Legacy
public class DataSourceReports
{
    private readonly string _customFileName;
    private readonly string _defaultFileName;
    private Dictionary<string, Pair> _dictionary;
    private Report[] _reports;
    
    public void DeleteByFilename(params string[] filenames)
    {
        // Delete implementation
    }
    
    public IEnumerable<Report> Select()
    {
        // Select implementation
    }
}

# Modern
class ReportService:
    """Report service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.session = session
        self.cache = ReportCache()
    
    async def get_reports(
        self,
        category: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Report]:
        """Get all reports."""
        query = select(Report)
        if category:
            query = query.where(Report.category == category)
        if not include_deleted:
            query = query.where(Report.is_deleted.is_(False))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def delete_reports(
        self,
        file_names: List[str],
        user_id: int
    ) -> None:
        """Delete reports by file names."""
        query = (
            update(Report)
            .where(Report.file_name.in_(file_names))
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow(),
                deleted_by=user_id
            )
        )
        await self.session.execute(query)
        await self.session.commit()
```

## Models

### 1. Database Models
```python
class Report(Base):
    """Report model."""
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(200))
    is_system: Mapped[bool] = mapped_column(default=False)
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("report_templates.id"),
        nullable=True
    )
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(default=1)


class ReportTemplate(Base):
    """Report template model."""
    __tablename__ = "report_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(200))
    is_system: Mapped[bool] = mapped_column(default=False)
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(default=1)
```

## Validation Rules

### 1. Report Validation
```python
def validate_report(report: Report) -> None:
    """Validate report."""
    if not report.name:
        raise ValueError("Report name is required")
        
    if not report.category:
        raise ValueError("Report category is required")
        
    if not report.file_name:
        raise ValueError("Report file name is required")
        
    if not re.match(r'^[A-Za-z0-9_\-\.]+$', report.file_name):
        raise ValueError("Invalid file name format")


def validate_parameters(parameters: Dict[str, Any]) -> None:
    """Validate report parameters."""
    for key, value in parameters.items():
        if not re.match(r'^[A-Za-z0-9_]+$', key):
            raise ValueError(f"Invalid parameter name: {key}")
            
        if not isinstance(value, (str, int, float, bool, dict, list)):
            raise ValueError(
                f"Invalid parameter type for {key}: {type(value)}"
            )
```

## Security Rules

### 1. Access Control
```python
def verify_report_access(
    user: User,
    report: Report,
    action: str
) -> bool:
    """Verify user has access to report."""
    if action == "view":
        return user.has_permission("reports.view")
        
    if action == "create":
        return user.has_permission("reports.create")
        
    if action == "edit":
        return (
            user.has_permission("reports.edit") and
            not report.is_system
        )
        
    if action == "delete":
        return (
            user.has_permission("reports.delete") and
            not report.is_system
        )
        
    return False


def verify_template_access(
    user: User,
    template: ReportTemplate,
    action: str
) -> bool:
    """Verify user has access to template."""
    if action == "view":
        return user.has_permission("templates.view")
        
    if action == "create":
        return user.has_permission("templates.create")
        
    if action == "edit":
        return (
            user.has_permission("templates.edit") and
            not template.is_system
        )
        
    if action == "delete":
        return (
            user.has_permission("templates.delete") and
            not template.is_system
        )
        
    return False
```

## Testing Rules

### 1. Service Tests
```python
@pytest.mark.asyncio
async def test_report_crud():
    """Test report CRUD operations."""
    service = ReportService(session)
    
    # Create
    report = await service.create_report(
        name="Test Report",
        category="Test",
        file_name="test.rpt",
        user_id=1
    )
    assert report.name == "Test Report"
    
    # Read
    found = await service.get_report(report.id)
    assert found.name == "Test Report"
    
    # Update
    updated = await service.update_report(
        report.id,
        name="Updated Report",
        user_id=1
    )
    assert updated.name == "Updated Report"
    
    # Delete
    await service.delete_report(report.id, user_id=1)
    deleted = await service.get_report(report.id)
    assert deleted.is_deleted
```

### 2. API Tests
```python
async def test_report_endpoints():
    """Test report API."""
    # Create report
    response = await client.post(
        "/reports",
        json={
            "name": "Test Report",
            "category": "Test",
            "file_name": "test.rpt"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Get report
    response = await client.get(f"/reports/{data['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Report"
    
    # Update report
    response = await client.put(
        f"/reports/{data['id']}",
        json={"name": "Updated Report"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Report"
    
    # Delete report
    response = await client.delete(f"/reports/{data['id']}")
    assert response.status_code == 200
```

### 3. UI Tests
```typescript
describe('ReportList', () => {
  it('displays reports', async () => {
    render(<ReportList />);
    
    const reports = await screen.findAllByRole('listitem');
    expect(reports).toHaveLength(2);
  });
  
  it('filters by category', async () => {
    render(<ReportList />);
    
    const filter = screen.getByLabelText('Category');
    await userEvent.selectOptions(filter, 'Test');
    
    const reports = await screen.findAllByRole('listitem');
    expect(reports).toHaveLength(1);
  });
  
  it('handles report deletion', async () => {
    render(<ReportList />);
    
    const deleteButton = screen.getByRole('button', {
      name: /delete/i
    });
    await userEvent.click(deleteButton);
    
    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    
    const confirmButton = within(dialog).getByRole('button', {
      name: /confirm/i
    });
    await userEvent.click(confirmButton);
    
    const reports = await screen.findAllByRole('listitem');
    expect(reports).toHaveLength(1);
  });
});
