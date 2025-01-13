import { NavigatorScreenParams } from '@react-navigation/native'

export type RootStackParamList = {
  Main: NavigatorScreenParams<MainTabParamList>
  DeliveryDetails: { id: string }
  InventoryScanner: undefined
  ServiceOrder: { id: string }
  Settings: undefined
}

export type MainTabParamList = {
  Home: undefined
  Deliveries: undefined
  Inventory: undefined
  Profile: undefined
}

export type DeliveryStatus = 
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface Location {
  latitude: number
  longitude: number
  timestamp: number
  accuracy?: number
  altitude?: number
  speed?: number
  heading?: number
}

export interface DeliveryRoute {
  id: string
  stops: DeliveryStop[]
  startTime: string
  endTime?: string
  status: DeliveryStatus
  assignedTo: string
  vehicleId?: string
  notes?: string
}

export interface DeliveryStop {
  id: string
  orderId: string
  location: {
    latitude: number
    longitude: number
    address: string
  }
  customer: {
    id: string
    name: string
    phone: string
  }
  timeWindow: {
    start: string
    end: string
  }
  status: DeliveryStatus
  notes?: string
  signature?: string
  photos?: string[]
}

export interface NavigationTheme {
  dark: boolean
  colors: {
    primary: string
    background: string
    card: string
    text: string
    border: string
    notification: string
  }
}
