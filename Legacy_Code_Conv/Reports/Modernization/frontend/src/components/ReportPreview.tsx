import React from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material';
import { Close, FileDownload } from '@mui/icons-material';
import { Report } from '../types/report';
import { useReportPreview } from '../hooks/useReportPreview';

interface ReportPreviewProps {
  open: boolean;
  onClose: () => void;
  report: Report;
}

export const ReportPreview: React.FC<ReportPreviewProps> = ({
  open,
  onClose,
  report,
}) => {
  const [format, setFormat] = React.useState<'pdf' | 'excel' | 'csv'>('pdf');
  const [previewScale, setPreviewScale] = React.useState(1);

  const {
    previewUrl,
    isLoading,
    error,
    generatePreview,
    downloadReport,
  } = useReportPreview();

  React.useEffect(() => {
    if (open && report) {
      generatePreview(report.id, format);
    }
  }, [open, report, format]);

  const handleFormatChange = (
    _: React.MouseEvent<HTMLElement>,
    newFormat: 'pdf' | 'excel' | 'csv',
  ) => {
    if (newFormat) {
      setFormat(newFormat);
    }
  };

  const handleZoomIn = () => {
    setPreviewScale(prev => Math.min(prev + 0.25, 2));
  };

  const handleZoomOut = () => {
    setPreviewScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleDownload = async () => {
    await downloadReport(report.id, format);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      <DialogTitle>
        <Stack
          direction="row"
          spacing={2}
          alignItems="center"
          justifyContent="space-between"
        >
          <Typography variant="h6">Report Preview</Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <ToggleButtonGroup
              value={format}
              exclusive
              onChange={handleFormatChange}
              size="small"
            >
              <ToggleButton value="pdf">PDF</ToggleButton>
              <ToggleButton value="excel">Excel</ToggleButton>
              <ToggleButton value="csv">CSV</ToggleButton>
            </ToggleButtonGroup>
            <IconButton onClick={onClose} size="small">
              <Close />
            </IconButton>
          </Stack>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {isLoading ? (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            height="100%"
          >
            <Typography>Loading preview...</Typography>
          </Box>
        ) : error ? (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            height="100%"
          >
            <Typography color="error">
              Error loading preview: {error.message}
            </Typography>
          </Box>
        ) : (
          <Box
            sx={{
              height: '100%',
              overflow: 'auto',
              bgcolor: 'grey.100',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {format === 'pdf' ? (
              <Box
                component="iframe"
                src={previewUrl}
                sx={{
                  width: `${100 * previewScale}%`,
                  height: '100%',
                  border: 'none',
                  transition: 'width 0.3s ease',
                }}
              />
            ) : (
              <Box
                sx={{
                  p: 3,
                  bgcolor: 'background.paper',
                  borderRadius: 1,
                  boxShadow: 1,
                }}
              >
                <Typography>
                  Preview not available for {format.toUpperCase()} format.
                  Please download to view.
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Stack
          direction="row"
          spacing={2}
          alignItems="center"
          sx={{ width: '100%', px: 2 }}
        >
          {format === 'pdf' && (
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                size="small"
                onClick={handleZoomOut}
                disabled={previewScale <= 0.5}
              >
                Zoom Out
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={handleZoomIn}
                disabled={previewScale >= 2}
              >
                Zoom In
              </Button>
            </Stack>
          )}
          <Box flex={1} />
          <Button
            variant="contained"
            startIcon={<FileDownload />}
            onClick={handleDownload}
          >
            Download
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>
  );
};
