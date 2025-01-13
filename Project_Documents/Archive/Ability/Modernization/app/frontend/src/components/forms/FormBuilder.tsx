import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Checkbox } from '@/components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { cn } from '@/lib/utils'
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult
} from '@hello-pangea/dnd'
import { Loader2 } from 'lucide-react'

export interface FormField {
  id: string
  type: string
  label: string
  name: string
  required: boolean
  placeholder?: string
  description?: string
  options?: { label: string; value: string }[]
  validation?: {
    type: string
    params?: any
  }[]
}

export interface FormConfig {
  id: string
  title: string
  description?: string
  fields: FormField[]
  submitEndpoint: string
  successMessage?: string
  errorMessage?: string
}

const fieldComponents = {
  text: Input,
  email: Input,
  password: Input,
  number: Input,
  textarea: Textarea,
  select: Select,
  checkbox: Checkbox,
  switch: Switch,
  radio: RadioGroup
}

export function FormBuilder({ config }: { config: FormConfig }) {
  const [formFields, setFormFields] = useState(config.fields)

  // Generate Zod schema from form config
  const generateSchema = () => {
    const schemaFields: { [key: string]: any } = {}

    formFields.forEach((field) => {
      let fieldSchema = z.string()

      if (field.required) {
        fieldSchema = fieldSchema.min(1, 'This field is required')
      } else {
        fieldSchema = fieldSchema.optional()
      }

      field.validation?.forEach((rule) => {
        switch (rule.type) {
          case 'email':
            fieldSchema = fieldSchema.email('Invalid email address')
            break
          case 'min':
            fieldSchema = fieldSchema.min(
              rule.params.value,
              `Minimum ${rule.params.value} characters required`
            )
            break
          case 'max':
            fieldSchema = fieldSchema.max(
              rule.params.value,
              `Maximum ${rule.params.value} characters allowed`
            )
            break
          case 'regex':
            fieldSchema = fieldSchema.regex(
              new RegExp(rule.params.pattern),
              rule.params.message || 'Invalid format'
            )
            break
        }
      })

      schemaFields[field.name] = fieldSchema
    })

    return z.object(schemaFields)
  }

  const form = useForm({
    resolver: zodResolver(generateSchema())
  })

  const submitMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await axios.post(config.submitEndpoint, data)
      return response.data
    }
  })

  const onSubmit = async (data: any) => {
    try {
      await submitMutation.mutateAsync(data)
      // Handle success
    } catch (error) {
      // Handle error
    }
  }

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return

    const items = Array.from(formFields)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    setFormFields(items)
  }

  const renderField = (field: FormField) => {
    const Component = fieldComponents[field.type as keyof typeof fieldComponents]
    if (!Component) return null

    return (
      <FormField
        key={field.id}
        control={form.control}
        name={field.name}
        render={({ field: formField }) => (
          <FormItem>
            <FormLabel>{field.label}</FormLabel>
            <FormControl>
              {field.type === 'select' ? (
                <Select
                  onValueChange={formField.onChange}
                  defaultValue={formField.value}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={field.placeholder} />
                  </SelectTrigger>
                  <SelectContent>
                    {field.options?.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : field.type === 'radio' ? (
                <RadioGroup
                  onValueChange={formField.onChange}
                  defaultValue={formField.value}
                  className="flex flex-col space-y-1"
                >
                  {field.options?.map((option) => (
                    <div key={option.value} className="flex items-center space-x-2">
                      <RadioGroupItem value={option.value} />
                      <span>{option.label}</span>
                    </div>
                  ))}
                </RadioGroup>
              ) : field.type === 'checkbox' ? (
                <Checkbox
                  checked={formField.value}
                  onCheckedChange={formField.onChange}
                />
              ) : field.type === 'switch' ? (
                <Switch
                  checked={formField.value}
                  onCheckedChange={formField.onChange}
                />
              ) : (
                <Component
                  {...formField}
                  type={field.type}
                  placeholder={field.placeholder}
                />
              )}
            </FormControl>
            {field.description && (
              <FormDescription>{field.description}</FormDescription>
            )}
            <FormMessage />
          </FormItem>
        )}
      />
    )
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8"
      >
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">{config.title}</h2>
          {config.description && (
            <p className="text-muted-foreground">{config.description}</p>
          )}
        </div>

        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="fields">
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                className="space-y-6"
              >
                {formFields.map((field, index) => (
                  <Draggable
                    key={field.id}
                    draggableId={field.id}
                    index={index}
                  >
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={cn(
                          'p-4 rounded-lg border',
                          snapshot.isDragging && 'bg-muted'
                        )}
                      >
                        {renderField(field)}
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

        <Button
          type="submit"
          disabled={submitMutation.isPending}
          className="w-full"
        >
          {submitMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            'Submit'
          )}
        </Button>
      </form>
    </Form>
  )
}
