# Calendar Module Modernization

This module provides a modern implementation of the calendar management system, replacing the legacy Windows Forms application with a FastAPI-based web service.

## Features

- Google Calendar integration
- Event creation and management
- Multiple reminder types (email, popup, SMS)
- Timezone support
- OAuth2 authentication
- Data persistence
- RESTful API endpoints

## Architecture

The module follows a clean architecture pattern with the following components:

1. Models
   - Pydantic models for data validation
   - SQLAlchemy models for persistence
   - Type definitions and validation rules

2. API Endpoints
   - RESTful endpoints using FastAPI
   - OAuth2 authentication
   - Input validation
   - Error handling

3. Services
   - Business logic implementation
   - Google Calendar integration
   - Event management
   - Reminder handling

4. Repositories
   - Data persistence layer
   - SQLAlchemy integration
   - Query optimization
   - Transaction management

5. Utilities
   - Helper functions
   - Date/time handling
   - Timezone conversion
   - Format validation

6. Security
   - OAuth2 implementation
   - Token management
   - Credential handling
   - User authentication

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Initialize database:
   ```bash
   alembic upgrade head
   ```

4. Configure Google Calendar credentials:
   - Create a project in Google Cloud Console
   - Enable Google Calendar API
   - Create OAuth2 credentials
   - Download client_secrets.json
   - Place in project root

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, view the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
pytest
```

## License

This project is licensed under the terms of the MIT license.
