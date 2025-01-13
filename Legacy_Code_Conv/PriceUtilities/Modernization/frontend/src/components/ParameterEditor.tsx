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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { toast } from '@/components/ui/use-toast';
import { Loader2, Plus, Edit2, Trash2 } from 'lucide-react';

const parameterSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  value: z.string().min(1, 'Value is required'),
  parameterType: z.enum(['MULTIPLIER', 'FIXED_ADDITION', 'PERCENTAGE']),
  description: z.string().optional(),
  effectiveDate: z.string().optional(),
  expirationDate: z.string().optional(),
});

type ParameterFormValues = z.infer<typeof parameterSchema>;

const ParameterEditor: React.FC = () => {
  const queryClient = useQueryClient();
  const [editingParameter, setEditingParameter] = React.useState<string | null>(null);

  const form = useForm<ParameterFormValues>({
    resolver: zodResolver(parameterSchema),
    defaultValues: {
      parameterType: 'MULTIPLIER',
    },
  });

  // Query for parameters
  const { data: parameters, isLoading } = useQuery({
    queryKey: ['parameters'],
    queryFn: async () => {
      const response = await fetch('/api/v1/prices/parameters');
      if (!response.ok) throw new Error('Failed to fetch parameters');
      return response.json();
    },
  });

  // Mutation for creating/updating parameters
  const upsertParameter = useMutation({
    mutationFn: async (values: ParameterFormValues) => {
      const url = editingParameter
        ? `/api/v1/prices/parameters/${editingParameter}`
        : '/api/v1/prices/parameters';
      
      const response = await fetch(url, {
        method: editingParameter ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to save parameter');
      }

      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: `Parameter ${editingParameter ? 'updated' : 'created'} successfully`,
      });
      queryClient.invalidateQueries({ queryKey: ['parameters'] });
      form.reset();
      setEditingParameter(null);
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Mutation for deleting parameters
  const deleteParameter = useMutation({
    mutationFn: async (name: string) => {
      const response = await fetch(`/api/v1/prices/parameters/${name}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to delete parameter');
      }
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Parameter deleted successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['parameters'] });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const onSubmit = (values: ParameterFormValues) => {
    upsertParameter.mutate(values);
  };

  const handleEdit = (parameter: any) => {
    setEditingParameter(parameter.name);
    form.reset({
      name: parameter.name,
      value: parameter.value.toString(),
      parameterType: parameter.parameterType,
      description: parameter.description,
      effectiveDate: parameter.effectiveDate,
      expirationDate: parameter.expirationDate,
    });
  };

  const handleDelete = (name: string) => {
    if (window.confirm('Are you sure you want to delete this parameter?')) {
      deleteParameter.mutate(name);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Parameter Editor</CardTitle>
        <CardDescription>
          Manage pricing parameters and modifiers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter parameter name"
                      {...field}
                      disabled={!!editingParameter}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="parameterType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select parameter type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="MULTIPLIER">Multiplier</SelectItem>
                      <SelectItem value="FIXED_ADDITION">Fixed Addition</SelectItem>
                      <SelectItem value="PERCENTAGE">Percentage</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="value"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Value</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="Enter value"
                      {...field}
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

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="effectiveDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Effective Date</FormLabel>
                    <FormControl>
                      <Input
                        type="datetime-local"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="expirationDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Expiration Date</FormLabel>
                    <FormControl>
                      <Input
                        type="datetime-local"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={upsertParameter.isPending}
            >
              {upsertParameter.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              {editingParameter ? 'Update' : 'Create'} Parameter
            </Button>
          </form>
        </Form>

        <div className="mt-8">
          <h3 className="text-lg font-medium mb-4">Active Parameters</h3>
          {isLoading ? (
            <div className="flex justify-center p-4">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {parameters?.map((param: any) => (
                    <TableRow key={param.name}>
                      <TableCell>{param.name}</TableCell>
                      <TableCell>{param.parameterType}</TableCell>
                      <TableCell>{param.value}</TableCell>
                      <TableCell>
                        {param.effectiveDate && new Date(param.effectiveDate) > new Date()
                          ? 'Pending'
                          : param.expirationDate && new Date(param.expirationDate) < new Date()
                          ? 'Expired'
                          : 'Active'}
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleEdit(param)}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(param.name)}
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
        </div>
      </CardContent>
    </Card>
  );
};

export default ParameterEditor;
