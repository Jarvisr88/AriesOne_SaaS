# Controls Modernization

This module provides modernized implementations of the legacy DMEWorks Controls components, including address management, name handling, and map integration services.

## Features

- Address management with validation and standardization
- Name handling with formatting and parsing
- Map provider integration with multiple provider support
- RESTful API endpoints
- Async/await support
- Type safety with Pydantic models
- SQLAlchemy ORM integration
- Comprehensive validation utilities

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Components

### Models

- `address_model.py`: Address data structures and validation
- `name_model.py`: Name data structures and validation
- `map_model.py`: Map provider integration models

### API Endpoints

- `address_endpoints.py`: Address management endpoints
- `name_endpoints.py`: Name management endpoints

### Services

- `address_service.py`: Address business logic
- `name_service.py`: Name business logic
- `map_service.py`: Map provider integration

### Repositories

- `address_repository.py`: Address data access
- `name_repository.py`: Name data access
- `base.py`: Base repository functionality

### Utilities

- `validation.py`: Common validation functions

## Usage

### Address Management

```python
from models.address_model import Address
from services.address_service import AddressService

# Create address
address = Address(
    address_line1="123 Main St",
    city="San Francisco",
    state="CA",
    zip_code="94105"
)

# Validate and standardize
validated = await address_service.validate_address(address)
```

### Name Management

```python
from models.name_model import Name
from services.name_service import NameService

# Create name
name = Name(
    first_name="John",
    last_name="Smith",
    middle_initial="A"
)

# Format name
formatted = await name_service.format_name(name, format_type="formal")
```

### Map Integration

```python
from services.map_service import MapService
from models.map_model import MapProvider

# Configure providers
config = {
    MapProvider.GOOGLE: MapProviderConfig(
        provider=MapProvider.GOOGLE,
        api_key="your-api-key",
        base_url="https://maps.googleapis.com/maps/api/"
    )
}

# Create service
map_service = MapService(config)

# Geocode address
result = await map_service.geocode_address(address)
```

## API Documentation

### Address Endpoints

- `POST /api/v1/address/validate`: Validate address
- `POST /api/v1/address/search`: Search addresses
- `POST /api/v1/address/geocode`: Geocode address
- `POST /api/v1/address/reverse-geocode`: Reverse geocode coordinates

### Name Endpoints

- `POST /api/v1/name/validate`: Validate name
- `GET /api/v1/name/courtesy-titles`: Get courtesy titles
- `POST /api/v1/name/format`: Format name
- `POST /api/v1/name/parse`: Parse name string

## Development

1. Run tests:
```bash
pytest
```

2. Format code:
```bash
black .
isort .
```

3. Type checking:
```bash
mypy .
```

4. Linting:
```bash
flake8
```

## Database Migrations

1. Create migration:
```bash
alembic revision --autogenerate -m "description"
```

2. Apply migrations:
```bash
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
