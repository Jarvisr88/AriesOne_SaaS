import React, { useState, useCallback } from 'react'
import { View, Text, Alert } from 'react-native'
import { InventoryCount, InventoryItem } from './types'
import { BarcodeScanner } from './BarcodeScanner'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Card } from '../ui/card'
import { ScrollView } from '../ui/scroll-view'
import { useToast } from '@/hooks/useToast'
import {
  ClipboardList,
  BarcodeScan,
  Save,
  AlertTriangle,
  Check,
} from 'lucide-react-native'
import { cn } from '@/lib/utils'

interface StockCountProps {
  count: InventoryCount
  onComplete: (count: InventoryCount) => Promise<void>
  onCancel: () => void
  className?: string
}

export function StockCount({
  count,
  onComplete,
  onCancel,
  className,
}: StockCountProps) {
  const [showScanner, setShowScanner] = useState(false)
  const [currentItem, setCurrentItem] = useState<InventoryItem | null>(null)
  const [quantities, setQuantities] = useState<Record<string, number>>(
    Object.fromEntries(
      count.items.map(item => [item.itemId, item.actualQuantity || 0])
    )
  )
  const [notes, setNotes] = useState<Record<string, string>>(
    Object.fromEntries(
      count.items.map(item => [item.itemId, item.notes || ''])
    )
  )
  const { toast } = useToast()

  const handleScan = useCallback(async (barcode: string) => {
    try {
      const response = await fetch(`/api/inventory/barcode/${barcode}`)
      if (!response.ok) {
        throw new Error('Item not found')
      }

      const item = await response.json()
      setCurrentItem(item)
      setShowScanner(false)
    } catch (error) {
      console.error('Error scanning item:', error)
      toast({
        title: 'Scan Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }, [toast])

  const updateQuantity = useCallback((itemId: string, quantity: string) => {
    const num = parseInt(quantity, 10)
    if (!isNaN(num) && num >= 0) {
      setQuantities(prev => ({ ...prev, [itemId]: num }))
    }
  }, [])

  const updateNotes = useCallback((itemId: string, note: string) => {
    setNotes(prev => ({ ...prev, [itemId]: note }))
  }, [])

  const calculateVariance = useCallback((
    itemId: string,
    expectedQuantity: number
  ) => {
    const actualQuantity = quantities[itemId] || 0
    return actualQuantity - expectedQuantity
  }, [quantities])

  const handleComplete = useCallback(async () => {
    // Validate all items have been counted
    const uncountedItems = count.items.filter(
      item => quantities[item.itemId] === undefined
    )

    if (uncountedItems.length > 0) {
      Alert.alert(
        'Incomplete Count',
        'Some items have not been counted. Do you want to continue?',
        [
          {
            text: 'Continue Counting',
            style: 'cancel',
          },
          {
            text: 'Complete Anyway',
            style: 'destructive',
            onPress: async () => {
              try {
                const completedCount: InventoryCount = {
                  ...count,
                  status: 'completed',
                  endTime: new Date().toISOString(),
                  items: count.items.map(item => ({
                    ...item,
                    actualQuantity: quantities[item.itemId] || 0,
                    variance: calculateVariance(
                      item.itemId,
                      item.expectedQuantity
                    ),
                    notes: notes[item.itemId] || '',
                  })),
                }
                await onComplete(completedCount)
              } catch (error) {
                console.error('Error completing count:', error)
                toast({
                  title: 'Error',
                  description: 'Failed to complete stock count',
                  variant: 'destructive',
                })
              }
            },
          },
        ]
      )
      return
    }

    // Complete the count
    try {
      const completedCount: InventoryCount = {
        ...count,
        status: 'completed',
        endTime: new Date().toISOString(),
        items: count.items.map(item => ({
          ...item,
          actualQuantity: quantities[item.itemId] || 0,
          variance: calculateVariance(
            item.itemId,
            item.expectedQuantity
          ),
          notes: notes[item.itemId] || '',
        })),
      }
      await onComplete(completedCount)
    } catch (error) {
      console.error('Error completing count:', error)
      toast({
        title: 'Error',
        description: 'Failed to complete stock count',
        variant: 'destructive',
      })
    }
  }, [count, quantities, notes, calculateVariance, onComplete, toast])

  return (
    <View className={cn('flex-1', className)}>
      {/* Header */}
      <View className="p-4 border-b border-border bg-card">
        <Text className="text-lg font-medium mb-2">
          Stock Count #{count.id}
        </Text>
        <Text className="text-sm text-muted-foreground">
          Location: {count.location.warehouse} • Zone {count.location.zone}
          {count.location.shelf && ` • Shelf ${count.location.shelf}`}
          {count.location.bin && ` • Bin ${count.location.bin}`}
        </Text>
      </View>

      {/* Item List */}
      <ScrollView className="flex-1 p-4">
        {count.items.map(item => (
          <Card
            key={item.itemId}
            className="mb-4 p-4"
          >
            <View className="flex-row justify-between items-start mb-4">
              <View className="flex-1">
                <Text className="text-base font-medium mb-1">
                  {item.itemId}
                </Text>
                <Text className="text-sm text-muted-foreground">
                  Expected: {item.expectedQuantity}
                </Text>
              </View>
              {quantities[item.itemId] !== undefined && (
                <View className="items-end">
                  <Text
                    className={cn(
                      'text-sm font-medium',
                      calculateVariance(item.itemId, item.expectedQuantity) === 0
                        ? 'text-success'
                        : 'text-destructive'
                    )}
                  >
                    Variance: {calculateVariance(item.itemId, item.expectedQuantity)}
                  </Text>
                </View>
              )}
            </View>

            <View className="flex-row gap-4 mb-4">
              <View className="flex-1">
                <Input
                  placeholder="Actual Quantity"
                  value={quantities[item.itemId]?.toString() || ''}
                  onChangeText={(text) => updateQuantity(item.itemId, text)}
                  keyboardType="numeric"
                />
              </View>
              <Button
                variant="outline"
                size="icon"
                onPress={() => setShowScanner(true)}
              >
                <BarcodeScan size={16} />
              </Button>
            </View>

            <Input
              placeholder="Notes"
              value={notes[item.itemId] || ''}
              onChangeText={(text) => updateNotes(item.itemId, text)}
              multiline
              numberOfLines={2}
            />
          </Card>
        ))}
      </ScrollView>

      {/* Actions */}
      <View className="p-4 border-t border-border bg-card">
        <View className="flex-row gap-4">
          <Button
            variant="outline"
            className="flex-1"
            onPress={onCancel}
          >
            Cancel
          </Button>
          <Button
            className="flex-1"
            onPress={handleComplete}
          >
            Complete Count
          </Button>
        </View>
      </View>

      {/* Barcode Scanner Modal */}
      {showScanner && (
        <View className="absolute inset-0 bg-background">
          <BarcodeScanner
            onScan={handleScan}
            onClose={() => setShowScanner(false)}
          />
        </View>
      )}
    </View>
  )
}
