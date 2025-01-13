import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useDropzone } from 'react-dropzone';
import * as XLSX from 'xlsx';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { toast } from '@/components/ui/use-toast';
import { Loader2, Upload, FileSpreadsheet } from 'lucide-react';

interface BulkUpdateRow {
  itemId: string;
  basePrice: number;
  currency: string;
  effectiveDate?: string;
  icdCodes?: string[];
}

const BulkUpdateInterface: React.FC = () => {
  const queryClient = useQueryClient();
  const [updates, setUpdates] = useState<BulkUpdateRow[]>([]);
  const [progress, setProgress] = useState(0);

  // File upload handling
  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    const reader = new FileReader();

    reader.onload = (event) => {
      try {
        const data = new Uint8Array(event.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, { type: 'array' });
        const worksheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);

        // Transform data to match our format
        const transformedData = jsonData.map((row: any) => ({
          itemId: row.itemId || row.item_id,
          basePrice: parseFloat(row.basePrice || row.base_price),
          currency: (row.currency || 'USD').toUpperCase(),
          effectiveDate: row.effectiveDate || row.effective_date,
          icdCodes: row.icdCodes || row.icd_codes,
        }));

        setUpdates(transformedData);
        toast({
          title: 'File Loaded',
          description: `Loaded ${transformedData.length} updates`,
        });
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to parse file',
          variant: 'destructive',
        });
      }
    };

    reader.readAsArrayBuffer(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  // Mutation for bulk updates
  const bulkUpdate = useMutation({
    mutationFn: async (updates: BulkUpdateRow[]) => {
      const response = await fetch('/api/v1/prices/bulk-update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ updates }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to process bulk update');
      }

      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: `Successfully processed ${data.successful} updates`,
      });
      queryClient.invalidateQueries({ queryKey: ['prices'] });
      setUpdates([]);
      setProgress(0);
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const handleBulkUpdate = async () => {
    if (updates.length === 0) {
      toast({
        title: 'Error',
        description: 'No updates to process',
        variant: 'destructive',
      });
      return;
    }

    const batchSize = 100;
    const totalBatches = Math.ceil(updates.length / batchSize);

    for (let i = 0; i < updates.length; i += batchSize) {
      const batch = updates.slice(i, i + batchSize);
      await bulkUpdate.mutateAsync(batch);
      setProgress(((i + batchSize) / updates.length) * 100);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Bulk Price Update</CardTitle>
        <CardDescription>
          Upload a spreadsheet to update multiple prices at once
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center ${
            isDragActive ? 'border-primary' : 'border-muted'
          }`}
        >
          <input {...getInputProps()} />
          <FileSpreadsheet className="mx-auto h-12 w-12 text-muted-foreground" />
          <p className="mt-2">
            {isDragActive
              ? 'Drop the file here'
              : 'Drag and drop a spreadsheet, or click to select'}
          </p>
          <p className="text-sm text-muted-foreground">
            Supports XLSX, XLS, and CSV files
          </p>
        </div>

        {updates.length > 0 && (
          <>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item ID</TableHead>
                    <TableHead>Base Price</TableHead>
                    <TableHead>Currency</TableHead>
                    <TableHead>Effective Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {updates.slice(0, 5).map((update, index) => (
                    <TableRow key={index}>
                      <TableCell>{update.itemId}</TableCell>
                      <TableCell>{update.basePrice}</TableCell>
                      <TableCell>{update.currency}</TableCell>
                      <TableCell>{update.effectiveDate || 'Immediate'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {updates.length > 5 && (
              <p className="text-sm text-muted-foreground text-center">
                Showing 5 of {updates.length} updates
              </p>
            )}

            <div className="space-y-2">
              <Progress value={progress} />
              <Button
                className="w-full"
                onClick={handleBulkUpdate}
                disabled={bulkUpdate.isPending}
              >
                {bulkUpdate.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Process {updates.length} Updates
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default BulkUpdateInterface;
