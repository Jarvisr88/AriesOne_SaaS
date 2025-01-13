import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { useFetchDeliveries } from '@/hooks/useFetchDeliveries'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import { formatTime, formatDate } from '@/lib/format'
import { cn } from '@/lib/utils'
import {
  Clock,
  MapPin,
  Package,
  ChevronRight,
  AlertCircle,
} from 'lucide-react-native'

type DeliveriesScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'Deliveries'
>

export function DeliveriesScreen() {
  const navigation = useNavigation<DeliveriesScreenNavigationProp>()
  const [selectedDate, setSelectedDate] = useState(new Date())

  const {
    deliveries,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useFetchDeliveries(selectedDate)

  const handleDateChange = useCallback((date: Date) => {
    setSelectedDate(date)
  }, [])

  const handleDeliveryPress = useCallback((deliveryId: string) => {
    navigation.navigate('DeliveryDetails', { id: deliveryId })
  }, [navigation])

  if (isLoading) {
    return <LoadingScreen />
  }

  if (error) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <AlertCircle
          size={48}
          className="text-destructive mb-4"
        />
        <Text className="text-lg font-medium text-center mb-2">
          Failed to load deliveries
        </Text>
        <Text className="text-sm text-muted-foreground text-center mb-4">
          {error.message}
        </Text>
        <Button onPress={() => refetch()}>
          Try Again
        </Button>
      </View>
    )
  }

  return (
    <View className="flex-1 bg-background">
      {/* Date Selector */}
      <View className="px-4 py-2 border-b border-border">
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          className="gap-2"
        >
          {[...Array(7)].map((_, i) => {
            const date = new Date()
            date.setDate(date.getDate() + i)
            const isSelected = date.toDateString() === selectedDate.toDateString()

            return (
              <TouchableOpacity
                key={i}
                onPress={() => handleDateChange(date)}
                className={cn(
                  'px-4 py-2 rounded-full',
                  isSelected
                    ? 'bg-primary'
                    : 'bg-muted'
                )}
              >
                <Text
                  className={cn(
                    'text-sm font-medium',
                    isSelected
                      ? 'text-primary-foreground'
                      : 'text-foreground'
                  )}
                >
                  {i === 0 ? 'Today' : formatDate(date)}
                </Text>
              </TouchableOpacity>
            )
          })}
        </ScrollView>
      </View>

      {/* Deliveries List */}
      <ScrollView
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
          />
        }
        className="flex-1 p-4"
      >
        {deliveries.length === 0 ? (
          <View className="flex-1 items-center justify-center py-8">
            <Package
              size={48}
              className="text-muted-foreground mb-4"
            />
            <Text className="text-lg font-medium text-center mb-2">
              No deliveries scheduled
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Check back later for new deliveries
            </Text>
          </View>
        ) : (
          <View className="gap-4">
            {deliveries.map((delivery) => (
              <Card
                key={delivery.id}
                onPress={() => handleDeliveryPress(delivery.id)}
                className="p-4"
              >
                {/* Route Info */}
                <View className="flex-row justify-between items-center mb-4">
                  <View className="flex-row items-center">
                    <Clock size={16} className="text-muted-foreground mr-2" />
                    <Text className="text-sm text-muted-foreground">
                      {formatTime(delivery.startTime)} - {formatTime(delivery.endTime)}
                    </Text>
                  </View>
                  <Text
                    className={cn(
                      'text-sm font-medium',
                      delivery.status === 'completed'
                        ? 'text-success'
                        : delivery.status === 'failed'
                        ? 'text-destructive'
                        : 'text-primary'
                    )}
                  >
                    {delivery.status.replace('_', ' ')}
                  </Text>
                </View>

                {/* Stops Summary */}
                <View className="mb-4">
                  <Text className="text-sm font-medium mb-2">
                    {delivery.stops.length} Stops
                  </Text>
                  {delivery.stops.slice(0, 2).map((stop, index) => (
                    <View
                      key={stop.id}
                      className="flex-row items-center mb-2"
                    >
                      <View
                        className={cn(
                          'w-6 h-6 rounded-full items-center justify-center mr-2',
                          stop.status === 'completed'
                            ? 'bg-success'
                            : 'bg-primary'
                        )}
                      >
                        <Text className="text-xs text-white">
                          {index + 1}
                        </Text>
                      </View>
                      <View className="flex-1">
                        <Text className="text-sm font-medium">
                          {stop.customer.name}
                        </Text>
                        <Text className="text-xs text-muted-foreground">
                          {stop.location.address}
                        </Text>
                      </View>
                    </View>
                  ))}
                  {delivery.stops.length > 2 && (
                    <Text className="text-sm text-muted-foreground">
                      +{delivery.stops.length - 2} more stops
                    </Text>
                  )}
                </View>

                {/* Action Button */}
                <Button
                  variant="outline"
                  className="flex-row items-center justify-center"
                  onPress={() => handleDeliveryPress(delivery.id)}
                >
                  <Text className="mr-2">View Details</Text>
                  <ChevronRight size={16} />
                </Button>
              </Card>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  )
}
