import { useState, useEffect, useCallback } from 'react'
import { Platform } from 'react-native'
import { DeliveryRoute, DeliveryStatus, DeliveryStop } from '../navigation/types'
import DeliveryTracker from './DeliveryTracker'
import { useLocation } from './useLocation'
import { useCamera } from '../utils/useCamera'
import { useSignature } from '../utils/useSignature'
import { storage } from '../utils/storage'

interface UseDeliveryProps {
  onStatusChange?: (status: DeliveryStatus) => void
  onError?: (error: Error) => void
}

interface UseDeliveryReturn {
  currentDelivery: DeliveryRoute | null
  currentStop: DeliveryStop | null
  isLoading: boolean
  error: Error | null
  startDelivery: (deliveryRoute: DeliveryRoute) => Promise<void>
  completeDelivery: () => Promise<void>
  updateStop: (
    stopId: string,
    status: DeliveryStatus,
    data?: {
      notes?: string
      photos?: string[]
      signature?: string
    }
  ) => Promise<void>
  capturePhoto: () => Promise<string>
  captureSignature: () => Promise<string>
  skipStop: (stopId: string, reason: string) => Promise<void>
  addStop: (stop: Omit<DeliveryStop, 'id'>) => Promise<void>
  reorderStops: (stopIds: string[]) => Promise<void>
  optimizeRoute: () => Promise<void>
}

