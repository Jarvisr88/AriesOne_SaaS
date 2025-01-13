import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Upload, FileText, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'

export function CSVUploader() {
  const [file, setFile] = useState<File | null>(null)
  const [selectedSchema, setSelectedSchema] = useState<string>('')
  const [validationErrors, setValidationErrors] = useState<any[]>([])

  const { data: schemas } = useQuery({
    queryKey: ['csv-schemas'],
    queryFn: async () => {
      const { data } = await axios.get('/api/v1/csv/schemas')
      return data
    }
  })

  const detectSchema = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await axios.post('/api/v1/csv/detect-schema', formData)
      return data
    }
  })

  const validateFile = useMutation({
    mutationFn: async ({ file, schema }: { file: File; schema: string }) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await axios.post(
        `/api/v1/csv/validate?schema_name=${schema}`,
        formData
      )
      return data
    }
  })

  const processFile = useMutation({
    mutationFn: async ({ file, schema }: { file: File; schema: string }) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await axios.post(
        `/api/v1/csv/process?schema_name=${schema}`,
        formData
      )
      return data
    }
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    onDrop: async (acceptedFiles) => {
      const file = acceptedFiles[0]
      setFile(file)
      setValidationErrors([])

      // Auto-detect schema
      try {
        const result = await detectSchema.mutateAsync(file)
        if (result.detected_schema && result.confidence > 0.8) {
          setSelectedSchema(result.detected_schema)
          toast.success(
            `Detected schema: ${result.detected_schema} (${Math.round(
              result.confidence * 100
            )}% confidence)`
          )
        }
      } catch (error) {
        toast.error('Failed to detect schema')
      }
    }
  })

  const handleValidate = async () => {
    if (!file || !selectedSchema) return

    try {
      const result = await validateFile.mutateAsync({
        file,
        schema: selectedSchema
      })
      
      if (result.is_valid) {
        toast.success('File validation successful')
        setValidationErrors([])
      } else {
        setValidationErrors(result.errors)
        toast.error('File validation failed')
      }
    } catch (error) {
      toast.error('Validation failed')
    }
  }

  const handleProcess = async () => {
    if (!file || !selectedSchema) return

    try {
      const result = await processFile.mutateAsync({
        file,
        schema: selectedSchema
      })
      toast.success('File processing started')
      setFile(null)
      setSelectedSchema('')
      setValidationErrors([])
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail?.message || 'Failed to process file'
      )
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Upload CSV File</CardTitle>
          <CardDescription>
            Drop your CSV file here or click to browse
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary bg-primary/10'
                : 'border-muted-foreground/25'
            }`}
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="flex items-center justify-center space-x-2">
                <FileText className="h-6 w-6" />
                <span>{file.name}</span>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center">
                <Upload className="h-8 w-8 mb-2" />
                <p>Drag and drop a CSV file here, or click to select</p>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            <Select
              value={selectedSchema}
              onValueChange={setSelectedSchema}
              disabled={!file}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select schema" />
              </SelectTrigger>
              <SelectContent>
                {schemas?.map((schema: string) => (
                  <SelectItem key={schema} value={schema}>
                    {schema}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="secondary"
              onClick={handleValidate}
              disabled={!file || !selectedSchema || validateFile.isPending}
            >
              {validateFile.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Validate'
              )}
            </Button>

            <Button
              onClick={handleProcess}
              disabled={
                !file ||
                !selectedSchema ||
                validationErrors.length > 0 ||
                processFile.isPending
              }
            >
              {processFile.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Process File'
              )}
            </Button>
          </div>

          {validationErrors.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p className="font-semibold">Validation Errors:</p>
                  <ul className="list-disc pl-4 space-y-1">
                    {validationErrors.map((error, index) => (
                      <li key={index}>
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
                      </li>
                    ))}
                  </ul>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
