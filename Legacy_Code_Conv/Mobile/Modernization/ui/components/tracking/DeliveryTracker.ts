import { Platform } from 'react-native'
import { DeliveryStatus, Location, DeliveryRoute, DeliveryStop } from '../navigation/types'
import LocationService from './LocationService'
import { storage } from '../utils/storage'

interface DeliveryUpdate {
  deliveryId: string
  location: Location
  status: DeliveryStatus
  timestamp: number
  notes?: string
  photos?: string[]
  signature?: string
}

interface DeliveryTrackerConfig {
  updateInterval: number
  maxRetries: number
  retryDelay: number
  offlineStorageKey: string
}

class DeliveryTracker {
  private static instance: DeliveryTracker
  private locationService: LocationService
  private currentDelivery?: DeliveryRoute
  private updateInterval?: NodeJS.Timeout
  private offlineUpdates: DeliveryUpdate[] = []
  private config: DeliveryTrackerConfig = {
    updateInterval: 30000, // 30 seconds
    maxRetries: 3,
    retryDelay: 5000, // 5 seconds
    offlineStorageKey: 'offline_delivery_updates',
  }

  private constructor() {
    this.locationService = LocationService.getInstance()
    this.loadOfflineUpdates()
  }

  public static getInstance(): DeliveryTracker {
    if (!DeliveryTracker.instance) {
      DeliveryTracker.instance = new DeliveryTracker()
    }
    return DeliveryTracker.instance
  }

  public async startDelivery(deliveryRoute: DeliveryRoute): Promise<void> {
    try {
      this.currentDelivery = deliveryRoute
      await this.locationService.startTracking()
      
      // Start periodic updates
      this.updateInterval = setInterval(
        this.sendLocationUpdate.bind(this),
        this.config.updateInterval
      )

      // Update delivery status
      await this.updateDeliveryStatus(deliveryRoute.id, 'in_progress')

      // Sync any offline updates
      await this.syncOfflineUpdates()
    } catch (error) {
      console.error('Error starting delivery:', error)
      throw error
    }
  }

  public async stopDelivery(): Promise<void> {
    try {
      if (this.currentDelivery) {
        await this.updateDeliveryStatus(this.currentDelivery.id, 'completed')
      }

      // Clear tracking
      if (this.updateInterval) {
        clearInterval(this.updateInterval)
      }
      await this.locationService.stopTracking()
      this.currentDelivery = undefined

      // Final sync attempt
      await this.syncOfflineUpdates()
    } catch (error) {
      console.error('Error stopping delivery:', error)
      throw error
    }
  }

  public async updateStop(
    stopId: string,
    status: DeliveryStatus,
    data?: {
      notes?: string
      photos?: string[]
      signature?: string
    }
  ): Promise<void> {
    if (!this.currentDelivery) {
      throw new Error('No active delivery')
    }

    try {
      const location = await this.locationService.getCurrentLocation()
      const update: DeliveryUpdate = {
        deliveryId: this.currentDelivery.id,
        location,
        status,
        timestamp: Date.now(),
        ...data,
      }

      await this.sendUpdate(update)
      await this.updateDeliveryProgress()
    } catch (error) {
      console.error('Error updating delivery stop:', error)
      throw error
    }
  }

  private async sendLocationUpdate(): Promise<void> {
    if (!this.currentDelivery) return

    try {
      const location = await this.locationService.getCurrentLocation()
      const update: DeliveryUpdate = {
        deliveryId: this.currentDelivery.id,
        location,
        status: 'in_progress',
        timestamp: Date.now(),
      }

      await this.sendUpdate(update)
    } catch (error) {
      console.error('Error sending location update:', error)
    }
  }

  private async sendUpdate(update: DeliveryUpdate, retryCount = 0): Promise<void> {
    try {
      const response = await fetch('/api/delivery/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(update),
      })

      if (!response.ok) {
        throw new Error('Failed to send update')
      }
    } catch (error) {
      // Handle offline scenario
      if (!navigator.onLine || retryCount >= this.config.maxRetries) {
        await this.storeOfflineUpdate(update)
        return
      }

      // Retry with exponential backoff
      await new Promise(resolve => 
        setTimeout(resolve, this.config.retryDelay * Math.pow(2, retryCount))
      )
      await this.sendUpdate(update, retryCount + 1)
    }
  }

  private async updateDeliveryStatus(
    deliveryId: string,
    status: DeliveryStatus
  ): Promise<void> {
    try {
      const response = await fetch(`/api/delivery/${deliveryId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      })

      if (!response.ok) {
        throw new Error('Failed to update delivery status')
      }
    } catch (error) {
      console.error('Error updating delivery status:', error)
      throw error
    }
  }

  private async updateDeliveryProgress(): Promise<void> {
    if (!this.currentDelivery) return

    const completedStops = this.currentDelivery.stops.filter(
      stop => stop.status === 'completed'
    )

    if (completedStops.length === this.currentDelivery.stops.length) {
      await this.stopDelivery()
    }
  }

  private async storeOfflineUpdate(update: DeliveryUpdate): Promise<void> {
    this.offlineUpdates.push(update)
    await storage.set(this.config.offlineStorageKey, this.offlineUpdates)
  }

  private async loadOfflineUpdates(): Promise<void> {
    const updates = await storage.get<DeliveryUpdate[]>(this.config.offlineStorageKey)
    if (updates) {
      this.offlineUpdates = updates
    }
  }

  private async syncOfflineUpdates(): Promise<void> {
    if (!navigator.onLine || this.offlineUpdates.length === 0) return

    const updates = [...this.offlineUpdates]
    this.offlineUpdates = []
    await storage.set(this.config.offlineStorageKey, this.offlineUpdates)

    for (const update of updates) {
      try {
        await this.sendUpdate(update)
      } catch (error) {
        console.error('Error syncing offline update:', error)
        // Put failed updates back in the queue
        this.offlineUpdates.push(update)
      }
    }

    await storage.set(this.config.offlineStorageKey, this.offlineUpdates)
  }
}

export default DeliveryTracker
