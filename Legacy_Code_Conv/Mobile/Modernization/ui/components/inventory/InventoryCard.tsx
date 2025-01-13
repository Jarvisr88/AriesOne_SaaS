import React from 'react'
import { View, Text, TouchableOpacity } from 'react-native'
import { Package, AlertTriangle, Archive } from 'lucide-react-native'
import { InventoryItem } from './types'
import { Card } from '../ui/card'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

interface InventoryCardProps {
  item: InventoryItem
  onPress?: () => void
  className?: string
}

export function InventoryCard({
  item,
  onPress,
  className,
}: InventoryCardProps) {
  const { theme } = useTheme()

  const getStatusColor = () => {
    switch (item.status) {
      case 'in_stock':
        return 'bg-success'
      case 'low_stock':
        return 'bg-warning'
      case 'out_of_stock':
        return 'bg-destructive'
      case 'discontinued':
        return 'bg-muted'
      case 'on_hold':
        return 'bg-secondary'
      default:
        return 'bg-muted'
    }
  }

  const getStockLevel = () => {
    const percentage = (item.quantity / item.maximumStock) * 100
    return Math.min(Math.max(percentage, 0), 100)
  }

  const isLowStock = item.quantity <= item.reorderPoint
  const isOutOfStock = item.quantity === 0

  return (
    <Card
      onPress={onPress}
      className={cn('p-4', className)}
    >
      {/* Header */}
      <View className="flex-row justify-between items-start mb-2">
        <View className="flex-1">
          <Text className="text-lg font-medium mb-1">
            {item.name}
          </Text>
          <Text className="text-sm text-muted-foreground">
            SKU: {item.sku}
          </Text>
        </View>
        <Badge variant="outline" className={getStatusColor()}>
          {item.status.replace('_', ' ')}
        </Badge>
      </View>

      {/* Stock Level */}
      <View className="mb-4">
        <View className="flex-row justify-between items-center mb-2">
          <Text className="text-sm text-muted-foreground">
            Stock Level
          </Text>
          <Text className="text-sm font-medium">
            {item.quantity} / {item.maximumStock} {item.unit}
          </Text>
        </View>
        <Progress value={getStockLevel()} className="h-2" />
      </View>

      {/* Location */}
      <View className="flex-row items-center mb-4">
        <Archive size={16} className="text-muted-foreground mr-2" />
        <Text className="text-sm text-muted-foreground">
          {item.location.warehouse} • Zone {item.location.zone} • 
          Shelf {item.location.shelf} • Bin {item.location.bin}
        </Text>
      </View>

      {/* Alerts */}
      {(isLowStock || isOutOfStock) && (
        <View className="flex-row items-center p-2 rounded-md bg-warning/10">
          <AlertTriangle
            size={16}
            className={cn(
              'mr-2',
              isOutOfStock ? 'text-destructive' : 'text-warning'
            )}
          />
          <Text className="text-sm font-medium text-warning">
            {isOutOfStock
              ? 'Out of stock'
              : `Low stock - Reorder point: ${item.reorderPoint} ${item.unit}`}
          </Text>
        </View>
      )}

      {/* Additional Info */}
      {item.expirationDate && (
        <View className="mt-2">
          <Text className="text-sm text-muted-foreground">
            Expires: {new Date(item.expirationDate).toLocaleDateString()}
          </Text>
        </View>
      )}

      {item.batchNumber && (
        <View className="mt-1">
          <Text className="text-sm text-muted-foreground">
            Batch: {item.batchNumber}
          </Text>
        </View>
      )}
    </Card>
  )
}
