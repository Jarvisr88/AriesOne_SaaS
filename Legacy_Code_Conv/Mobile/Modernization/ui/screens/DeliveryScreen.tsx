import React, { useEffect } from 'react'
import { View, StyleSheet, Alert } from 'react-native'
import { useNavigation, useRoute } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { useDelivery } from '../tracking/useDelivery'
import { useLocation } from '../tracking/useLocation'
import { DeliveryMap } from '../delivery/DeliveryMap'
import { DeliveryDetails } from '../delivery/DeliveryDetails'
import { LoadingScreen } from '../ui/loading-screen'
import { useToast } from '@/hooks/useToast'

type DeliveryScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'DeliveryDetails'
>

export function DeliveryScreen() {
  const navigation = useNavigation<DeliveryScreenNavigationProp>()
  const route = useRoute()
  const { toast } = useToast()

  const {
    currentDelivery,
    currentStop,
    isLoading,
    error,
    startDelivery,
    completeDelivery,
  } = useDelivery({
    onStatusChange: (status) => {
      if (status === 'completed') {
        toast({
          title: 'Delivery Completed',
          description: 'All stops have been completed.',
          duration: 3000,
        })
        navigation.navigate('Home')
      }
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      })
    },
  })

  const {
    location: currentLocation,
    isTracking,
    error: locationError,
  } = useLocation()

  useEffect(() => {
    // Start delivery when screen mounts
    const deliveryId = route.params?.deliveryId
    if (deliveryId && !currentDelivery) {
      fetchAndStartDelivery(deliveryId)
    }

    // Cleanup when screen unmounts
    return () => {
      if (currentDelivery) {
        completeDelivery().catch(console.error)
      }
    }
  }, [])

  const fetchAndStartDelivery = async (deliveryId: string) => {
    try {
      const response = await fetch(`/api/delivery/${deliveryId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch delivery')
      }

      const deliveryRoute = await response.json()
      await startDelivery(deliveryRoute)
    } catch (error) {
      console.error('Error fetching delivery:', error)
      Alert.alert(
        'Error',
        'Failed to load delivery. Please try again.',
        [
          {
            text: 'Retry',
            onPress: () => fetchAndStartDelivery(deliveryId),
          },
          {
            text: 'Cancel',
            onPress: () => navigation.goBack(),
            style: 'cancel',
          },
        ]
      )
    }
  }

  if (isLoading || !currentDelivery) {
    return <LoadingScreen />
  }

  if (error || locationError) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>
          {error?.message || locationError?.message}
        </Text>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <DeliveryMap
        delivery={currentDelivery}
        currentStop={currentStop}
        currentLocation={currentLocation}
        isTracking={isTracking}
        onMarkerPress={(stop) => {
          // Show stop details in bottom sheet
        }}
        className="flex-1"
      />
      {currentStop && (
        <DeliveryDetails
          stop={currentStop}
          className="absolute bottom-0 left-0 right-0"
        />
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  error: {
    color: 'red',
    textAlign: 'center',
    margin: 20,
  },
})
