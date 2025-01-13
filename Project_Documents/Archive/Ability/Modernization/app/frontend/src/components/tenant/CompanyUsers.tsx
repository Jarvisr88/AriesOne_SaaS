import { useState } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { toast } from 'sonner'
import { User, UserRole } from '@/types/user'

const userSchema = z.object({
  email: z.string().email(),
  fullName: z.string().min(1, 'Full name is required'),
  role: z.enum(['admin', 'user', 'viewer']),
  department: z.string().optional()
})

interface CompanyUsersProps {
  companyId: number
}

export function CompanyUsers({ companyId }: CompanyUsersProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: users, isLoading } = useQuery({
    queryKey: ['company-users', companyId],
    queryFn: async () => {
      const { data } = await axios.get<User[]>(
        `/api/v1/companies/${companyId}/users`
      )
      return data
    }
  })

  const createUser = useMutation({
    mutationFn: async (values: z.infer<typeof userSchema>) => {
      const { data } = await axios.post(
        `/api/v1/companies/${companyId}/users`,
        values
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company-users'] })
      setIsCreateOpen(false)
      toast.success('User invited successfully')
    },
    onError: () => {
      toast.error('Failed to invite user')
    }
  })

  const updateUserStatus = useMutation({
    mutationFn: async ({
      userId,
      status
    }: {
      userId: number
      status: string
    }) => {
      const { data } = await axios.put(
        `/api/v1/companies/${companyId}/users/${userId}/status`,
        { status }
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company-users'] })
      toast.success('User status updated')
    },
    onError: () => {
      toast.error('Failed to update user status')
    }
  })

  const form = useForm<z.infer<typeof userSchema>>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      email: '',
      fullName: '',
      role: 'user',
      department: ''
    }
  })

  const onSubmit = (values: z.infer<typeof userSchema>) => {
    createUser.mutate(values)
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold tracking-tight">Users</h2>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>Invite User</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite New User</DialogTitle>
              <DialogDescription>
                Send an invitation to join the company
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input {...field} type="email" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="fullName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Full Name</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="role"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Role</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        defaultValue={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a role" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="admin">Admin</SelectItem>
                          <SelectItem value="user">User</SelectItem>
                          <SelectItem value="viewer">Viewer</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="department"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Department (Optional)</FormLabel>
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
                    disabled={createUser.isPending}
                  >
                    {createUser.isPending ? 'Sending...' : 'Send Invitation'}
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
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : users?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center">
                  No users found
                </TableCell>
              </TableRow>
            ) : (
              users?.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.fullName}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell className="capitalize">{user.role}</TableCell>
                  <TableCell>{user.department || '-'}</TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        user.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : user.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {user.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Select
                      value={user.status}
                      onValueChange={(status) =>
                        updateUserStatus.mutate({ userId: user.id, status })
                      }
                      disabled={updateUserStatus.isPending}
                    >
                      <SelectTrigger className="w-[100px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Activate</SelectItem>
                        <SelectItem value="suspended">Suspend</SelectItem>
                        <SelectItem value="inactive">Deactivate</SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
