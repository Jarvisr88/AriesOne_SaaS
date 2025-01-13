import React from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { DeliveryStatus } from '../navigation/types'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

interface MapMarkerProps {
  index: number
  isActive: boolean
  status: DeliveryStatus
  className?: string
}

export function MapMarker({
  index,
  isActive,
  status,
  className,
}: MapMarkerProps) {
  const { theme } = useTheme()

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return theme.colors.success
      case 'failed':
        return theme.colors.error
      case 'in_progress':
        return theme.colors.warning
      default:
        return theme.colors.muted
    }
  }

  return (
    <View
      className={cn(
        'items-center justify-center',
        'rounded-full',
        'shadow-lg shadow-black/25',
        isActive ? 'scale-125' : 'scale-100',
        className
      )}
      style={[
        styles.container,
        {
          backgroundColor: getStatusColor(),
          borderColor: theme.colors.background,
        },
      ]}
    >
      <Text
        className={cn(
          'text-sm font-bold',
          'text-center',
          status === 'completed' ? 'line-through' : ''
        )}
        style={{ color: theme.colors.background }}
      >
        {index}
      </Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    width: 32,
    height: 32,
    borderWidth: 2,
    elevation: 5,
  },
})
