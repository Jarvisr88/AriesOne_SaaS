import React, { useRef, useEffect, useState } from 'react'
import { View, StyleSheet, Dimensions } from 'react-native'
import MapView, { Marker, Polyline, PROVIDER_GOOGLE } from 'react-native-maps'
import { MapStyle } from './MapStyle'
import { DeliveryRoute, DeliveryStop, Location } from '../navigation/types'
import { calculateRoute, type RouteCoordinates } from '../utils/routeUtils'
import { MapMarker } from './MapMarker'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

interface DeliveryMapProps {
  delivery: DeliveryRoute
  currentStop: DeliveryStop | null
  currentLocation: Location | null
  isTracking: boolean
  onMarkerPress?: (stop: DeliveryStop) => void
  className?: string
}

export function DeliveryMap({
  delivery,
  currentStop,
  currentLocation,
  isTracking,
  onMarkerPress,
  className,
}: DeliveryMapProps) {
  const mapRef = useRef<MapView>(null)
  const [route, setRoute] = useState<RouteCoordinates[]>([])
  const { theme } = useTheme()

  // Update route when stops change
  useEffect(() => {
    const updateRoute = async () => {
      if (!delivery.stops.length) return

      try {
        const coordinates = await calculateRoute(delivery.stops)
        setRoute(coordinates)

        // Fit map to show all stops
        if (mapRef.current) {
          mapRef.current.fitToCoordinates(coordinates, {
            edgePadding: {
              top: 50,
              right: 50,
              bottom: 50,
              left: 50,
            },
            animated: true,
          })
        }
      } catch (error) {
        console.error('Error calculating route:', error)
      }
    }

    updateRoute()
  }, [delivery.stops])

  // Follow current location
  useEffect(() => {
    if (isTracking && currentLocation && mapRef.current) {
      mapRef.current.animateCamera({
        center: {
          latitude: currentLocation.latitude,
          longitude: currentLocation.longitude,
        },
        zoom: 15,
        heading: currentLocation.heading || 0,
      })
    }
  }, [isTracking, currentLocation])

  return (
    <View className={cn('flex-1', className)}>
      <MapView
        ref={mapRef}
        provider={PROVIDER_GOOGLE}
        style={StyleSheet.absoluteFill}
        customMapStyle={MapStyle}
        showsUserLocation={true}
        followsUserLocation={isTracking}
        showsMyLocationButton={true}
        showsCompass={true}
        showsScale={true}
        loadingEnabled={true}
        loadingIndicatorColor={theme.colors.primary}
        loadingBackgroundColor={theme.colors.background}
      >
        {/* Route line */}
        <Polyline
          coordinates={route}
          strokeWidth={3}
          strokeColor={theme.colors.primary}
          lineDashPattern={[1]}
        />

        {/* Stop markers */}
        {delivery.stops.map((stop, index) => (
          <Marker
            key={stop.id}
            coordinate={{
              latitude: stop.location.latitude,
              longitude: stop.location.longitude,
            }}
            onPress={() => onMarkerPress?.(stop)}
          >
            <MapMarker
              index={index + 1}
              isActive={stop.id === currentStop?.id}
              status={stop.status}
            />
          </Marker>
        ))}
      </MapView>
    </View>
  )
}
