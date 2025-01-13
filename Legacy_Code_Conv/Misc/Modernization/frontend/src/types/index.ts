/**
 * Common types for the Misc module
 */

// Deposit types
export interface Deposit {
  id: number;
  amount: number;
  paymentMethod: string;
  customerId: number;
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface DepositCreate {
  amount: number;
  paymentMethod: string;
  customerId: number;
}

export interface DepositUpdate {
  amount?: number;
  paymentMethod?: string;
  status?: 'pending' | 'completed' | 'failed';
}

// Void types
export interface Void {
  id: number;
  reason: string;
  amount: number;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  approvedBy?: string;
}

export interface VoidCreate {
  reason: string;
  amount: number;
}

export interface VoidUpdate {
  reason?: string;
  status?: 'pending' | 'approved' | 'rejected';
}

// Purchase Order types
export interface PurchaseOrderItem {
  id: number;
  name: string;
  quantity: number;
  price: number;
  total: number;
}

export interface PurchaseOrder {
  id: number;
  vendorId: number;
  items: PurchaseOrderItem[];
  status: 'draft' | 'submitted' | 'approved' | 'received';
  total: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  approvedBy?: string;
}

export interface PurchaseOrderCreate {
  vendorId: number;
  items: Omit<PurchaseOrderItem, 'id'>[];
}

export interface PurchaseOrderUpdate {
  items?: Omit<PurchaseOrderItem, 'id'>[];
  status?: 'draft' | 'submitted' | 'approved' | 'received';
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Auth types
export interface User {
  username: string;
  email: string;
  role: string;
  permissions: string[];
}

// Form validation types
export type ValidationError = {
  field: string;
  message: string;
}

export type FormErrors = Record<string, string>;
