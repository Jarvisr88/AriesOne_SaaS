import { useState, useEffect, useCallback } from 'react'
import { PermissionsAndroid, Platform } from 'react-native'
import { Location } from '../navigation/types'
import LocationService from './LocationService'

interface UseLocationReturn {
  location: Location | null
  isTracking: boolean
  error: Error | null
  startTracking: () => Promise<void>
  stopTracking: () => Promise<void>
  getCurrentLocation: () => Promise<Location>
}

export function useLocation(): UseLocationReturn {
  const [location, setLocation] = useState<Location | null>(null)
  const [isTracking, setIsTracking] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const locationService = LocationService.getInstance()

  const requestAndroidPermissions = async (): Promise<boolean> => {
    try {
      const granted = await PermissionsAndroid.requestMultiple([
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION,
        PermissionsAndroid.PERMISSIONS.ACCESS_BACKGROUND_LOCATION,
      ])

      return Object.values(granted).every(
        (permission) => permission === PermissionsAndroid.RESULTS.GRANTED
      )
    } catch (err) {
      console.error('Error requesting Android permissions:', err)
      return false
    }
  }

  const startTracking = useCallback(async () => {
    try {
      setError(null)

      // Request permissions on Android
      if (Platform.OS === 'android') {
        const hasPermissions = await requestAndroidPermissions()
        if (!hasPermissions) {
          throw new Error('Location permissions not granted')
        }
      }

      await locationService.startTracking()
      setIsTracking(true)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to start tracking')
      setError(error)
      throw error
    }
  }, [])

  const stopTracking = useCallback(async () => {
    try {
      setError(null)
      await locationService.stopTracking()
      setIsTracking(false)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to stop tracking')
      setError(error)
      throw error
    }
  }, [])

  const getCurrentLocation = useCallback(async () => {
    try {
      setError(null)
      return await locationService.getCurrentLocation()
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to get current location')
      setError(error)
      throw error
    }
  }, [])

  useEffect(() => {
    const unsubscribe = locationService.addLocationListener((newLocation) => {
      setLocation(newLocation)
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return {
    location,
    isTracking,
    error,
    startTracking,
    stopTracking,
    getCurrentLocation,
  }
}

// Example usage:
/*
function DeliveryScreen() {
  const {
    location,
    isTracking,
    error,
    startTracking,
    stopTracking,
    getCurrentLocation,
  } = useLocation()

  useEffect(() => {
    // Start tracking when component mounts
    startTracking().catch(console.error)

    // Stop tracking when component unmounts
    return () => {
      stopTracking().catch(console.error)
    }
  }, [])

  useEffect(() => {
    if (location) {
      // Update delivery location in backend
      updateDeliveryLocation(deliveryId, location).catch(console.error)
    }
  }, [location])

  if (error) {
    return <ErrorView error={error} />
  }

  return (
    <View>
      <Map
        currentLocation={location}
        isTracking={isTracking}
      />
      <DeliveryInfo />
    </View>
  )
}
*/
