# Component Documentation

## Overview
This document provides detailed documentation for all React components in the Misc module.

## Components

### Auth Components

#### LoginForm
A form component for user authentication.

```tsx
import { LoginForm } from '../components/auth/LoginForm';

// Usage
<LoginForm />
```

Props: None

State:
- `isSubmitting`: Boolean indicating form submission state
- Form fields managed by React Hook Form

Events:
- `onSubmit`: Handles form submission with credentials
- Redirects to previous page on success
- Shows toast messages for success/error

### Deposit Components

#### DepositForm
A form component for creating and editing deposits.

```tsx
import { DepositForm } from '../components/deposits/DepositForm';

// Usage
<DepositForm onSuccess={(data) => console.log(data)} />
```

Props:
- `onSuccess`: Callback function called after successful submission
- `defaultValues`: Optional initial values for the form

Validation:
- Amount: Required, greater than 0
- Payment Method: Required, one of [cash, check, credit, debit, transfer]
- Customer ID: Required, positive integer

#### DepositList
A table component displaying a list of deposits.

```tsx
import { DepositList } from '../components/deposits/DepositList';

// Usage
<DepositList />
```

Features:
- Pagination
- Sorting by columns
- Filtering by status
- Search by reference number

### Void Components

#### VoidForm
A form component for creating void requests.

```tsx
import { VoidForm } from '../components/voids/VoidForm';

// Usage
<VoidForm onSuccess={(data) => console.log(data)} />
```

Props:
- `onSuccess`: Callback function called after successful submission
- `defaultValues`: Optional initial values for the form

Validation:
- Amount: Required, greater than 0
- Reason: Required, min 10 characters, max 500 characters
- Transaction ID: Optional string

### Purchase Order Components

#### PurchaseOrderForm
A form component for creating purchase orders.

```tsx
import { PurchaseOrderForm } from '../components/purchase-orders/PurchaseOrderForm';

// Usage
<PurchaseOrderForm onSuccess={(data) => console.log(data)} />
```

Props:
- `onSuccess`: Callback function called after successful submission
- `defaultValues`: Optional initial values for the form

Features:
- Dynamic item addition/removal
- Automatic total calculation
- Item validation

### Common Components

#### ErrorBoundary
A component that catches JavaScript errors in child components.

```tsx
import { ErrorBoundary } from '../components/common/ErrorBoundary';

// Usage
<ErrorBoundary>
  <ChildComponent />
</ErrorBoundary>
```

Props:
- `children`: React nodes to be rendered
- `fallback`: Optional custom error component

#### LoadingSpinner
A loading indicator component.

```tsx
import { LoadingSpinner } from '../components/common/LoadingSpinner';

// Usage
<LoadingSpinner message="Loading deposits..." />
```

Props:
- `message`: Optional loading message
- `size`: Optional size (sm, md, lg)

## Custom Hooks

### useAuth
Authentication hook for managing user session.

```tsx
import { useAuth } from '../hooks/useAuth';

// Usage
const { user, login, logout, hasRoles } = useAuth();
```

Returns:
- `user`: Current user object or null
- `login`: Function to handle login
- `logout`: Function to handle logout
- `hasRoles`: Function to check user roles
- `isAuthenticated`: Boolean indicating auth status

### useFormValidation
Form validation hook using Zod schemas.

```tsx
import { useFormValidation } from '../hooks/useFormValidation';

// Usage
const form = useFormValidation({
  schema: depositSchema,
  onSubmit: handleSubmit
});
```

Props:
- `schema`: Zod validation schema
- `defaultValues`: Optional initial form values
- `onSubmit`: Form submission handler

### useToastMessage
Toast notification hook.

```tsx
import { useToastMessage } from '../hooks/useToastMessage';

// Usage
const toast = useToastMessage();
toast.success('Operation completed successfully');
```

Methods:
- `success`: Show success message
- `error`: Show error message
- `warning`: Show warning message
- `info`: Show info message
