import React from 'react';
import {
  Box,
  Card,
  Grid,
  IconButton,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { Add, Delete } from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { ReportTemplate } from '../types/report';

interface TemplateEditorProps {
  template?: ReportTemplate;
  parameters: Record<string, any>;
  onChange: (key: string, value: any) => void;
}

export const TemplateEditor: React.FC<TemplateEditorProps> = ({
  template,
  parameters,
  onChange,
}) => {
  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const items = Array.from(parameters.sections || []);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    onChange('sections', items);
  };

  const handleAddSection = () => {
    const sections = parameters.sections || [];
    onChange('sections', [
      ...sections,
      {
        id: `section-${sections.length + 1}`,
        title: '',
        content: '',
      },
    ]);
  };

  const handleRemoveSection = (index: number) => {
    const sections = Array.from(parameters.sections || []);
    sections.splice(index, 1);
    onChange('sections', sections);
  };

  const handleSectionChange = (index: number, field: string, value: any) => {
    const sections = Array.from(parameters.sections || []);
    sections[index] = {
      ...sections[index],
      [field]: value,
    };
    onChange('sections', sections);
  };

  if (!template) {
    return (
      <Box p={3}>
        <Typography color="textSecondary">
          Please select a template to configure parameters
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Stack spacing={2}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              label="Title"
              value={parameters.title || ''}
              onChange={e => onChange('title', e.target.value)}
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              label="Subtitle"
              value={parameters.subtitle || ''}
              onChange={e => onChange('subtitle', e.target.value)}
              fullWidth
            />
          </Grid>
        </Grid>

        <Box>
          <Stack
            direction="row"
            spacing={2}
            alignItems="center"
            sx={{ mb: 2 }}
          >
            <Typography variant="subtitle1">Sections</Typography>
            <IconButton
              color="primary"
              onClick={handleAddSection}
              size="small"
            >
              <Add />
            </IconButton>
          </Stack>

          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="sections">
              {provided => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                >
                  {(parameters.sections || []).map((section: any, index: number) => (
                    <Draggable
                      key={section.id}
                      draggableId={section.id}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <Card
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          sx={{
                            p: 2,
                            mb: 2,
                            bgcolor: snapshot.isDragging
                              ? 'action.hover'
                              : 'background.paper',
                          }}
                        >
                          <Stack spacing={2}>
                            <Stack
                              direction="row"
                              spacing={2}
                              alignItems="center"
                            >
                              <div {...provided.dragHandleProps}>
                                <Typography
                                  variant="subtitle2"
                                  sx={{ cursor: 'move' }}
                                >
                                  Section {index + 1}
                                </Typography>
                              </div>
                              <Box flex={1} />
                              <IconButton
                                size="small"
                                onClick={() => handleRemoveSection(index)}
                              >
                                <Delete />
                              </IconButton>
                            </Stack>

                            <TextField
                              label="Title"
                              value={section.title}
                              onChange={e =>
                                handleSectionChange(
                                  index,
                                  'title',
                                  e.target.value,
                                )
                              }
                              fullWidth
                            />

                            <TextField
                              label="Content"
                              value={section.content}
                              onChange={e =>
                                handleSectionChange(
                                  index,
                                  'content',
                                  e.target.value,
                                )
                              }
                              fullWidth
                              multiline
                              rows={4}
                            />
                          </Stack>
                        </Card>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </Box>

        {template.templateType === 'pdf' && (
          <Card sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              PDF Settings
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  label="Page Size"
                  value={parameters.pageSize || 'A4'}
                  onChange={e => onChange('pageSize', e.target.value)}
                  fullWidth
                >
                  <MenuItem value="A4">A4</MenuItem>
                  <MenuItem value="Letter">Letter</MenuItem>
                  <MenuItem value="Legal">Legal</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  label="Orientation"
                  value={parameters.orientation || 'portrait'}
                  onChange={e => onChange('orientation', e.target.value)}
                  fullWidth
                >
                  <MenuItem value="portrait">Portrait</MenuItem>
                  <MenuItem value="landscape">Landscape</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </Card>
        )}

        {template.templateType === 'excel' && (
          <Card sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Excel Settings
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Sheet Name"
                  value={parameters.sheetName || ''}
                  onChange={e => onChange('sheetName', e.target.value)}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  type="number"
                  label="Freeze Rows"
                  value={parameters.freezeRows || 0}
                  onChange={e =>
                    onChange('freezeRows', parseInt(e.target.value, 10))
                  }
                  fullWidth
                />
              </Grid>
            </Grid>
          </Card>
        )}
      </Stack>
    </Box>
  );
};
