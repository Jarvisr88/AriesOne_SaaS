# Billing API Documentation

## Overview
The Billing API provides endpoints for managing invoices, rental billing, payments, and insurance claims in the AriesOne SaaS application.

## Base URL
All endpoints are prefixed with `/billing`

## Authentication
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Invoices

#### Create Invoice
```http
POST /invoices
```

Creates a new invoice with line items.

**Request Body:**
```json
{
  "document_number": "string",
  "document_type": "Invoice",
  "document_date": "2025-01-12",
  "customer_id": "integer",
  "order_id": "integer",
  "subtotal": "decimal",
  "tax_amount": "decimal",
  "discount_amount": "decimal",
  "total_amount": "decimal",
  "insurance_id": "integer (optional)",
  "authorization_number": "string (optional)",
  "internal_notes": "string (optional)",
  "customer_notes": "string (optional)",
  "items": [
    {
      "item_id": "integer",
      "quantity": "integer",
      "unit_price": "decimal",
      "tax_rate": "decimal",
      "tax_amount": "decimal",
      "discount_amount": "decimal",
      "total_amount": "decimal",
      "hcpcs_code": "string (optional)",
      "diagnosis_code": "string (optional)",
      "insurance_amount": "decimal",
      "patient_amount": "decimal"
    }
  ]
}
```

**Response:** Invoice object with created ID

#### Get Invoice
```http
GET /invoices/{invoice_id}
```

Retrieves a specific invoice by ID.

**Parameters:**
- `invoice_id`: Invoice ID (path parameter)

**Response:** Complete invoice object with items

#### List Invoices
```http
GET /invoices
```

Retrieves a list of invoices with optional filtering.

**Query Parameters:**
- `customer_id`: Filter by customer (optional)
- `status`: Filter by status (optional)
- `start_date`: Filter by start date (optional)
- `end_date`: Filter by end date (optional)
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)

**Response:** Array of invoice objects

#### Update Invoice
```http
PATCH /invoices/{invoice_id}
```

Updates an existing invoice.

**Parameters:**
- `invoice_id`: Invoice ID (path parameter)

**Request Body:**
```json
{
  "status": "string (optional)",
  "due_date": "date (optional)",
  "payment_terms": "string (optional)",
  "insurance_id": "integer (optional)",
  "authorization_number": "string (optional)",
  "internal_notes": "string (optional)",
  "customer_notes": "string (optional)"
}
```

**Response:** Updated invoice object

### Rental Invoices

#### Create Rental Invoice
```http
POST /rental-invoices
```

Creates a new rental invoice.

**Request Body:**
```json
{
  "document_number": "string",
  "document_type": "RentalInvoice",
  "document_date": "2025-01-12",
  "customer_id": "integer",
  "order_id": "integer",
  "subtotal": "decimal",
  "tax_amount": "decimal",
  "total_amount": "decimal",
  "rental_period_start": "date",
  "rental_period_end": "date",
  "recurring_frequency": "string",
  "next_bill_date": "date (optional)",
  "coverage_start": "date (optional)",
  "coverage_end": "date (optional)",
  "items": [
    {
      "item_id": "integer",
      "serial_number_id": "integer (optional)",
      "rental_start": "date",
      "rental_end": "date",
      "rental_rate": "decimal",
      "quantity": "integer",
      "tax_rate": "decimal",
      "tax_amount": "decimal",
      "total_amount": "decimal",
      "hcpcs_code": "string (optional)",
      "diagnosis_code": "string (optional)"
    }
  ]
}
```

**Response:** Rental invoice object with created ID

#### Get Rental Invoice
```http
GET /rental-invoices/{invoice_id}
```

Retrieves a specific rental invoice.

**Parameters:**
- `invoice_id`: Rental Invoice ID (path parameter)

**Response:** Complete rental invoice object with items

#### Update Rental Invoice
```http
PATCH /rental-invoices/{invoice_id}
```

Updates an existing rental invoice.

**Parameters:**
- `invoice_id`: Rental Invoice ID (path parameter)

**Request Body:**
```json
{
  "status": "string (optional)",
  "rental_period_end": "date (optional)",
  "next_bill_date": "date (optional)",
  "coverage_end": "date (optional)",
  "insurance_id": "integer (optional)",
  "authorization_number": "string (optional)"
}
```

