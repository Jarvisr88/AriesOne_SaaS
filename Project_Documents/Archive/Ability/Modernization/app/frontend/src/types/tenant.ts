export type TenantStatus = 'active' | 'suspended' | 'pending' | 'archived'
export type SubscriptionTier = 'free' | 'basic' | 'professional' | 'enterprise'

export interface Tenant {
  id: number
  name: string
  domain: string | null
  status: TenantStatus
  subscription_tier: SubscriptionTier
  settings: Record<string, any>
  features: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Company {
  id: number
  tenant_id: number
  name: string
  domain: string | null
  settings: Record<string, any>
  features: Record<string, any>
  created_at: string
  updated_at: string
}

export interface TenantStats {
  company_count: number
  user_count: number
  active_user_count: number
  storage_usage: number
}

export interface TenantCreate {
  name: string
  domain?: string
  company_name: string
  admin_email: string
  admin_name: string
  settings?: Record<string, any>
}

export interface TenantUpdate {
  name?: string
  domain?: string
  settings?: Record<string, any>
}

export interface CompanyCreate {
  name: string
  domain?: string
  settings?: Record<string, any>
  features?: Record<string, any>
}

export interface CompanyUpdate {
  name?: string
  domain?: string
  settings?: Record<string, any>
  features?: Record<string, any>
}
