# Tenant Management Components

## Overview
The tenant management system provides a comprehensive set of components for managing multi-tenant applications. These components handle tenant configuration, company management, and user administration within companies.

## Components

### TenantDashboard
A dashboard component that displays tenant statistics and overview information.

#### Features
- Displays tenant name and subscription tier
- Shows company count
- Displays active user count and total user count
- Shows storage usage statistics

#### Usage
```tsx
import { TenantDashboard } from '@/components/tenant/TenantDashboard'

function DashboardPage() {
  return <TenantDashboard />
}
```

### CompanyManager
A component for managing companies within a tenant.

#### Features
- List all companies
- Create new companies
- Edit existing companies
- Delete companies
- Pagination support

#### Usage
```tsx
import { CompanyManager } from '@/components/tenant/CompanyManager'

function CompaniesPage() {
  return <CompanyManager />
}
```

### CompanySettings
A component for managing company-specific settings and features.

#### Features
- Company branding configuration
- Theme selection
- Language preferences
- Timezone settings
- Feature toggles
- Custom branding options
- API access management
- Audit logging configuration

#### Usage
```tsx
import { CompanySettings } from '@/components/tenant/CompanySettings'

function CompanySettingsPage({ company }) {
  return <CompanySettings company={company} />
}
```

### CompanyUsers
A component for managing users within a company.

#### Features
- User listing
- User invitation
- Role management
- Department assignment
- User status management
- Bulk actions

#### Usage
```tsx
import { CompanyUsers } from '@/components/tenant/CompanyUsers'

function CompanyUsersPage({ companyId }) {
  return <CompanyUsers companyId={companyId} />
}
```

## API Integration

### Tenant API
The components integrate with the following tenant management endpoints:

- `GET /api/v1/tenants/me` - Get current tenant information
- `PUT /api/v1/tenants/me` - Update tenant settings
- `GET /api/v1/tenants/me/stats` - Get tenant statistics

### Company API
Company management endpoints:

- `GET /api/v1/tenants/me/companies` - List companies
- `POST /api/v1/tenants/me/companies` - Create company
- `PUT /api/v1/tenants/me/companies/{id}` - Update company
- `DELETE /api/v1/tenants/me/companies/{id}` - Delete company

### User API
User management endpoints:

- `GET /api/v1/companies/{id}/users` - List users
- `POST /api/v1/companies/{id}/users` - Invite user
- `PUT /api/v1/companies/{id}/users/{userId}/status` - Update user status

## Testing

### Unit Tests
Each component has corresponding unit tests in the `__tests__` directory:

- `TenantDashboard.test.tsx`
- `CompanyManager.test.tsx`
- `CompanySettings.test.tsx`
- `CompanyUsers.test.tsx`

### E2E Tests
End-to-end tests are available in `tests/e2e/test_tenant_management.py`

## Performance Considerations

1. **Data Fetching**
   - Uses TanStack Query for efficient data fetching and caching
   - Implements pagination for large datasets
   - Optimistic updates for better user experience

2. **Component Optimization**
   - Lazy loading of complex components
   - Memoization of expensive computations
   - Virtual scrolling for long lists

3. **State Management**
   - Local state for UI-specific data
   - Server state managed by TanStack Query
   - Efficient form state management with React Hook Form

## Security Considerations

1. **Authentication**
   - All API requests require valid JWT tokens
   - Token refresh handling
   - Session management

2. **Authorization**
   - Role-based access control
   - Feature-based permissions
   - Company-specific access restrictions

3. **Data Protection**
   - Input validation and sanitization
   - XSS prevention
   - CSRF protection

## Error Handling

1. **API Errors**
   - Consistent error message format
   - Retry logic for transient failures
   - Fallback UI states

2. **Form Validation**
   - Client-side validation with Zod
   - Server-side validation
   - Meaningful error messages

3. **Edge Cases**
   - Empty state handling
   - Loading state management
   - Error boundary implementation
