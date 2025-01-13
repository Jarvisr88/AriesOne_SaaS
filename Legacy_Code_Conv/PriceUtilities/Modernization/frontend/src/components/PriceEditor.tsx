import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { format } from 'date-fns';
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
import { toast } from '@/components/ui/use-toast';
import { Loader2 } from 'lucide-react';

// Form validation schema
const priceFormSchema = z.object({
  itemId: z.string().min(1, 'Item ID is required'),
  basePrice: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Invalid price format'),
  currency: z.string().length(3, 'Currency must be 3 letters'),
  effectiveDate: z.string().optional(),
  icdCodes: z.array(z.string()).optional(),
});

type PriceFormValues = z.infer<typeof priceFormSchema>;

const PriceEditor: React.FC = () => {
  const queryClient = useQueryClient();

  // Form setup
  const form = useForm<PriceFormValues>({
    resolver: zodResolver(priceFormSchema),
    defaultValues: {
      currency: 'USD',
      icdCodes: [],
    },
  });

  // Query for ICD codes
  const { data: icdCodes, isLoading: isLoadingIcdCodes } = useQuery({
    queryKey: ['icdCodes'],
    queryFn: async () => {
      const response = await fetch('/api/v1/prices/icd-codes');
      if (!response.ok) throw new Error('Failed to fetch ICD codes');
      return response.json();
    },
  });

  // Mutation for price updates
  const updatePrice = useMutation({
    mutationFn: async (values: PriceFormValues) => {
      const response = await fetch('/api/v1/prices/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: values.itemId,
          base_price: parseFloat(values.basePrice),
          currency: values.currency,
          effective_date: values.effectiveDate,
          icd_codes: values.icdCodes,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to update price');
      }

      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Price updated successfully',
      });
      queryClient.invalidateQueries({ queryKey: ['prices'] });
      form.reset();
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const onSubmit = (values: PriceFormValues) => {
    updatePrice.mutate(values);
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Price Editor</CardTitle>
        <CardDescription>
          Update pricing information for medical equipment
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="itemId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Item ID</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter item ID" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="basePrice"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Base Price</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Enter the base price without any discounts
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="currency"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Currency</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select currency" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                      <SelectItem value="GBP">GBP</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

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
                      min={format(new Date(), "yyyy-MM-dd'T'HH:mm")}
                    />
                  </FormControl>
                  <FormDescription>
                    When should this price become effective?
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              className="w-full"
              disabled={updatePrice.isPending}
            >
              {updatePrice.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Update Price
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default PriceEditor;
