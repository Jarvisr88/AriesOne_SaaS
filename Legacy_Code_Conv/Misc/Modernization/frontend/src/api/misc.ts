/**
 * API client for the Misc module
 */
import axios, { AxiosError } from 'axios';
import {
  ApiResponse,
  ApiError,
  Deposit,
  DepositCreate,
  DepositUpdate,
  Void,
  VoidCreate,
  VoidUpdate,
  PurchaseOrder,
  PurchaseOrderCreate,
  PurchaseOrderUpdate
} from '../types';

const api = axios.create({
  baseURL: '/api/v1/misc',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Error handler
const handleError = (error: AxiosError): never => {
  const apiError: ApiError = {
    message: error.response?.data?.message || 'An error occurred',
    code: error.response?.data?.code,
    details: error.response?.data?.details
  };
  throw apiError;
};

// Deposits API
export const depositsApi = {
  create: async (deposit: DepositCreate): Promise<Deposit> => {
    try {
      const response = await api.post<ApiResponse<Deposit>>(
        '/deposits',
        deposit
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  get: async (id: number): Promise<Deposit> => {
    try {
      const response = await api.get<ApiResponse<Deposit>>(
        `/deposits/${id}`
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  update: async (
    id: number,
    deposit: DepositUpdate
  ): Promise<Deposit> => {
    try {
      const response = await api.put<ApiResponse<Deposit>>(
        `/deposits/${id}`,
        deposit
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  delete: async (id: number): Promise<void> => {
    try {
      await api.delete(`/deposits/${id}`);
    } catch (error) {
      return handleError(error as AxiosError);
    }
  }
};

// Voids API
export const voidsApi = {
  create: async (voidRequest: VoidCreate): Promise<Void> => {
    try {
      const response = await api.post<ApiResponse<Void>>(
        '/voids',
        voidRequest
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  get: async (id: number): Promise<Void> => {
    try {
      const response = await api.get<ApiResponse<Void>>(
        `/voids/${id}`
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  update: async (
    id: number,
    voidUpdate: VoidUpdate
  ): Promise<Void> => {
    try {
      const response = await api.put<ApiResponse<Void>>(
        `/voids/${id}`,
        voidUpdate
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  }
};

// Purchase Orders API
export const purchaseOrdersApi = {
  create: async (
    order: PurchaseOrderCreate
  ): Promise<PurchaseOrder> => {
    try {
      const response = await api.post<ApiResponse<PurchaseOrder>>(
        '/purchase-orders',
        order
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  get: async (id: number): Promise<PurchaseOrder> => {
    try {
      const response = await api.get<ApiResponse<PurchaseOrder>>(
        `/purchase-orders/${id}`
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  update: async (
    id: number,
    order: PurchaseOrderUpdate
  ): Promise<PurchaseOrder> => {
    try {
      const response = await api.put<ApiResponse<PurchaseOrder>>(
        `/purchase-orders/${id}`,
        order
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  },

  receive: async (
    id: number,
    items: string[]
  ): Promise<PurchaseOrder> => {
    try {
      const response = await api.post<ApiResponse<PurchaseOrder>>(
        `/purchase-orders/${id}/receive`,
        { items }
      );
      return response.data.data;
    } catch (error) {
      return handleError(error as AxiosError);
    }
  }
};