**Response:** Updated rental invoice object

### Payments

#### Create Payment
```http
POST /payments
```

Creates a new payment.

**Request Body:**
```json
{
  "payment_number": "string",
  "payment_date": "2025-01-12",
  "payment_method": "string",
  "customer_id": "integer",
  "invoice_id": "integer (optional)",
  "rental_invoice_id": "integer (optional)",
  "amount": "decimal",
  "reference_number": "string (optional)",
  "authorization_code": "string (optional)",
  "payment_gateway_id": "string (optional)",
  "notes": "string (optional)"
}
```

**Response:** Payment object with created ID

#### Get Payment
```http
GET /payments/{payment_id}
```

Retrieves a specific payment.

**Parameters:**
- `payment_id`: Payment ID (path parameter)

**Response:** Complete payment object

#### Update Payment
```http
PATCH /payments/{payment_id}
```

Updates an existing payment.

**Parameters:**
- `payment_id`: Payment ID (path parameter)

**Request Body:**
```json
{
  "status": "string (optional)",
  "authorization_code": "string (optional)",
  "payment_gateway_id": "string (optional)",
  "notes": "string (optional)"
}
```

**Response:** Updated payment object

### Insurance Claims

#### Create Claim
```http
POST /claims
```

Creates a new insurance claim.

**Request Body:**
```json
{
  "document_number": "string",
  "document_type": "Claim",
  "document_date": "2025-01-12",
  "customer_id": "integer",
  "claim_number": "string",
  "payer_id": "integer",
  "subscriber_id": "string (optional)",
  "group_number": "string (optional)",
  "service_start_date": "date (optional)",
  "service_end_date": "date (optional)",
  "place_of_service": "string (optional)",
  "items": [
    {
      "service_date": "date",
      "hcpcs_code": "string",
      "diagnosis_code": "string (optional)",
      "modifier_1": "string (optional)",
      "modifier_2": "string (optional)",
      "modifier_3": "string (optional)",
      "modifier_4": "string (optional)",
      "quantity": "integer",
      "charge_amount": "decimal"
    }
  ]
}
```

**Response:** Claim object with created ID

#### Get Claim
```http
GET /claims/{claim_id}
```

Retrieves a specific claim.

**Parameters:**
- `claim_id`: Claim ID (path parameter)

**Response:** Complete claim object with items

#### List Claims
```http
GET /claims
```

Retrieves a list of claims with optional filtering.

**Query Parameters:**
- `customer_id`: Filter by customer (optional)
- `payer_id`: Filter by insurance payer (optional)
- `status`: Filter by status (optional)
- `start_date`: Filter by start date (optional)
- `end_date`: Filter by end date (optional)
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)

**Response:** Array of claim objects

#### Update Claim
```http
PATCH /claims/{claim_id}
```

Updates an existing claim.

**Parameters:**
- `claim_id`: Claim ID (path parameter)

**Request Body:**
```json
{
  "claim_status": "string (optional)",
  "payer_claim_number": "string (optional)",
  "adjudication_date": "date (optional)",
  "paid_amount": "decimal (optional)",
  "denied_amount": "decimal (optional)",
  "adjustment_amount": "decimal (optional)",
  "patient_responsibility": "decimal (optional)"
}
```

**Response:** Updated claim object

## Status Codes

The API returns the following status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Error Responses

Error responses follow this format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Data Types

- `string`: Text value
- `integer`: Whole number
- `decimal`: Decimal number with 2 decimal places
- `date`: ISO 8601 date format (YYYY-MM-DD)
- `boolean`: true/false value

## Enums

### DocumentStatus
- `Draft`
- `Pending`
- `Submitted`
- `Paid`
- `Partial`
- `Void`

### PaymentMethod
- `Cash`
- `Check`
- `CreditCard`
- `ACH`
- `Insurance`

### PaymentStatus
- `Pending`
- `Authorized`
- `Completed`
- `Failed`
- `Refunded`
- `Voided`

### ClaimStatus
- `Draft`
- `Ready`
- `Submitted`
- `Accepted`
- `Rejected`
- `Paid`
- `Denied`
