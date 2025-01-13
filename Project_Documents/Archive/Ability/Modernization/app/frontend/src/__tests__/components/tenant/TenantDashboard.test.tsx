import { render, screen } from '@testing-library/react'
import { TenantDashboard } from '@/components/tenant/TenantDashboard'
import { useCurrentTenant, useTenantStats } from '@/api/tenant'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock the API hooks
jest.mock('@/api/tenant', () => ({
  useCurrentTenant: jest.fn(),
  useTenantStats: jest.fn()
}))

describe('TenantDashboard', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false
      }
    }
  })

  const mockTenant = {
    id: 1,
    name: 'Test Tenant',
    domain: 'test.example.com',
    status: 'active',
    subscription_tier: 'professional',
    settings: {},
    features: {},
    created_at: '2025-01-08T12:00:00Z',
    updated_at: '2025-01-08T12:00:00Z'
  }

  const mockStats = {
    company_count: 5,
    user_count: 25,
    active_user_count: 20,
    storage_usage: 1024 * 1024 * 100 // 100MB
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading state correctly', () => {
    ;(useCurrentTenant as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null
    })
    ;(useTenantStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null
    })

    render(
      <QueryClientProvider client={queryClient}>
        <TenantDashboard />
      </QueryClientProvider>
    )

    expect(screen.getByTestId('tenant-name-skeleton')).toBeInTheDocument()
    expect(screen.getAllByTestId('stat-skeleton')).toHaveLength(3)
  })

  it('renders tenant data correctly', () => {
    ;(useCurrentTenant as jest.Mock).mockReturnValue({
      data: mockTenant,
      isLoading: false,
      error: null
    })
    ;(useTenantStats as jest.Mock).mockReturnValue({
      data: mockStats,
      isLoading: false,
      error: null
    })

    render(
      <QueryClientProvider client={queryClient}>
        <TenantDashboard />
      </QueryClientProvider>
    )

    expect(screen.getByText('Test Tenant')).toBeInTheDocument()
    expect(screen.getByText('PROFESSIONAL')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument() // company count
    expect(screen.getByText('20')).toBeInTheDocument() // active users
    expect(screen.getByText('of 25 total users')).toBeInTheDocument()
    expect(screen.getByText('100 MB')).toBeInTheDocument()
  })

  it('renders error state correctly', () => {
    const error = new Error('Failed to load tenant data')
    ;(useCurrentTenant as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      error
    })
    ;(useTenantStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      error
    })

    render(
      <QueryClientProvider client={queryClient}>
        <TenantDashboard />
      </QueryClientProvider>
    )

    expect(
      screen.getByText('Failed to load tenant information. Please try again later.')
    ).toBeInTheDocument()
  })

  it('displays correct status indicator', () => {
    ;(useCurrentTenant as jest.Mock).mockReturnValue({
      data: { ...mockTenant, status: 'suspended' },
      isLoading: false,
      error: null
    })
    ;(useTenantStats as jest.Mock).mockReturnValue({
      data: mockStats,
      isLoading: false,
      error: null
    })

    render(
      <QueryClientProvider client={queryClient}>
        <TenantDashboard />
      </QueryClientProvider>
    )

    const statusIndicator = screen.getByTestId('status-indicator')
    expect(statusIndicator).toHaveClass('bg-red-500')
  })
})
