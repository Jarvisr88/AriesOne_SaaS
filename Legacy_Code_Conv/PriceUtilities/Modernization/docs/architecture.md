# Price Utilities SaaS Architecture Documentation

## Overview
The Price Utilities SaaS is a modern, scalable application designed to handle complex pricing calculations and updates for healthcare equipment. This document outlines the technical architecture, components, and design decisions.

## System Architecture

### Backend Architecture
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: OAuth2 with JWT
- **API Version**: v1

#### Core Services
1. **Price Calculation Service**
   - Handles complex price calculations
   - Supports quantity-based discounts
   - Processes ICD code modifiers
   - Applies dynamic parameters

2. **Validation Service**
   - Validates price updates
   - Ensures data integrity
   - Handles business rule validation
   - Manages constraint checking

3. **Update Processing Service**
   - Processes single price updates
   - Handles bulk price updates
   - Manages effective dates
   - Maintains audit trail

4. **Audit Service**
   - Tracks all price changes
   - Records user actions
   - Maintains change history
   - Supports compliance requirements

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **State Management**: TanStack Query
- **UI Components**: shadcn/ui
- **Form Handling**: React Hook Form with Zod

#### Key Components
1. **PriceEditor**
   - Single price update interface
   - Real-time validation
   - Dynamic calculations
   - Error handling

2. **BulkUpdateInterface**
   - File upload support
   - Progress tracking
   - Error reporting
   - Batch processing

3. **ICDCodeManager**
   - ICD code management
   - Code validation
   - Modifier management
   - Search functionality

4. **ParameterEditor**
   - Parameter configuration
   - Dynamic updates
   - Validation rules
   - Effective date management

## Data Flow

### Price Update Flow
1. User initiates price update
2. Frontend validates input
3. Backend validates request
4. Price calculation service processes update
5. Database updated with new price
6. Audit record created
7. Success/failure response returned

### Bulk Update Flow
1. User uploads spreadsheet
2. Frontend validates format
3. Backend processes records
4. Updates applied in transaction
5. Audit records created
6. Progress reported to user
7. Final summary displayed

## Security

### Authentication
- OAuth2 implementation
- JWT token-based
- Role-based access control
- Token refresh mechanism

### Data Protection
- Input sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

## Performance Considerations

### Optimization Techniques
- Query optimization
- Caching strategy
- Bulk operation handling
- Pagination implementation

### Scalability
- Horizontal scaling support
- Load balancing ready
- Database indexing
- Connection pooling

## Error Handling

### Frontend
- Form validation
- API error handling
- User feedback
- Retry mechanisms

### Backend
- Input validation
- Business rule validation
- Exception handling
- Error logging

## Monitoring and Logging

### Metrics
- Response times
- Error rates
- Usage patterns
- System health

### Logging
- Application logs
- Audit logs
- Error logs
- Performance metrics

## Deployment

### Requirements
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis (optional)

### Configuration
- Environment variables
- Database configuration
- API endpoints
- Security settings
