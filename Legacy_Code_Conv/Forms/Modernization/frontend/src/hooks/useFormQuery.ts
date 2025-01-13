/**
 * Form query hooks.
 * 
 * This module provides React Query hooks for form operations.
 */
import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import {
  Form,
  FormCreate,
  FormUpdate,
  FormSubmission,
} from '../types/forms';
import {
  createForm,
  getForms,
  getForm,
  updateForm,
  submitForm,
  getFormSubmissions,
} from '../api/forms';


// Query keys
export const formKeys = {
  all: ['forms'] as const,
  lists: () => [...formKeys.all, 'list'] as const,
  list: (activeOnly: boolean) => [...formKeys.lists(), { activeOnly }] as const,
  details: () => [...formKeys.all, 'detail'] as const,
  detail: (id: number) => [...formKeys.details(), id] as const,
  submissions: (formId: number) => [...formKeys.detail(formId), 'submissions'] as const,
};

// Hooks
export const useFormList = (
  activeOnly = true
): UseQueryResult<Form[]> => {
  return useQuery({
    queryKey: formKeys.list(activeOnly),
    queryFn: () => getForms(activeOnly),
  });
};

export const useFormDetail = (
  id: number
): UseQueryResult<Form> => {
  return useQuery({
    queryKey: formKeys.detail(id),
    queryFn: () => getForm(id),
    enabled: !!id,
  });
};

export const useFormSubmissions = (
  formId: number
): UseQueryResult<FormSubmission[]> => {
  return useQuery({
    queryKey: formKeys.submissions(formId),
    queryFn: () => getFormSubmissions(formId),
    enabled: !!formId,
  });
};

export const useCreateForm = (): UseMutationResult<
  Form,
  Error,
  FormCreate
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createForm,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: formKeys.lists() });
      queryClient.setQueryData(formKeys.detail(data.id), data);
    },
  });
};

export const useUpdateForm = (): UseMutationResult<
  Form,
  Error,
  { id: number; data: FormUpdate }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => updateForm(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: formKeys.lists() });
      queryClient.setQueryData(formKeys.detail(data.id), data);
    },
  });
};

export const useSubmitForm = (): UseMutationResult<
  FormSubmission,
  Error,
  { formId: number; data: FormSubmission }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ formId, data }) => submitForm(formId, data),
    onSuccess: (data, { formId }) => {
      queryClient.invalidateQueries({
        queryKey: formKeys.submissions(formId),
      });
    },
  });
};
