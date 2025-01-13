import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { toast } from 'sonner'
import {
  Tenant,
  Company,
  TenantStats,
  TenantCreate,
  TenantUpdate,
  CompanyCreate,
  CompanyUpdate
} from '@/types/tenant'

const API_URL = '/api/v1'

// Tenant Queries
export const useCurrentTenant = () => {
  return useQuery({
    queryKey: ['tenant'],
    queryFn: async () => {
      const { data } = await axios.get<Tenant>(`${API_URL}/tenants/me`)
      return data
    }
  })
}

export const useTenantStats = () => {
  return useQuery({
    queryKey: ['tenant', 'stats'],
    queryFn: async () => {
      const { data } = await axios.get<TenantStats>(`${API_URL}/tenants/me/stats`)
      return data
    }
  })
}

export const useUpdateTenant = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (updateData: TenantUpdate) => {
      const { data } = await axios.put<Tenant>(`${API_URL}/tenants/me`, updateData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant'] })
      toast.success('Tenant updated successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to update tenant: ${error.message}`)
    }
  })
}

// Company Queries
export const useCompanies = (page = 1, limit = 10) => {
  return useQuery({
    queryKey: ['companies', page, limit],
    queryFn: async () => {
      const { data } = await axios.get<Company[]>(
        `${API_URL}/tenants/me/companies?skip=${(page - 1) * limit}&limit=${limit}`
      )
      return data
    }
  })
}

export const useCompany = (companyId: number) => {
  return useQuery({
    queryKey: ['companies', companyId],
    queryFn: async () => {
      const { data } = await axios.get<Company>(
        `${API_URL}/tenants/me/companies/${companyId}`
      )
      return data
    },
    enabled: !!companyId
  })
}

export const useCreateCompany = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (companyData: CompanyCreate) => {
      const { data } = await axios.post<Company>(
        `${API_URL}/tenants/me/companies`,
        companyData
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      toast.success('Company created successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to create company: ${error.message}`)
    }
  })
}

export const useUpdateCompany = (companyId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (updateData: CompanyUpdate) => {
      const { data } = await axios.put<Company>(
        `${API_URL}/tenants/me/companies/${companyId}`,
        updateData
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      toast.success('Company updated successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to update company: ${error.message}`)
    }
  })
}

export const useDeleteCompany = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (companyId: number) => {
      await axios.delete(`${API_URL}/tenants/me/companies/${companyId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      toast.success('Company deleted successfully')
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete company: ${error.message}`)
    }
  })
