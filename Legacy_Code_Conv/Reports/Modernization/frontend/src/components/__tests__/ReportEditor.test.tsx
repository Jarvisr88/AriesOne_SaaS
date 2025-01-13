import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReportEditor } from '../ReportEditor';
import { useReport } from '../../hooks/useReport';
import { useCategories } from '../../hooks/useCategories';
import { useTemplates } from '../../hooks/useTemplates';

// Mock the custom hooks
jest.mock('../../hooks/useReport');
jest.mock('../../hooks/useCategories');
jest.mock('../../hooks/useTemplates');

describe('ReportEditor', () => {
  const mockReport = {
    id: '1',
    name: 'Test Report',
    description: 'Test Description',
    category: { id: '1', name: 'Category 1' },
    template: { id: '1', name: 'Template 1' },
    parameters: {
      title: 'Test Title',
      sections: [
        { id: 'section-1', title: 'Section 1', content: 'Content 1' },
      ],
    },
  };

  const mockCategories = [
    { id: '1', name: 'Category 1' },
    { id: '2', name: 'Category 2' },
  ];

  const mockTemplates = [
    { id: '1', name: 'Template 1', templateType: 'pdf' },
    { id: '2', name: 'Template 2', templateType: 'excel' },
  ];

  const mockHooks = {
    report: {
      report: mockReport,
      isLoading: false,
      error: null,
      updateReport: jest.fn(),
      createReport: jest.fn(),
    },
    categories: {
      categories: mockCategories,
      isLoading: false,
      error: null,
    },
    templates: {
      templates: mockTemplates,
      isLoading: false,
      error: null,
    },
  };

  beforeEach(() => {
    (useReport as jest.Mock).mockReturnValue(mockHooks.report);
    (useCategories as jest.Mock).mockReturnValue(mockHooks.categories);
    (useTemplates as jest.Mock).mockReturnValue(mockHooks.templates);
  });

  it('renders editor with report data', () => {
    render(<ReportEditor reportId="1" />);
    
    expect(screen.getByDisplayValue('Test Report')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test Description')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Category 1')).toBeInTheDocument();
  });

  it('handles form changes', async () => {
    render(<ReportEditor reportId="1" />);
    
    const nameInput = screen.getByLabelText('Name');
    await userEvent.clear(nameInput);
    await userEvent.type(nameInput, 'Updated Report');
    
    expect(nameInput).toHaveValue('Updated Report');
  });

  it('handles category selection', () => {
    render(<ReportEditor reportId="1" />);
    
    const categorySelect = screen.getByLabelText('Category');
    fireEvent.mouseDown(categorySelect);
    
    const option = screen.getByText('Category 2');
    fireEvent.click(option);
    
    expect(categorySelect).toHaveValue('2');
  });

  it('handles template selection', () => {
    render(<ReportEditor reportId="1" />);
    
    const templateSelect = screen.getByLabelText('Template');
    fireEvent.mouseDown(templateSelect);
    
    const option = screen.getByText('Template 2');
    fireEvent.click(option);
    
    expect(templateSelect).toHaveValue('2');
  });

  it('handles save for existing report', async () => {
    const onSave = jest.fn();
    render(<ReportEditor reportId="1" onSave={onSave} />);
    
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(mockHooks.report.updateReport).toHaveBeenCalled();
      expect(onSave).toHaveBeenCalled();
    });
  });

  it('handles save for new report', async () => {
    const onSave = jest.fn();
    render(<ReportEditor onSave={onSave} />);
    
    // Fill required fields
    await userEvent.type(screen.getByLabelText('Name'), 'New Report');
    fireEvent.mouseDown(screen.getByLabelText('Category'));
    fireEvent.click(screen.getByText('Category 1'));
    fireEvent.mouseDown(screen.getByLabelText('Template'));
    fireEvent.click(screen.getByText('Template 1'));
    
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(mockHooks.report.createReport).toHaveBeenCalled();
      expect(onSave).toHaveBeenCalled();
    });
  });

  it('handles preview', () => {
    render(<ReportEditor reportId="1" />);
    
    const previewButton = screen.getByText('Preview');
    fireEvent.click(previewButton);
    
    expect(screen.getByText('Report Preview')).toBeInTheDocument();
  });

  it('displays error state', () => {
    (useReport as jest.Mock).mockReturnValue({
      ...mockHooks.report,
      error: new Error('Failed to load report'),
    });
    
    render(<ReportEditor reportId="1" />);
    expect(screen.getByText(/Failed to load report/)).toBeInTheDocument();
  });

  it('handles tab switching', () => {
    render(<ReportEditor reportId="1" />);
    
    const templateTab = screen.getByText('Template');
    fireEvent.click(templateTab);
    
    expect(screen.getByText('Template content editor coming soon...')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<ReportEditor />);
    
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    
    expect(screen.getByText('Name is required')).toBeInTheDocument();
    expect(screen.getByText('Category is required')).toBeInTheDocument();
    expect(screen.getByText('Template is required')).toBeInTheDocument();
  });
});
