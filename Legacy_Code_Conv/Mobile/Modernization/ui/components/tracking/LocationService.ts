import Geolocation, {
  GeolocationResponse,
  GeolocationError,
} from '@react-native-community/geolocation'
import BackgroundGeolocation, {
  Location,
  LocationError,
  Config,
} from 'react-native-background-geolocation'
import { Platform } from 'react-native'
import { Location as AppLocation } from '../navigation/types'

class LocationService {
  private static instance: LocationService
  private isTracking: boolean = false
  private watchId?: number
  private listeners: Set<(location: AppLocation) => void> = new Set()

  private constructor() {
    // Initialize geolocation configuration
    if (Platform.OS === 'ios') {
      Geolocation.setRNConfiguration({
        skipPermissionRequests: false,
        authorizationLevel: 'whenInUse',
      })
    }

    // Configure background geolocation
    BackgroundGeolocation.configure({
      desiredAccuracy: BackgroundGeolocation.HIGH_ACCURACY,
      distanceFilter: 10, // Minimum distance in meters between updates
      stopOnTerminate: false,
      startOnBoot: true,
      debug: __DEV__, // Enable debug logs in development
      logLevel: BackgroundGeolocation.LOG_LEVEL_VERBOSE,
      stopTimeout: 1, // Stop tracking after 1 minute of no movement
      notification: {
        title: 'Location Tracking',
        text: 'Tracking delivery location',
        channelId: 'location_tracking',
      },
      locationProvider: BackgroundGeolocation.ACTIVITY_PROVIDER,
      interval: 10000, // Get location every 10 seconds
      fastestInterval: 5000,
      activitiesInterval: 10000,
    } as Config)

    // Handle background location updates
    BackgroundGeolocation.onLocation(
      this.handleBackgroundLocation.bind(this),
      this.handleBackgroundError.bind(this)
    )
  }

  public static getInstance(): LocationService {
    if (!LocationService.instance) {
      LocationService.instance = new LocationService()
    }
    return LocationService.instance
  }

  public async requestPermissions(): Promise<boolean> {
    try {
      const status = await BackgroundGeolocation.checkStatus()
      
      if (status.locationServicesEnabled) {
        return true
      }

      await BackgroundGeolocation.requestPermission()
      return true
    } catch (error) {
      console.error('Error requesting location permissions:', error)
      return false
    }
  }

  public async startTracking(): Promise<void> {
    if (this.isTracking) return

    try {
      const hasPermission = await this.requestPermissions()
      if (!hasPermission) {
        throw new Error('Location permissions not granted')
      }

      // Start background tracking
      await BackgroundGeolocation.start()

      // Start foreground tracking
      this.watchId = Geolocation.watchPosition(
        this.handleForegroundLocation.bind(this),
        this.handleForegroundError.bind(this),
        {
          enableHighAccuracy: true,
          distanceFilter: 10,
          interval: 10000,
          fastestInterval: 5000,
        }
      )

      this.isTracking = true
    } catch (error) {
      console.error('Error starting location tracking:', error)
      throw error
    }
  }

  public async stopTracking(): Promise<void> {
    if (!this.isTracking) return

    try {
      // Stop background tracking
      await BackgroundGeolocation.stop()

      // Stop foreground tracking
      if (this.watchId !== undefined) {
        Geolocation.clearWatch(this.watchId)
        this.watchId = undefined
      }

      this.isTracking = false
    } catch (error) {
      console.error('Error stopping location tracking:', error)
      throw error
    }
  }

  public async getCurrentLocation(): Promise<AppLocation> {
    return new Promise((resolve, reject) => {
      Geolocation.getCurrentPosition(
        (position: GeolocationResponse) => {
          resolve(this.formatLocation(position))
        },
        (error: GeolocationError) => {
          reject(new Error(`Error getting current location: ${error.message}`))
        },
        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 10000,
        }
      )
    })
  }

  public addLocationListener(listener: (location: AppLocation) => void): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private handleForegroundLocation(position: GeolocationResponse): void {
    const location = this.formatLocation(position)
    this.notifyListeners(location)
  }

  private handleForegroundError(error: GeolocationError): void {
    console.error('Foreground location error:', error)
  }

  private handleBackgroundLocation(location: Location): void {
    const appLocation: AppLocation = {
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      timestamp: location.timestamp,
      accuracy: location.coords.accuracy,
      altitude: location.coords.altitude,
      speed: location.coords.speed,
      heading: location.coords.heading,
    }
    this.notifyListeners(appLocation)
  }

  private handleBackgroundError(error: LocationError): void {
    console.error('Background location error:', error)
  }

  private formatLocation(position: GeolocationResponse): AppLocation {
    return {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      timestamp: position.timestamp,
      accuracy: position.coords.accuracy,
      altitude: position.coords.altitude,
      speed: position.coords.speed,
      heading: position.coords.heading,
    }
  }

  private notifyListeners(location: AppLocation): void {
    this.listeners.forEach((listener) => {
      try {
        listener(location)
      } catch (error) {
        console.error('Error in location listener:', error)
      }
    })
  }
}

export default LocationService
