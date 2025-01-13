import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeProvider } from 'styled-components'
import { z } from 'zod'
import {
  Form,
  FormField,
  FormContainer,
  FormGroup,
  FormSection,
  useFormContext
} from './Form'
import { lightTheme } from '../../theme/theme'

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider theme={lightTheme}>
      {ui}
    </ThemeProvider>
  )
}

const TestInput = ({ name, ...props }: { name: string; [key: string]: any }) => {
  const { register } = useFormContext()
  return <input {...register(name)} {...props} />
}

describe('Form', () => {
  const schema = z.object({
    username: z.string().min(3, 'Username must be at least 3 characters'),
    email: z.string().email('Invalid email address'),
    age: z.number().min(18, 'Must be at least 18 years old')
  })

  it('renders form elements', () => {
    renderWithTheme(
      <Form onSubmit={() => {}}>
        <FormContainer>
          <FormField name="username" label="Username">
            <TestInput name="username" />
          </FormField>
        </FormContainer>
      </Form>
    )

    expect(screen.getByLabelText('Username')).toBeInTheDocument()
  })

  it('handles form submission with validation', async () => {
    const onSubmit = jest.fn()
    const onError = jest.fn()

    renderWithTheme(
      <Form
        schema={schema}
        onSubmit={onSubmit}
        onError={onError}
      >
        <FormContainer>
          <FormField name="username" label="Username">
            <TestInput name="username" />
          </FormField>
          <FormField name="email" label="Email">
            <TestInput name="email" />
          </FormField>
          <FormField name="age" label="Age">
            <TestInput name="age" type="number" />
          </FormField>
          <button type="submit">Submit</button>
        </FormContainer>
      </Form>
    )

    fireEvent.click(screen.getByText('Submit'))

    await waitFor(() => {
      expect(screen.getByText('Username must be at least 3 characters')).toBeInTheDocument()
      expect(screen.getByText('Invalid email address')).toBeInTheDocument()
    })

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('submits form with valid data', async () => {
    const onSubmit = jest.fn()

    renderWithTheme(
      <Form
        schema={schema}
        onSubmit={onSubmit}
      >
        <FormContainer>
          <FormField name="username" label="Username">
            <TestInput name="username" />
          </FormField>
          <FormField name="email" label="Email">
            <TestInput name="email" />
          </FormField>
          <FormField name="age" label="Age">
            <TestInput name="age" type="number" />
          </FormField>
          <button type="submit">Submit</button>
        </FormContainer>
      </Form>
    )

    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'testuser' }
    })
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByLabelText('Age'), {
      target: { value: '20' }
    })

    fireEvent.click(screen.getByText('Submit'))

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        age: 20
      })
    })
  })

  it('renders form with different layouts', () => {
    const { rerender } = renderWithTheme(
      <Form onSubmit={() => {}}>
        <FormContainer layout="vertical">
          <FormField name="field1" label="Field 1">
            <TestInput name="field1" />
          </FormField>
          <FormField name="field2" label="Field 2">
            <TestInput name="field2" />
          </FormField>
        </FormContainer>
      </Form>
    )

    expect(screen.getByLabelText('Field 1')).toBeInTheDocument()
    expect(screen.getByLabelText('Field 2')).toBeInTheDocument()

    rerender(
      <ThemeProvider theme={lightTheme}>
        <Form onSubmit={() => {}}>
          <FormContainer layout="horizontal">
            <FormField name="field1" label="Field 1">
              <TestInput name="field1" />
            </FormField>
            <FormField name="field2" label="Field 2">
              <TestInput name="field2" />
            </FormField>
          </FormContainer>
        </Form>
      </ThemeProvider>
    )

    expect(screen.getByLabelText('Field 1')).toBeInTheDocument()
    expect(screen.getByLabelText('Field 2')).toBeInTheDocument()
  })

  it('renders form groups with columns', () => {
    renderWithTheme(
      <Form onSubmit={() => {}}>
        <FormGroup columns={2}>
          <FormField name="field1" label="Field 1">
            <TestInput name="field1" />
          </FormField>
          <FormField name="field2" label="Field 2">
            <TestInput name="field2" />
          </FormField>
        </FormGroup>
      </Form>
    )

    expect(screen.getByLabelText('Field 1')).toBeInTheDocument()
    expect(screen.getByLabelText('Field 2')).toBeInTheDocument()
  })

  it('renders form sections', () => {
    renderWithTheme(
      <Form onSubmit={() => {}}>
        <FormSection>
          <FormField name="field1" label="Field 1">
            <TestInput name="field1" />
          </FormField>
        </FormSection>
      </Form>
    )

    expect(screen.getByLabelText('Field 1')).toBeInTheDocument()
  })

  it('shows helper text and error messages', async () => {
    renderWithTheme(
      <Form
        schema={schema}
        onSubmit={() => {}}
      >
        <FormField
          name="username"
          label="Username"
          helperText="Enter your username"
        >
          <TestInput name="username" />
        </FormField>
        <button type="submit">Submit</button>
      </Form>
    )

    expect(screen.getByText('Enter your username')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Submit'))

    await waitFor(() => {
      expect(screen.getByText('Username must be at least 3 characters')).toBeInTheDocument()
      expect(screen.queryByText('Enter your username')).not.toBeInTheDocument()
    })
  })

  it('shows required field indicator', () => {
    renderWithTheme(
      <Form onSubmit={() => {}}>
        <FormField
          name="username"
          label="Username"
          required
        >
          <TestInput name="username" />
        </FormField>
      </Form>
    )

    const label = screen.getByText('Username')
    expect(label.parentElement).toHaveStyle({ content: '*' })
  })
})
