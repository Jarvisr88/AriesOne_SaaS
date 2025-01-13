/**
 * Form query hooks tests.
 */
import { renderHook, act } from '@testing-library/react-hooks';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useFormList,
  useFormDetail,
  useCreateForm,
  useUpdateForm,
} from '../../hooks/useFormQuery';
import {
  getForms,
  getForm,
  createForm,
  updateForm,
} from '../../api/forms';


// Mock API functions
jest.mock('../../api/forms', () => ({
  getForms: jest.fn(),
  getForm: jest.fn(),
  createForm: jest.fn(),
  updateForm: jest.fn(),
}));

describe('useFormQuery', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });
  
  afterEach(() => {
    jest.clearAllMocks();
  });
  
  describe('useFormList', () => {
    it('fetches forms successfully', async () => {
      const mockForms = [
        { id: 1, name: 'Form 1' },
        { id: 2, name: 'Form 2' },
      ];
      
      (getForms as jest.Mock).mockResolvedValueOnce(mockForms);
      
      const { result, waitFor } = renderHook(
        () => useFormList(),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );
      
      await waitFor(() => result.current.isSuccess);
      
      expect(result.current.data).toEqual(mockForms);
    });
    
    it('handles error state', async () => {
      const error = new Error('Failed to fetch');
      (getForms as jest.Mock).mockRejectedValueOnce(error);
      
      const { result, waitFor } = renderHook(
        () => useFormList(),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );
      
      await waitFor(() => result.current.isError);
      
      expect(result.current.error).toBe(error);
    });
  });
  
  describe('useFormDetail', () => {
    it('fetches form detail successfully', async () => {
      const mockForm = {
        id: 1,
        name: 'Form 1',
        schema: { fields: [] },
      };
      
      (getForm as jest.Mock).mockResolvedValueOnce(mockForm);
      
      const { result, waitFor } = renderHook(
        () => useFormDetail(1),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );
      
      await waitFor(() => result.current.isSuccess);
      
      expect(result.current.data).toEqual(mockForm);
    });
  });
  
  describe('useCreateForm', () => {
    it('creates form successfully', async () => {
      const newForm = {
        name: 'New Form',
        schema: { fields: [] },
      };
      
      const createdForm = {
        id: 1,
        ...newForm,
      };
      
      (createForm as jest.Mock).mockResolvedValueOnce(createdForm);
      
      const { result, waitFor } = renderHook(
        () => useCreateForm(),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );
      
      act(() => {
        result.current.mutate(newForm);
      });
      
      await waitFor(() => result.current.isSuccess);
      
      expect(result.current.data).toEqual(createdForm);
    });
  });
  
  describe('useUpdateForm', () => {
    it('updates form successfully', async () => {
      const formUpdate = {
        id: 1,
        data: {
          name: 'Updated Form',
        },
      };
      
      const updatedForm = {
        id: 1,
        name: 'Updated Form',
        schema: { fields: [] },
      };
      
      (updateForm as jest.Mock).mockResolvedValueOnce(updatedForm);
      
      const { result, waitFor } = renderHook(
        () => useUpdateForm(),
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        }
      );
      
      act(() => {
        result.current.mutate(formUpdate);
      });
      
      await waitFor(() => result.current.isSuccess);
      
      expect(result.current.data).toEqual(updatedForm);
    });
  });
});
