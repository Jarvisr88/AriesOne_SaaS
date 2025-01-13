import { useState } from 'react'
import {
  useCompanies,
  useCreateCompany,
  useUpdateCompany,
  useDeleteCompany
} from '@/api/tenant'
import { Company, CompanyCreate } from '@/types/tenant'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Pencil, Trash2, Plus } from 'lucide-react'

const companySchema = z.object({
  name: z.string().min(1, 'Name is required'),
  domain: z.string().optional(),
  settings: z.record(z.any()).optional(),
  features: z.record(z.any()).optional()
})

export function CompanyManager() {
  const [page, setPage] = useState(1)
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)

  const { data: companies, isLoading } = useCompanies(page)
  const createCompany = useCreateCompany()
  const updateCompany = useUpdateCompany(selectedCompany?.id || 0)
  const deleteCompany = useDeleteCompany()

  const form = useForm<z.infer<typeof companySchema>>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      name: '',
      domain: '',
      settings: {},
      features: {}
    }
  })

  const onSubmit = async (values: z.infer<typeof companySchema>) => {
    if (selectedCompany) {
      await updateCompany.mutateAsync(values)
      setIsEditOpen(false)
    } else {
      await createCompany.mutateAsync(values as CompanyCreate)
      setIsCreateOpen(false)
    }
    form.reset()
  }

  const handleEdit = (company: Company) => {
    setSelectedCompany(company)
    form.reset({
      name: company.name,
      domain: company.domain || '',
      settings: company.settings,
      features: company.features
    })
    setIsEditOpen(true)
  }

  const handleDelete = async () => {
    if (selectedCompany) {
      await deleteCompany.mutateAsync(selectedCompany.id)
      setIsDeleteOpen(false)
      setSelectedCompany(null)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold tracking-tight">Companies</h2>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Company
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Company</DialogTitle>
              <DialogDescription>
                Add a new company to your tenant.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Company Name</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="domain"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Domain (Optional)</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter>
                  <Button
                    type="submit"
                    disabled={createCompany.isPending}
                  >
                    {createCompany.isPending ? 'Creating...' : 'Create Company'}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Domain</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : companies?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center">
                  No companies found
                </TableCell>
              </TableRow>
            ) : (
              companies?.map((company) => (
                <TableRow key={company.id}>
                  <TableCell>{company.name}</TableCell>
                  <TableCell>{company.domain || '-'}</TableCell>
                  <TableCell>
                    {new Date(company.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEdit(company)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setSelectedCompany(company)
                          setIsDeleteOpen(true)
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Company</DialogTitle>
            <DialogDescription>
              Update company information.
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Company Name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="domain"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Domain</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button
                  type="submit"
                  disabled={updateCompany.isPending}
                >
                  {updateCompany.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the
              company and all associated data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteCompany.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
