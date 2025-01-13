import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CompanyManager } from '@/components/tenant/CompanyManager'
import {
  useCompanies,
  useCreateCompany,
  useUpdateCompany,
  useDeleteCompany
} from '@/api/tenant'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock the API hooks
jest.mock('@/api/tenant', () => ({
  useCompanies: jest.fn(),
  useCreateCompany: jest.fn(),
  useUpdateCompany: jest.fn(),
  useDeleteCompany: jest.fn()
}))

describe('CompanyManager', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false
      }
    }
  })

  const mockCompanies = [
    {
      id: 1,
      name: 'Test Company 1',
      domain: 'company1.example.com',
      settings: {},
      features: {},
      created_at: '2025-01-08T12:00:00Z',
      updated_at: '2025-01-08T12:00:00Z'
    },
    {
      id: 2,
      name: 'Test Company 2',
      domain: 'company2.example.com',
      settings: {},
      features: {},
      created_at: '2025-01-08T12:00:00Z',
      updated_at: '2025-01-08T12:00:00Z'
    }
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders companies list correctly', () => {
    ;(useCompanies as jest.Mock).mockReturnValue({
      data: mockCompanies,
      isLoading: false
    })
    ;(useCreateCompany as jest.Mock).mockReturnValue({
      mutateAsync: jest.fn(),
      isPending: false
    })
    ;(useUpdateCompany as jest.Mock).mockReturnValue({
      mutateAsync: jest.fn(),
      isPending: false
    })
    ;(useDeleteCompany as jest.Mock).mockReturnValue({
      mutateAsync: jest.fn(),
      isPending: false
    })

    render(
      <QueryClientProvider client={queryClient}>
        <CompanyManager />
      </QueryClientProvider>
    )

    expect(screen.getByText('Test Company 1')).toBeInTheDocument()
    expect(screen.getByText('Test Company 2')).toBeInTheDocument()
    expect(screen.getByText('company1.example.com')).toBeInTheDocument()
    expect(screen.getByText('company2.example.com')).toBeInTheDocument()
  })

  it('opens create company dialog and submits form', async () => {
    const createCompanyMock = jest.fn()
    ;(useCompanies as jest.Mock).mockReturnValue({
      data: mockCompanies,
      isLoading: false
    })
    ;(useCreateCompany as jest.Mock).mockReturnValue({
      mutateAsync: createCompanyMock,
      isPending: false
    })

    render(
      <QueryClientProvider client={queryClient}>
        <CompanyManager />
      </QueryClientProvider>
    )

    // Open create dialog
    fireEvent.click(screen.getByText('Add Company'))

    // Fill form
    await userEvent.type(
      screen.getByLabelText('Company Name'),
      'New Test Company'
    )
    await userEvent.type(
      screen.getByLabelText('Domain (Optional)'),
      'new.example.com'
    )

    // Submit form
    fireEvent.click(screen.getByText('Create Company'))

    await waitFor(() => {
      expect(createCompanyMock).toHaveBeenCalledWith({
        name: 'New Test Company',
        domain: 'new.example.com',
        settings: {},
        features: {}
      })
    })
  })

  it('opens edit company dialog and updates company', async () => {
    const updateCompanyMock = jest.fn()
    ;(useCompanies as jest.Mock).mockReturnValue({
      data: mockCompanies,
      isLoading: false
    })
    ;(useUpdateCompany as jest.Mock).mockReturnValue({
      mutateAsync: updateCompanyMock,
      isPending: false
    })

    render(
      <QueryClientProvider client={queryClient}>
        <CompanyManager />
      </QueryClientProvider>
    )

    // Click edit button for first company
    const editButtons = screen.getAllByRole('button', { name: /edit/i })
    fireEvent.click(editButtons[0])

    // Update company name
    const nameInput = screen.getByLabelText('Company Name')
    await userEvent.clear(nameInput)
    await userEvent.type(nameInput, 'Updated Company Name')

    // Submit form
    fireEvent.click(screen.getByText('Save Changes'))

    await waitFor(() => {
      expect(updateCompanyMock).toHaveBeenCalledWith({
        name: 'Updated Company Name',
        domain: 'company1.example.com',
        settings: {},
        features: {}
      })
    })
  })

  it('confirms and deletes company', async () => {
    const deleteCompanyMock = jest.fn()
    ;(useCompanies as jest.Mock).mockReturnValue({
      data: mockCompanies,
      isLoading: false
    })
    ;(useDeleteCompany as jest.Mock).mockReturnValue({
      mutateAsync: deleteCompanyMock,
      isPending: false
    })

    render(
      <QueryClientProvider client={queryClient}>
        <CompanyManager />
      </QueryClientProvider>
    )

    // Click delete button for first company
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
    fireEvent.click(deleteButtons[0])

    // Confirm deletion
    fireEvent.click(screen.getByText('Delete'))

    await waitFor(() => {
      expect(deleteCompanyMock).toHaveBeenCalledWith(1)
    })
  })

  it('shows loading state', () => {
    ;(useCompanies as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true
    })

    render(
      <QueryClientProvider client={queryClient}>
        <CompanyManager />
      </QueryClientProvider>
    )

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('shows empty state', () => {
    ;(useCompanies as jest.Mock).mockReturnValue({
      data: [],
      isLoading: false
    })

    render(
      <QueryClientProvider client={queryClient}>
        <CompanyManager />
      </QueryClientProvider>
    )

    expect(screen.getByText('No companies found')).toBeInTheDocument()
  })
})
