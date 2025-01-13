/**
 * Price list editor component with grid editing and bulk updates.
 */
import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ValueSetterParams, GridReadyEvent } from 'ag-grid-community';
import { PriceListItem, PriceType, PriceCategory } from '../types';
import { formatCurrency, parsePrice } from '../utils/formatters';
import { usePriceList } from '../hooks/usePriceList';
import { Button } from './common/Button';
import { Spinner } from './common/Spinner';
import { ErrorMessage } from './common/ErrorMessage';
import { BulkUpdateModal } from './BulkUpdateModal';

interface PriceListEditorProps {
  companyId: string;
  onSave?: () => void;
}

export const PriceListEditor: React.FC<PriceListEditorProps> = ({
  companyId,
  onSave,
}) => {
  const [selectedItems, setSelectedItems] = useState<PriceListItem[]>([]);
  const [showBulkUpdate, setShowBulkUpdate] = useState(false);
  const [gridApi, setGridApi] = useState(null);

  const {
    priceList,
    loading,
    error,
    updatePrices,
    fetchPriceList,
  } = usePriceList(companyId);

  const columnDefs: ColDef[] = [
    {
      field: 'item_code',
      headerName: 'Item Code',
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
    },
    {
      field: 'price_type',
      headerName: 'Price Type',
      sortable: true,
      filter: true,
      cellEditor: 'agSelectCellEditor',
      cellEditorParams: {
        values: Object.values(PriceType),
      },
    },
    {
      field: 'rental_price',
      headerName: 'Rental Price',
      sortable: true,
      filter: 'agNumberColumnFilter',
      editable: true,
      valueFormatter: (params) => formatCurrency(params.value),
      valueSetter: (params: ValueSetterParams) => {
        const newValue = parsePrice(params.newValue);
        if (newValue !== null) {
          params.data.rental_price = newValue;
          return true;
        }
        return false;
      },
    },
    {
      field: 'sale_price',
      headerName: 'Sale Price',
      sortable: true,
      filter: 'agNumberColumnFilter',
      editable: true,
      valueFormatter: (params) => formatCurrency(params.value),
      valueSetter: (params: ValueSetterParams) => {
        const newValue = parsePrice(params.newValue);
        if (newValue !== null) {
          params.data.sale_price = newValue;
          return true;
        }
        return false;
      },
    },
    {
      field: 'allowable_price',
      headerName: 'Allowable',
      sortable: true,
      filter: 'agNumberColumnFilter',
      editable: true,
      valueFormatter: (params) => formatCurrency(params.value),
      valueSetter: (params: ValueSetterParams) => {
        const newValue = parsePrice(params.newValue);
        if (newValue !== null) {
          params.data.allowable_price = newValue;
          return true;
        }
        return false;
      },
    },
    {
      field: 'billable_price',
      headerName: 'Billable',
      sortable: true,
      filter: 'agNumberColumnFilter',
      editable: true,
      valueFormatter: (params) => formatCurrency(params.value),
      valueSetter: (params: ValueSetterParams) => {
        const newValue = parsePrice(params.newValue);
        if (newValue !== null) {
          params.data.billable_price = newValue;
          return true;
        }
        return false;
      },
    },
    {
      field: 'effective_date',
      headerName: 'Effective Date',
      sortable: true,
      filter: true,
      valueFormatter: (params) =>
        params.value ? new Date(params.value).toLocaleDateString() : '',
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
    setSelectedItems(selectedRows);
  };

  const handleBulkUpdate = async (updateData: any) => {
    try {
      await updatePrices({
        item_codes: selectedItems.map((item) => item.item_code),
        ...updateData,
      });
      await fetchPriceList();
      setShowBulkUpdate(false);
    } catch (error) {
      console.error('Failed to update prices:', error);
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
        <h2 className="text-2xl font-bold">Price List Editor</h2>
        <div className="space-x-4">
          <Button
            disabled={selectedItems.length === 0}
            onClick={() => setShowBulkUpdate(true)}
          >
            Bulk Update
          </Button>
          <Button
            variant="primary"
            onClick={onSave}
          >
            Save Changes
          </Button>
        </div>
      </div>

      <div className="h-[600px] w-full ag-theme-alpine">
        <AgGridReact
          rowData={priceList}
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

      {showBulkUpdate && (
        <BulkUpdateModal
          selectedItems={selectedItems}
          onUpdate={handleBulkUpdate}
          onClose={() => setShowBulkUpdate(false)}
        />
      )}
    </div>
  );
};
