/**
 * ICD code management component with search and bulk updates.
 */
import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GridReadyEvent } from 'ag-grid-community';
import { ICDCode, ICDCodeType } from '../types';
import { useICDCodes } from '../hooks/useICDCodes';
import { Button } from './common/Button';
import { Spinner } from './common/Spinner';
import { ErrorMessage } from './common/ErrorMessage';
import { SearchInput } from './common/SearchInput';
import { ImportModal } from './ImportModal';

interface ICDCodeManagerProps {
  codeType: ICDCodeType;
}

export const ICDCodeManager: React.FC<ICDCodeManagerProps> = ({
  codeType,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showImport, setShowImport] = useState(false);
  const [gridApi, setGridApi] = useState(null);
  const [selectedCodes, setSelectedCodes] = useState<ICDCode[]>([]);

  const {
    codes,
    loading,
    error,
    updateCodes,
    fetchCodes,
  } = useICDCodes(codeType);

  const columnDefs: ColDef[] = [
    {
      field: 'code',
      headerName: 'Code',
      sortable: true,
      filter: true,
      checkboxSelection: true,
    },
    {
      field: 'description',
      headerName: 'Description',
      sortable: true,
      filter: true,
      flex: 1,
      editable: true,
    },
    {
      field: 'effective_date',
      headerName: 'Effective Date',
      sortable: true,
      filter: true,
      valueFormatter: (params) =>
        params.value ? new Date(params.value).toLocaleDateString() : '',
    },
    {
      field: 'is_active',
      headerName: 'Active',
      sortable: true,
      filter: true,
      cellRenderer: 'agCheckboxCellRenderer',
      cellEditor: 'agCheckboxCellEditor',
      editable: true,
    },
  ];

  const defaultColDef = {
    resizable: true,
  };

  const onGridReady = (params: GridReadyEvent) => {
    setGridApi(params.api);
    params.api.sizeColumnsToFit();
  };

  const onSelectionChanged = () => {
    const selectedRows = gridApi?.getSelectedRows() || [];
    setSelectedCodes(selectedRows);
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    if (gridApi) {
      gridApi.setQuickFilter(value);
    }
  };

  const handleImport = async (importedCodes: ICDCode[]) => {
    try {
      await updateCodes(importedCodes);
      await fetchCodes();
      setShowImport(false);
    } catch (error) {
      console.error('Failed to import codes:', error);
    }
  };

  const handleDeactivate = async () => {
    if (!selectedCodes.length || !window.confirm('Deactivate selected codes?')) {
      return;
    }

    const updatedCodes = selectedCodes.map(code => ({
      ...code,
      is_active: false,
      deactivation_date: new Date().toISOString(),
    }));

    try {
      await updateCodes(updatedCodes);
      await fetchCodes();
    } catch (error) {
      console.error('Failed to deactivate codes:', error);
    }
  };

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">
          {codeType === ICDCodeType.ICD9 ? 'ICD-9' : 'ICD-10'} Code Manager
        </h2>
        <div className="space-x-4">
          <Button
            disabled={selectedCodes.length === 0}
            variant="danger"
            onClick={handleDeactivate}
          >
            Deactivate Selected
          </Button>
          <Button
            variant="primary"
            onClick={() => setShowImport(true)}
          >
            Import Codes
          </Button>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <SearchInput
          value={searchTerm}
          onChange={handleSearch}
          placeholder="Search codes or descriptions..."
          className="w-96"
        />
        <div className="text-sm text-gray-500">
          {codes.length} codes found
        </div>
      </div>

      <div className="h-[600px] w-full ag-theme-alpine">
        <AgGridReact
          rowData={codes}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          onGridReady={onGridReady}
          rowSelection="multiple"
          onSelectionChanged={onSelectionChanged}
          enableCellTextSelection
          ensureDomOrder
          pagination
          paginationPageSize={100}
        />
      </div>

      {showImport && (
        <ImportModal
          codeType={codeType}
          onImport={handleImport}
          onClose={() => setShowImport(false)}
        />
      )}
    </div>
  );
};
