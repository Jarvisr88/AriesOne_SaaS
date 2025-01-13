import React from 'react';
import {
  Box,
  Button,
  Card,
  Grid,
  MenuItem,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import { Save, Preview } from '@mui/icons-material';
import { useReport } from '../hooks/useReport';
import { useCategories } from '../hooks/useCategories';
import { useTemplates } from '../hooks/useTemplates';
import { TemplateEditor } from './TemplateEditor';
import { ReportPreview } from './ReportPreview';

interface ReportEditorProps {
  reportId?: string;
  onSave?: () => void;
}

export const ReportEditor: React.FC<ReportEditorProps> = ({
  reportId,
  onSave,
}) => {
  const [activeTab, setActiveTab] = React.useState(0);
  const [previewOpen, setPreviewOpen] = React.useState(false);

  const {
    report,
    isLoading: reportLoading,
    error: reportError,
    updateReport,
    createReport,
  } = useReport(reportId);

  const { categories } = useCategories();
  const { templates } = useTemplates();

  const [formData, setFormData] = React.useState({
    name: '',
    description: '',
    categoryId: '',
    templateId: '',
    parameters: {},
  });

  React.useEffect(() => {
    if (report) {
      setFormData({
        name: report.name,
        description: report.description || '',
        categoryId: report.category.id,
        templateId: report.template.id,
        parameters: report.parameters,
      });
    }
  }, [report]);

  const handleChange = (field: string) => (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleParameterChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [key]: value,
      },
    }));
  };

  const handleSave = async () => {
    try {
      if (reportId) {
        await updateReport(formData);
      } else {
        await createReport(formData);
      }
      onSave?.();
    } catch (error) {
      console.error('Failed to save report:', error);
    }
  };

  const handlePreview = () => {
    setPreviewOpen(true);
  };

  if (reportError) {
    return (
      <Box p={3}>
        <Typography color="error">
          Error loading report: {reportError.message}
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Card>
        <Box p={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="h6">
              {reportId ? 'Edit Report' : 'New Report'}
            </Typography>
            <Box flex={1} />
            <Button
              variant="outlined"
              startIcon={<Preview />}
              onClick={handlePreview}
            >
              Preview
            </Button>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save
            </Button>
          </Stack>
        </Box>

        <Box p={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Name"
                value={formData.name}
                onChange={handleChange('name')}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                select
                label="Category"
                value={formData.categoryId}
                onChange={handleChange('categoryId')}
                fullWidth
                required
              >
                {categories.map(category => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={formData.description}
                onChange={handleChange('description')}
                fullWidth
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                select
                label="Template"
                value={formData.templateId}
                onChange={handleChange('templateId')}
                fullWidth
                required
              >
                {templates.map(template => (
                  <MenuItem key={template.id} value={template.id}>
                    {template.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        </Box>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={(_, value) => setActiveTab(value)}
            aria-label="report editor tabs"
          >
            <Tab label="Parameters" />
            <Tab label="Template" />
            <Tab label="Styling" />
          </Tabs>
        </Box>

        <Box p={2}>
          {activeTab === 0 && (
            <TemplateEditor
              template={templates.find(t => t.id === formData.templateId)}
              parameters={formData.parameters}
              onChange={handleParameterChange}
            />
          )}
          {activeTab === 1 && (
            <Box p={2}>
              <Typography color="textSecondary">
                Template content editor coming soon...
              </Typography>
            </Box>
          )}
          {activeTab === 2 && (
            <Box p={2}>
              <Typography color="textSecondary">
                Style editor coming soon...
              </Typography>
            </Box>
          )}
        </Box>
      </Card>

      <ReportPreview
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        report={{
          ...report,
          ...formData,
        }}
      />
    </>
  );
};