export function useDelivery({
  onStatusChange,
  onError,
}: UseDeliveryProps = {}): UseDeliveryReturn {
  const [currentDelivery, setCurrentDelivery] = useState<DeliveryRoute | null>(null)
  const [currentStop, setCurrentStop] = useState<DeliveryStop | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const { location, startTracking, stopTracking } = useLocation()
  const { captureImage } = useCamera()
  const { captureSignature: getSignature } = useSignature()
  const deliveryTracker = DeliveryTracker.getInstance()

  // Load saved delivery state
  useEffect(() => {
    const loadSavedState = async () => {
      try {
        const savedDelivery = await storage.get<DeliveryRoute>('current_delivery')
        if (savedDelivery) {
          setCurrentDelivery(savedDelivery)
          const activeStop = savedDelivery.stops.find(
            stop => stop.status === 'pending' || stop.status === 'in_progress'
          )
          setCurrentStop(activeStop || null)
        }
      } catch (error) {
        console.error('Error loading saved delivery state:', error)
      }
    }

    loadSavedState()
  }, [])

  // Save delivery state changes
  useEffect(() => {
    if (currentDelivery) {
      storage.set('current_delivery', currentDelivery)
    } else {
      storage.remove('current_delivery')
    }
  }, [currentDelivery])

  const startDelivery = useCallback(async (deliveryRoute: DeliveryRoute) => {
    try {
      setIsLoading(true)
      setError(null)

      await startTracking()
      await deliveryTracker.startDelivery(deliveryRoute)

      setCurrentDelivery(deliveryRoute)
      setCurrentStop(deliveryRoute.stops[0])
      onStatusChange?.('in_progress')
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to start delivery')
      setError(error)
      onError?.(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [startTracking, onStatusChange, onError])

  const completeDelivery = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      await deliveryTracker.stopDelivery()
      await stopTracking()

      setCurrentDelivery(null)
      setCurrentStop(null)
      onStatusChange?.('completed')
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to complete delivery')
      setError(error)
      onError?.(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [stopTracking, onStatusChange, onError])

  const updateStop = useCallback(async (
    stopId: string,
    status: DeliveryStatus,
    data?: {
      notes?: string
      photos?: string[]
      signature?: string
    }
  ) => {
    if (!currentDelivery) {
      throw new Error('No active delivery')
    }

    try {
      setIsLoading(true)
      setError(null)

      await deliveryTracker.updateStop(stopId, status, data)

      // Update local state
      const updatedDelivery = {
        ...currentDelivery,
        stops: currentDelivery.stops.map(stop =>
          stop.id === stopId
            ? { ...stop, status, ...data }
            : stop
        ),
      }
      setCurrentDelivery(updatedDelivery)

      // Move to next stop if completed
      if (status === 'completed') {
        const nextStop = updatedDelivery.stops.find(stop => stop.status === 'pending')
        setCurrentStop(nextStop || null)
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update stop')
      setError(error)
      onError?.(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [currentDelivery, onError])

  const capturePhoto = useCallback(async () => {
    try {
      const photo = await captureImage()
      return photo
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to capture photo')
      setError(error)
      onError?.(error)
      throw error
    }
  }, [captureImage, onError])

  const captureSignature = useCallback(async () => {
    try {
      const signature = await getSignature()
      return signature
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to capture signature')
      setError(error)
      onError?.(error)
      throw error
    }
  }, [getSignature, onError])

  const skipStop = useCallback(async (stopId: string, reason: string) => {
    try {
      await updateStop(stopId, 'failed', { notes: reason })
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to skip stop')
      setError(error)
      onError?.(error)
      throw error
    }
  }, [updateStop, onError])

  const addStop = useCallback(async (stop: Omit<DeliveryStop, 'id'>) => {
    if (!currentDelivery) {
      throw new Error('No active delivery')
    }

    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch('/api/delivery/stops', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          deliveryId: currentDelivery.id,
          stop,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to add stop')
      }

      const newStop = await response.json()
      const updatedDelivery = {
        ...currentDelivery,
        stops: [...currentDelivery.stops, newStop],
      }
      setCurrentDelivery(updatedDelivery)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to add stop')
      setError(error)
      onError?.(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [currentDelivery, onError])

  const reorderStops = useCallback(async (stopIds: string[]) => {
    if (!currentDelivery) {
      throw new Error('No active delivery')
    }

    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`/api/delivery/${currentDelivery.id}/reorder`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ stopIds }),
      })

      if (!response.ok) {
        throw new Error('Failed to reorder stops')
      }

      const updatedStops = stopIds.map(
        id => currentDelivery.stops.find(stop => stop.id === id)!
      )
      const updatedDelivery = {
        ...currentDelivery,
        stops: updatedStops,
      }
      setCurrentDelivery(updatedDelivery)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to reorder stops')
      setError(error)
      onError?.(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [currentDelivery, onError])

  const optimizeRoute = useCallback(async () => {
    if (!currentDelivery) {
      throw new Error('No active delivery')
    }

    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`/api/delivery/${currentDelivery.id}/optimize`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to optimize route')
      }

      const optimizedRoute = await response.json()
      setCurrentDelivery(optimizedRoute)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to optimize route')
      setError(error)
      onError?.(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [currentDelivery, onError])

  return {
    currentDelivery,
    currentStop,
    isLoading,
    error,
    startDelivery,
    completeDelivery,
    updateStop,
    capturePhoto,
    captureSignature,
    skipStop,
    addStop,
    reorderStops,
    optimizeRoute,
  }
}

// Example usage:
/*
function DeliveryScreen() {
  const {
    currentDelivery,
    currentStop,
    isLoading,
    error,
    updateStop,
    capturePhoto,
    captureSignature,
    skipStop,
  } = useDelivery({
    onStatusChange: (status) => {
      console.log('Delivery status changed:', status)
    },
    onError: (error) => {
      console.error('Delivery error:', error)
    },
  })

  const handleCompleteStop = async () => {
    if (!currentStop) return

    try {
      // Capture proof of delivery
      const [photo] = await Promise.all([
        capturePhoto(),
        captureSignature(),
      ])

      // Update stop status
      await updateStop(currentStop.id, 'completed', {
        photos: [photo],
        signature,
        notes: 'Delivered successfully',
      })
    } catch (error) {
      console.error('Error completing stop:', error)
    }
  }

  return (
    <View>
      <DeliveryMap
        delivery={currentDelivery}
        currentStop={currentStop}
      />
      <StopDetails
        stop={currentStop}
        onComplete={handleCompleteStop}
        onSkip={(reason) => skipStop(currentStop?.id, reason)}
      />
    </View>
  )
}
*/
