export interface InventoryItem {
  id: string
  sku: string
  name: string
  description: string
  category: string
  quantity: number
  unit: string
  location: {
    warehouse: string
    zone: string
    shelf: string
    bin: string
  }
  status: InventoryStatus
  lastUpdated: string
  minimumStock: number
  maximumStock: number
  reorderPoint: number
  supplier: {
    id: string
    name: string
    leadTime: number
  }
  barcodes: string[]
  serialNumbers?: string[]
  expirationDate?: string
  batchNumber?: string
  notes?: string
}

export type InventoryStatus =
  | 'in_stock'
  | 'low_stock'
  | 'out_of_stock'
  | 'discontinued'
  | 'on_hold'

export interface StockMovement {
  id: string
  itemId: string
  type: 'receive' | 'dispatch' | 'transfer' | 'adjust' | 'return'
  quantity: number
  fromLocation?: {
    warehouse: string
    zone: string
    shelf: string
    bin: string
  }
  toLocation?: {
    warehouse: string
    zone: string
    shelf: string
    bin: string
  }
  timestamp: string
  orderId?: string
  userId: string
  notes?: string
}

export interface InventoryCount {
  id: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  startTime: string
  endTime?: string
  location: {
    warehouse: string
    zone: string
    shelf?: string
    bin?: string
  }
  assignedTo: string[]
  items: InventoryCountItem[]
}

export interface InventoryCountItem {
  itemId: string
  expectedQuantity: number
  actualQuantity?: number
  variance?: number
  notes?: string
  scannedBarcodes?: string[]
  countedBy?: string
  countedAt?: string
}

export interface StockAudit {
  id: string
  countId: string
  createdAt: string
  createdBy: string
  type: 'variance' | 'discrepancy' | 'damage' | 'expiry'
  status: 'open' | 'in_progress' | 'resolved' | 'cancelled'
  items: StockAuditItem[]
  notes: string
  attachments?: string[]
  resolution?: {
    action: 'adjust' | 'recount' | 'investigate' | 'write_off'
    resolvedBy: string
    resolvedAt: string
    notes: string
  }
}

export interface StockAuditItem {
  itemId: string
  reason: string
  quantity: number
  expectedQuantity: number
  variance: number
  action?: 'adjust' | 'recount' | 'investigate' | 'write_off'
  notes?: string
  images?: string[]
}

export interface InventoryTransfer {
  id: string
  status: 'draft' | 'pending' | 'completed' | 'cancelled'
  sourceType: 'vehicle' | 'warehouse'
  sourceId: string
  destinationType: 'vehicle' | 'warehouse'
  destinationId: string
  items: TransferItem[]
  notes: string
  createdAt: string
  createdBy: string
  completedAt?: string
  completedBy?: string
}

export interface TransferItem {
  itemId: string
  barcode: string
  quantity: number
  notes: string
}

export interface MaintenanceTag {
  id: string
  itemId: string
  type: 'repair' | 'inspection' | 'calibration' | 'cleaning' | 'replacement'
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  description: string
  scheduledDate: string
  estimatedDuration: number // in minutes
  images?: string[]
  createdAt: string
  createdBy: string
  assignedTo?: string
  completedAt?: string
  completedBy?: string
  resolution?: {
    notes: string
    parts?: string[]
    cost?: number
  }
}

export interface PurchaseOrder {
  id: string
  status: 'pending' | 'partial' | 'received' | 'cancelled'
  vendorId: string
  items: {
    itemId: string
    quantity: number
    unitPrice: number
    notes?: string
  }[]
  orderDate: string
  expectedDeliveryDate?: string
  notes?: string
}

export interface PurchaseReceival {
  purchaseOrderId: string
  warehouseId: string
  receivedAt: string
  receivedBy: string
  items: {
    itemId: string
    orderedQuantity: number
    receivedQuantity: number
    notes?: string
  }[]
}

export interface CycleCount {
  id: string
  warehouseId: string
  zone: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  startTime: string
  endTime?: string
  items: CycleCountItem[]
  createdBy: string
  completedBy?: string
}

export interface CycleCountItem {
  itemId: string
  expectedQuantity: number
  scannedQuantity?: number
  variance?: number
  barcode: string
  lastScannedAt?: string
  notes?: string
}

export interface Warehouse {
  id: string
  name: string
  code: string
  address: string
  zones: WarehouseZone[]
  isActive: boolean
}

export interface WarehouseZone {
  id: string
  name: string
  code: string
  type: 'storage' | 'receiving' | 'shipping' | 'staging'
  capacity: number
  currentOccupancy: number
}
