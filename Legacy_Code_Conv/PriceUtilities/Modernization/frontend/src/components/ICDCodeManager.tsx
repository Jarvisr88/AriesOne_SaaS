import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { toast } from '@/components/ui/use-toast';
import { Loader2, Plus, Edit2, Trash2 } from 'lucide-react';

const icdCodeSchema = z.object({
  code: z.string().regex(/^[A-Z0-9]+$/, 'Invalid ICD code format'),
  description: z.string().min(1, 'Description is required'),
  priceModifier: z.number()
    .min(0, 'Modifier must be positive')
    .max(10, 'Modifier cannot exceed 10'),
});

type ICDCodeFormValues = z.infer<typeof icdCodeSchema>;

const ICDCodeManager: React.FC = () => {
  const queryClient = useQueryClient();
  const [editingCode, setEditingCode] = React.useState<string | null>(null);

  const form = useForm<ICDCodeFormValues>({
    resolver: zodResolver(icdCodeSchema),
    defaultValues: {
      priceModifier: 1,
    },
  });

  // Query for ICD codes
  const { data: icdCodes, isLoading } = useQuery({
    queryKey: ['icdCodes'],
    queryFn: async () => {
      const response = await fetch('/api/v1/prices/icd-codes');
      if (!response.ok) throw new Error('Failed to fetch ICD codes');
      return response.json();
    },
  });

  // Mutation for creating/updating ICD codes
  const upsertICDCode = useMutation({
    mutationFn: async (values: ICDCodeFormValues) => {
      const url = editingCode
        ? `/api/v1/prices/icd-codes/${editingCode}`
        : '/api/v1/prices/icd-codes';
      
      const response = await fetch(url, {
        method: editingCode ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to save ICD code');
      }

      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: `ICD code ${editingCode ? 'updated' : 'created'} successfully`,
      });
      queryClient.invalidateQueries({ queryKey: ['icdCodes'] });
      form.reset();
      setEditingCode(null);
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Mutation for deleting ICD codes
  const deleteICDCode = useMutation({
    mutationFn: async (code: string) => {
      const response = await fetch(`/api/v1/prices/icd-codes/${code}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to delete ICD code');
      }
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'ICD code deleted successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['icdCodes'] });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const onSubmit = (values: ICDCodeFormValues) => {
    upsertICDCode.mutate(values);
  };

  const handleEdit = (code: any) => {
    setEditingCode(code.code);
    form.reset({
      code: code.code,
      description: code.description,
      priceModifier: code.priceModifier,
    });
  };

  const handleDelete = (code: string) => {
    if (window.confirm('Are you sure you want to delete this ICD code?')) {
      deleteICDCode.mutate(code);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>ICD Code Management</CardTitle>
          <CardDescription>
            Manage ICD codes and their price modifiers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Dialog>
            <DialogTrigger asChild>
              <Button className="mb-4">
                <Plus className="mr-2 h-4 w-4" />
                Add ICD Code
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingCode ? 'Edit ICD Code' : 'Add New ICD Code'}
                </DialogTitle>
                <DialogDescription>
                  Enter the ICD code details below
                </DialogDescription>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="code"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Code</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter ICD code"
                            {...field}
                            disabled={!!editingCode}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter description"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="priceModifier"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Price Modifier</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="0.01"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value))}
                          />
                        </FormControl>
                        <FormDescription>
                          Multiplier applied to base price (1 = no change)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={upsertICDCode.isPending}
                  >
                    {upsertICDCode.isPending && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    {editingCode ? 'Update' : 'Create'} ICD Code
                  </Button>
                </form>
              </Form>
            </DialogContent>
          </Dialog>

          {isLoading ? (
            <div className="flex justify-center p-4">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Price Modifier</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {icdCodes?.map((code: any) => (
                    <TableRow key={code.code}>
                      <TableCell>{code.code}</TableCell>
                      <TableCell>{code.description}</TableCell>
                      <TableCell>{code.priceModifier}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleEdit(code)}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(code.code)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ICDCodeManager;
