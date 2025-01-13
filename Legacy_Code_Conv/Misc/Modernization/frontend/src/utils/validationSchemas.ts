/**
 * Zod validation schemas for forms
 */
import { z } from 'zod';

// Common schemas
const moneySchema = z.number().min(0.01, 'Amount must be greater than 0');
const idSchema = z.number().int().positive('ID must be a positive number');

// Deposit schemas
export const depositCreateSchema = z.object({
  amount: moneySchema,
  paymentMethod: z.enum(['cash', 'check', 'credit', 'debit', 'transfer'], {
    required_error: 'Payment method is required'
  }),
  customerId: idSchema,
  notes: z.string().optional(),
  referenceNumber: z.string().optional()
});

export const depositUpdateSchema = depositCreateSchema.partial();

// Void schemas
export const voidCreateSchema = z.object({
  amount: moneySchema,
  reason: z.string()
    .min(10, 'Reason must be at least 10 characters')
    .max(500, 'Reason must not exceed 500 characters'),
  transactionId: z.string().optional(),
  notes: z.string().optional()
});

export const voidUpdateSchema = voidCreateSchema.partial();

// Purchase Order schemas
const purchaseOrderItemSchema = z.object({
  name: z.string().min(1, 'Item name is required'),
  quantity: z.number()
    .int()
    .min(1, 'Quantity must be at least 1'),
  price: moneySchema,
  notes: z.string().optional()
});

export const purchaseOrderCreateSchema = z.object({
  vendorId: idSchema,
  items: z.array(purchaseOrderItemSchema)
    .min(1, 'At least one item is required'),
  notes: z.string().optional()
});

export const purchaseOrderUpdateSchema = purchaseOrderCreateSchema.partial();

export const purchaseOrderReceiveSchema = z.object({
  items: z.array(z.object({
    id: idSchema,
    received: z.boolean(),
    notes: z.string().optional()
  }))
});

// Login schema
export const loginSchema = z.object({
  email: z.string()
    .email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
});

// Error formatting
export const formatZodError = (error: z.ZodError) => {
  const formattedErrors: Record<string, string> = {};
  
  error.errors.forEach((err) => {
    const path = err.path.join('.');
    formattedErrors[path] = err.message;
  });

  return formattedErrors;
};
