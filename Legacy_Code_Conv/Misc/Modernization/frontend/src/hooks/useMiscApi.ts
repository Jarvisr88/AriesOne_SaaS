/**
 * Custom hooks for the Misc module API
 */
import { useState, useCallback } from 'react';
import { depositsApi, voidsApi, purchaseOrdersApi } from '../api/misc';
import {
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

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

interface ApiHook<T> extends ApiState<T> {
  reset: () => void;
}

// Deposits hooks
export const useCreateDeposit = () => {
  const [state, setState] = useState<ApiState<Deposit>>({
    data: null,
    loading: false,
    error: null
  });

  const createDeposit = useCallback(
    async (deposit: DepositCreate) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await depositsApi.create(deposit);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, createDeposit, reset };
};

export const useUpdateDeposit = (id: number) => {
  const [state, setState] = useState<ApiState<Deposit>>({
    data: null,
    loading: false,
    error: null
  });

  const updateDeposit = useCallback(
    async (deposit: DepositUpdate) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await depositsApi.update(id, deposit);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    [id]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, updateDeposit, reset };
};

// Voids hooks
export const useCreateVoid = () => {
  const [state, setState] = useState<ApiState<Void>>({
    data: null,
    loading: false,
    error: null
  });

  const createVoid = useCallback(
    async (voidRequest: VoidCreate) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await voidsApi.create(voidRequest);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, createVoid, reset };
};

export const useUpdateVoid = (id: number) => {
  const [state, setState] = useState<ApiState<Void>>({
    data: null,
    loading: false,
    error: null
  });

  const updateVoid = useCallback(
    async (voidUpdate: VoidUpdate) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await voidsApi.update(id, voidUpdate);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    [id]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, updateVoid, reset };
};

// Purchase Orders hooks
export const useCreatePurchaseOrder = () => {
  const [state, setState] = useState<ApiState<PurchaseOrder>>({
    data: null,
    loading: false,
    error: null
  });

  const createPurchaseOrder = useCallback(
    async (order: PurchaseOrderCreate) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await purchaseOrdersApi.create(order);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, createPurchaseOrder, reset };
};

export const useUpdatePurchaseOrder = (id: number) => {
  const [state, setState] = useState<ApiState<PurchaseOrder>>({
    data: null,
    loading: false,
    error: null
  });

  const updatePurchaseOrder = useCallback(
    async (order: PurchaseOrderUpdate) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await purchaseOrdersApi.update(id, order);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    [id]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, updatePurchaseOrder, reset };
};

export const useReceivePurchaseOrder = (id: number) => {
  const [state, setState] = useState<ApiState<PurchaseOrder>>({
    data: null,
    loading: false,
    error: null
  });

  const receivePurchaseOrder = useCallback(
    async (items: string[]) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await purchaseOrdersApi.receive(id, items);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error as ApiError
        });
        throw error;
      }
    },
    [id]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, receivePurchaseOrder, reset };
};
