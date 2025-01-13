import React from 'react';
import {
  Box,
  Button,
  Card,
  Checkbox,
  IconButton,
  Menu,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Delete,
  Edit,
  FileCopy,
  FileDownload,
  History,
  MoreVert,
  Search,
} from '@mui/icons-material';
import { useReports } from '../hooks/useReports';
import { SearchFilters } from '../types/report';
import { formatDate } from '../utils/date';

export const ReportList: React.FC = () => {
  const [filters, setFilters] = React.useState<SearchFilters>({
    searchText: '',
    categoryId: null,
    isSystem: null,
    offset: 0,
    limit: 20,
  });

  const [selectedReports, setSelectedReports] = React.useState<string[]>([]);
  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [activeReport, setActiveReport] = React.useState<string | null>(null);

  const {
    reports,
    totalCount,
    isLoading,
    error,
    deleteReports,
    cloneReport,
    exportReport,
  } = useReports(filters);

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({
      ...prev,
      searchText: event.target.value,
      offset: 0,
    }));
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedReports(reports.map(report => report.id));
    } else {
      setSelectedReports([]);
    }
  };

  const handleSelectReport = (reportId: string) => {
    setSelectedReports(prev => {
      if (prev.includes(reportId)) {
        return prev.filter(id => id !== reportId);
      }
      return [...prev, reportId];
    });
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, reportId: string) => {
    setMenuAnchor(event.currentTarget);
    setActiveReport(reportId);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setActiveReport(null);
  };

  const handleClone = async () => {
    if (!activeReport) return;
    await cloneReport(activeReport);
    handleMenuClose();
  };

  const handleDelete = async () => {
    if (selectedReports.length === 0) return;
    await deleteReports(selectedReports);
    setSelectedReports([]);
  };

  const handleExport = async (format: 'pdf' | 'excel' | 'csv') => {
    if (!activeReport) return;
    await exportReport(activeReport, format);
    handleMenuClose();
  };

  if (error) {
    return (
      <Box p={3}>
        <Typography color="error">Error loading reports: {error.message}</Typography>
      </Box>
    );
  }

  return (
    <Card>
      <Box p={2}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            placeholder="Search reports..."
            value={filters.searchText}
            onChange={handleSearch}
            InputProps={{
              startAdornment: <Search color="action" />,
            }}
            size="small"
            sx={{ width: 300 }}
          />
          <Box flex={1} />
          {selectedReports.length > 0 && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDelete}
            >
              Delete Selected ({selectedReports.length})
            </Button>
          )}
        </Stack>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={
                    selectedReports.length > 0 &&
                    selectedReports.length < reports.length
                  }
                  checked={
                    reports.length > 0 &&
                    selectedReports.length === reports.length
                  }
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Created By</TableCell>
              <TableCell>Last Modified</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.map(report => (
              <TableRow
                key={report.id}
                hover
                selected={selectedReports.includes(report.id)}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedReports.includes(report.id)}
                    onChange={() => handleSelectReport(report.id)}
                    disabled={report.isSystem}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{report.name}</Typography>
                  {report.description && (
                    <Typography variant="caption" color="textSecondary">
                      {report.description}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>{report.category.name}</TableCell>
                <TableCell>{report.createdBy}</TableCell>
                <TableCell>{formatDate(report.updatedAt)}</TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => {/* TODO: Implement edit */}}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="History">
                      <IconButton
                        size="small"
                        onClick={() => {/* TODO: Implement history */}}
                      >
                        <History fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <IconButton
                      size="small"
                      onClick={e => handleMenuOpen(e, report.id)}
                    >
                      <MoreVert fontSize="small" />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleClone}>
          <FileCopy fontSize="small" sx={{ mr: 1 }} />
          Clone
        </MenuItem>
        <MenuItem onClick={() => handleExport('pdf')}>
          <FileDownload fontSize="small" sx={{ mr: 1 }} />
          Export as PDF
        </MenuItem>
        <MenuItem onClick={() => handleExport('excel')}>
          <FileDownload fontSize="small" sx={{ mr: 1 }} />
          Export as Excel
        </MenuItem>
        <MenuItem onClick={() => handleExport('csv')}>
          <FileDownload fontSize="small" sx={{ mr: 1 }} />
          Export as CSV
        </MenuItem>
      </Menu>
    </Card>
  );
};
