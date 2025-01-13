/**
 * Company query hooks.
 * 
 * This module provides React Query hooks for company operations.
 */
import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import {
  Company,
  CompanyCreate,
  CompanyUpdate,
  CompanyForm,
  CompanyFormCreate,
  CompanyFormUpdate,
} from '../types/companies';
import {
  createCompany,
  getCompanies,
  getCompany,
  updateCompany,
  getCompanyForms,
  getCompanyForm,
  assignForm,
  updateFormSettings,
} from '../api/companies';


// Query keys
export const companyKeys = {
  all: ['companies'] as const,
  lists: () => [...companyKeys.all, 'list'] as const,
  list: (activeOnly: boolean) => [...companyKeys.lists(), { activeOnly }] as const,
  details: () => [...companyKeys.all, 'detail'] as const,
  detail: (id: number) => [...companyKeys.details(), id] as const,
  forms: (companyId: number) => [...companyKeys.detail(companyId), 'forms'] as const,
  form: (companyId: number, formId: number) => [...companyKeys.forms(companyId), formId] as const,
};

// Hooks
export const useCompanyList = (
  activeOnly = true
): UseQueryResult<Company[]> => {
  return useQuery({
    queryKey: companyKeys.list(activeOnly),
    queryFn: () => getCompanies(activeOnly),
  });
};

export const useCompanyDetail = (
  id: number
): UseQueryResult<Company> => {
  return useQuery({
    queryKey: companyKeys.detail(id),
    queryFn: () => getCompany(id),
    enabled: !!id,
  });
};

export const useCompanyForms = (
  companyId: number
): UseQueryResult<CompanyForm[]> => {
  return useQuery({
    queryKey: companyKeys.forms(companyId),
    queryFn: () => getCompanyForms(companyId),
    enabled: !!companyId,
  });
};

export const useCompanyForm = (
  companyId: number,
  formId: number
): UseQueryResult<CompanyForm> => {
  return useQuery({
    queryKey: companyKeys.form(companyId, formId),
    queryFn: () => getCompanyForm(companyId, formId),
    enabled: !!companyId && !!formId,
  });
};

export const useCreateCompany = (): UseMutationResult<
  Company,
  Error,
  CompanyCreate
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createCompany,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
      queryClient.setQueryData(companyKeys.detail(data.id), data);
    },
  });
};

export const useUpdateCompany = (): UseMutationResult<
  Company,
  Error,
  { id: number; data: CompanyUpdate }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => updateCompany(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
      queryClient.setQueryData(companyKeys.detail(data.id), data);
    },
  });
};

export const useAssignForm = (): UseMutationResult<
  CompanyForm,
  Error,
  CompanyFormCreate
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: assignForm,
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: companyKeys.forms(data.company_id),
      });
    },
  });
};

export const useUpdateCompanyForm = (): UseMutationResult<
  CompanyForm,
  Error,
  { companyId: number; formId: number; data: CompanyFormUpdate }
> => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ companyId, formId, data }) => (
      updateFormSettings(companyId, formId, data)
    ),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: companyKeys.forms(data.company_id),
      });
      queryClient.setQueryData(
        companyKeys.form(data.company_id, data.form_id),
        data
      );
    },
  });
};
