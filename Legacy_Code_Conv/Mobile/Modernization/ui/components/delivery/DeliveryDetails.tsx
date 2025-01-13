import React, { useState } from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native'
import { Camera, Package, Signature, X } from 'lucide-react-native'
import { DeliveryStop } from '../navigation/types'
import { useDelivery } from '../tracking/useDelivery'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { Input } from '../ui/input'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'
import { formatDistance, formatTime } from '@/lib/format'

interface DeliveryDetailsProps {
  stop: DeliveryStop
  className?: string
}

export function DeliveryDetails({ stop, className }: DeliveryDetailsProps) {
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { theme } = useTheme()

  const {
    updateStop,
    capturePhoto,
    captureSignature,
    skipStop,
    error,
  } = useDelivery({
    onError: (error) => {
      Alert.alert('Error', error.message)
    },
  })

  const handleComplete = async () => {
    try {
      setIsSubmitting(true)

      // Capture proof of delivery
      const [photo, signature] = await Promise.all([
        capturePhoto(),
        captureSignature(),
      ])

      // Update stop status
      await updateStop(stop.id, 'completed', {
        photos: [photo],
        signature,
        notes,
      })
    } catch (error) {
      console.error('Error completing stop:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSkip = () => {
    Alert.alert(
      'Skip Stop',
      'Are you sure you want to skip this stop? Please provide a reason.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Skip',
          style: 'destructive',
          onPress: () => {
            skipStop(stop.id, notes || 'No reason provided')
          },
        },
      ]
    )
  }

  return (
    <Card
      className={cn(
        'rounded-t-3xl',
        'bg-background',
        'shadow-xl shadow-black/25',
        className
      )}
    >
      {/* Handle */}
      <View className="items-center py-2">
        <View className="w-16 h-1 rounded-full bg-muted" />
      </View>

      <ScrollView className="px-4">
        {/* Customer Info */}
        <View className="mb-4">
          <Text className="text-xl font-bold mb-2">{stop.customer.name}</Text>
          <Text className="text-base text-muted-foreground">
            {stop.location.address}
          </Text>
          <Text className="text-sm text-muted-foreground">
            {formatDistance(stop.location.latitude, stop.location.longitude)}
          </Text>
        </View>

        {/* Time Window */}
        <View className="mb-4">
          <Text className="text-sm font-medium mb-1">Delivery Window</Text>
          <Text className="text-base">
            {formatTime(stop.timeWindow.start)} - {formatTime(stop.timeWindow.end)}
          </Text>
        </View>

        {/* Order Details */}
        <View className="mb-4">
          <Text className="text-sm font-medium mb-1">Order #{stop.orderId}</Text>
          <View className="flex-row items-center">
            <Package size={16} color={theme.colors.foreground} />
            <Text className="ml-2">3 items</Text>
          </View>
        </View>

        {/* Notes */}
        <Input
          placeholder="Add delivery notes..."
          value={notes}
          onChangeText={setNotes}
          multiline
          numberOfLines={3}
          className="mb-4"
        />

        {/* Action Buttons */}
        <View className="flex-row gap-4 mb-4">
          <Button
            onPress={capturePhoto}
            variant="outline"
            className="flex-1"
          >
            <Camera size={20} className="mr-2" />
            Photo
          </Button>
          <Button
            onPress={captureSignature}
            variant="outline"
            className="flex-1"
          >
            <Signature size={20} className="mr-2" />
            Signature
          </Button>
        </View>

        {/* Complete/Skip Buttons */}
        <View className="flex-row gap-4 mb-4">
          <Button
            onPress={handleComplete}
            className="flex-1"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <ActivityIndicator color={theme.colors.background} />
            ) : (
              'Complete Delivery'
            )}
          </Button>
          <Button
            onPress={handleSkip}
            variant="destructive"
            disabled={isSubmitting}
          >
            <X size={20} />
          </Button>
        </View>

        {error && (
          <Text className="text-sm text-destructive mb-4">
            {error.message}
          </Text>
        )}
      </ScrollView>
    </Card>
  )
}
