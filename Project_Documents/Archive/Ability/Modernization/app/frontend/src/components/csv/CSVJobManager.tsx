import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ProcessingStatus } from '@/types/csv'
import { formatDistanceToNow } from 'date-fns'

export function CSVJobManager() {
  const [selectedStatus, setSelectedStatus] = useState<ProcessingStatus | 'all'>(
    'all'
  )
  const [selectedJob, setSelectedJob] = useState<any>(null)

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['csv-jobs', selectedStatus],
    queryFn: async () => {
      const params = selectedStatus !== 'all' ? { status: selectedStatus } : {}
      const { data } = await axios.get('/api/v1/csv/jobs', { params })
      return data
    },
    refetchInterval: (data) => {
      // Refetch more frequently if there are pending or in-progress jobs
      const hasActiveJobs = data?.some((job: any) =>
        ['pending', 'in_progress'].includes(job.status)
      )
      return hasActiveJobs ? 5000 : 30000
    }
  })

  const getStatusBadgeVariant = (status: ProcessingStatus) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'destructive'
      case 'in_progress':
        return 'default'
      default:
        return 'secondary'
    }
  }

  const formatProgress = (job: any) => {
    if (!job.total_rows) return '0%'
    return `${Math.round((job.processed_rows / job.total_rows) * 100)}%`
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Processing Jobs</CardTitle>
          <CardDescription>
            Monitor and manage CSV processing jobs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Select
              value={selectedStatus}
              onValueChange={(value: ProcessingStatus | 'all') =>
                setSelectedStatus(value)
              }
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File Name</TableHead>
                  <TableHead>Schema</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Started</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="text-center text-muted-foreground"
                    >
                      Loading jobs...
                    </TableCell>
                  </TableRow>
                ) : jobs?.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="text-center text-muted-foreground"
                    >
                      No jobs found
                    </TableCell>
                  </TableRow>
                ) : (
                  jobs?.map((job: any) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.file_name}</TableCell>
                      <TableCell>{job.schema_name}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(job.status)}>
                          {job.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatProgress(job)}</TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(job.start_time), {
                          addSuffix: true
                        })}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          onClick={() => setSelectedJob(job)}
                        >
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Dialog open={!!selectedJob} onOpenChange={() => setSelectedJob(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Job Details</DialogTitle>
            <DialogDescription>
              Processing details for {selectedJob?.file_name}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium">Status</p>
                <Badge variant={getStatusBadgeVariant(selectedJob?.status)}>
                  {selectedJob?.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm font-medium">Schema</p>
                <p className="text-sm">{selectedJob?.schema_name}</p>
              </div>
              <div>
                <p className="text-sm font-medium">Started</p>
                <p className="text-sm">
                  {selectedJob?.start_time &&
                    new Date(selectedJob.start_time).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Completed</p>
                <p className="text-sm">
                  {selectedJob?.end_time
                    ? new Date(selectedJob.end_time).toLocaleString()
                    : '-'}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Total Rows</p>
                <p className="text-sm">{selectedJob?.total_rows || 0}</p>
              </div>
              <div>
                <p className="text-sm font-medium">Processed Rows</p>
                <p className="text-sm">{selectedJob?.processed_rows || 0}</p>
              </div>
            </div>

            {selectedJob?.errors?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Errors</p>
                <ScrollArea className="h-[200px] border rounded-lg p-4">
                  <ul className="space-y-2">
                    {selectedJob.errors.map((error: any, index: number) => (
                      <li key={index} className="text-sm text-destructive">
                        {error.type === 'missing_columns' && (
                          <span>
                            Missing required columns:{' '}
                            {error.columns.join(', ')}
                          </span>
                        )}
                        {error.type === 'invalid_type' && (
                          <span>
                            Invalid data type in column {error.column}:{' '}
                            {error.expected_type} (rows:{' '}
                            {error.rows.slice(0, 3).join(', ')}
                            {error.rows.length > 3 ? '...' : ''})
                          </span>
                        )}
                        {error.type === 'rule_violation' && (
                          <span>
                            {error.column}: {error.rule} rule violation (rows:{' '}
                            {error.rows.slice(0, 3).join(', ')}
                            {error.rows.length > 3 ? '...' : ''})
                          </span>
                        )}
                        {error.type === 'processing_error' && (
                          <span>{error.message}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </ScrollArea>
              </div>
            )}

            {selectedJob?.output_path && (
              <div className="flex justify-end">
                <Button
                  onClick={() =>
                    window.open(
                      `/api/v1/csv/download/${selectedJob.id}`,
                      '_blank'
                    )
                  }
                >
                  Download Processed File
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
