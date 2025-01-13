import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  Alert,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { CycleCount, CycleCountItem } from '../inventory/types'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Select } from '../ui/select'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import {
  ClipboardList,
  BarcodeScan,
  Warehouse,
  Check,
  AlertTriangle,
  Search,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

type CycleCountScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'CycleCount'
>

export function CycleCountScreen() {
  const navigation = useNavigation<CycleCountScreenNavigationProp>()
  const { toast } = useToast()

  const [showScanner, setShowScanner] = useState(false)
  const [selectedWarehouse, setSelectedWarehouse] = useState('')
  const [selectedZone, setSelectedZone] = useState('')
  const [cycleCount, setCycleCount] = useState<CycleCount>({
    id: '', // Will be set when created
    warehouseId: '',
    zone: '',
    status: 'in_progress',
    startTime: new Date().toISOString(),
    items: [],
    createdBy: 'current-user-id', // Replace with actual user ID
  })

  const {
    warehouses,
    zones,
    isLoading,
    error,
    createCycleCount,
    updateCycleCount,
    completeCycleCount,
  } = useCycleCount(selectedWarehouse)

  const handleScanItem = useCallback(async (barcode: string) => {
    try {
      const response = await fetch(`/api/inventory/barcode/${barcode}`)
      if (!response.ok) {
        throw new Error('Item not found')
      }

      const item = await response.json()
      
      // Check if item already scanned
      const existingIndex = cycleCount.items.findIndex(
        i => i.itemId === item.id
      )

      if (existingIndex >= 0) {
        // Update existing item count
        setCycleCount(prev => ({
          ...prev,
          items: prev.items.map((i, index) =>
            index === existingIndex
              ? { ...i, scannedQuantity: (i.scannedQuantity || 0) + 1 }
              : i
          ),
        }))
      } else {
        // Add new item
        setCycleCount(prev => ({
          ...prev,
          items: [
            ...prev.items,
            {
              itemId: item.id,
              expectedQuantity: item.quantity,
              scannedQuantity: 1,
              barcode,
              lastScannedAt: new Date().toISOString(),
            },
          ],
        }))
      }

      toast({
        title: 'Item Scanned',
        description: `${item.name} added to count`,
      })
    } catch (error) {
      console.error('Error scanning item:', error)
      toast({
        title: 'Scan Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }, [cycleCount, toast])

  const handleUpdateQuantity = useCallback((
    itemId: string,
    quantity: string
  ) => {
    const num = parseInt(quantity, 10)
    if (!isNaN(num) && num >= 0) {
      setCycleCount(prev => ({
        ...prev,
        items: prev.items.map(item =>
          item.itemId === itemId
            ? { ...item, scannedQuantity: num }
            : item
        ),
      }))
    }
  }, [])

  const handleComplete = useCallback(async () => {
    if (!selectedWarehouse || !selectedZone) {
      toast({
        title: 'Error',
        description: 'Please select warehouse and zone',
        variant: 'destructive',
      })
      return
    }

    try {
      // Calculate variances
      const itemsWithVariance = cycleCount.items.map(item => ({
        ...item,
        variance: (item.scannedQuantity || 0) - item.expectedQuantity,
      }))

      const completedCount: CycleCount = {
        ...cycleCount,
        warehouseId: selectedWarehouse,
        zone: selectedZone,
        status: 'completed',
        endTime: new Date().toISOString(),
        items: itemsWithVariance,
      }

      await completeCycleCount(completedCount)

      toast({
        title: 'Count Complete',
        description: 'Cycle count has been completed',
      })

      navigation.goBack()
    } catch (error) {
      console.error('Error completing count:', error)
      toast({
        title: 'Error',
        description: 'Failed to complete cycle count',
        variant: 'destructive',
      })
    }
  }, [
    cycleCount,
    selectedWarehouse,
    selectedZone,
    completeCycleCount,
    navigation,
    toast,
  ])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        <Text className="text-xl font-bold mb-4">Cycle Count</Text>

        <View className="gap-4">
          <Select
            value={selectedWarehouse}
            onValueChange={setSelectedWarehouse}
            items={warehouses.map(w => ({
              label: w.name,
              value: w.id,
            }))}
            placeholder="Select Warehouse"
          />

          {selectedWarehouse && (
            <Select
              value={selectedZone}
              onValueChange={setSelectedZone}
              items={zones.map(z => ({
                label: z.name,
                value: z.id,
              }))}
              placeholder="Select Zone"
            />
          )}

          {selectedWarehouse && selectedZone && (
            <Button
              onPress={() => setShowScanner(true)}
              className="w-full"
            >
              <BarcodeScan size={16} className="mr-2" />
              Scan Items
            </Button>
          )}
        </View>
      </View>

      <ScrollView className="flex-1 p-4">
        {cycleCount.items.length === 0 ? (
          <View className="flex-1 items-center justify-center py-8">
            <ClipboardList
              size={48}
              className="text-muted-foreground mb-4"
            />
            <Text className="text-lg font-medium text-center mb-2">
              No Items Counted
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Scan items to begin counting
            </Text>
          </View>
        ) : (
          <View className="gap-4">
            {cycleCount.items.map((item) => (
              <Card
                key={item.itemId}
                className="p-4"
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
                  {(item.scannedQuantity || 0) !== item.expectedQuantity && (
                    <AlertTriangle
                      size={16}
                      className="text-destructive"
                    />
                  )}
                </View>

                <View className="flex-row gap-4">
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-2">
                      Counted Quantity
                    </Text>
                    <Input
                      value={item.scannedQuantity?.toString()}
                      onChangeText={(text) =>
                        handleUpdateQuantity(item.itemId, text)
                      }
                      keyboardType="numeric"
                    />
                  </View>
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-2">
                      Variance
                    </Text>
                    <Text
                      className={cn(
                        'text-base font-medium',
                        (item.scannedQuantity || 0) === item.expectedQuantity
                          ? 'text-success'
                          : 'text-destructive'
                      )}
                    >
                      {(item.scannedQuantity || 0) - item.expectedQuantity}
                    </Text>
                  </View>
                </View>
              </Card>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Actions */}
      {cycleCount.items.length > 0 && (
        <View className="p-4 border-t border-border">
          <Button
            onPress={handleComplete}
            className="w-full"
          >
            Complete Count
          </Button>
        </View>
      )}

      {/* Barcode Scanner Modal */}
      {showScanner && (
        <View className="absolute inset-0 bg-background">
          <BarcodeScanner
            onScan={handleScanItem}
            onClose={() => setShowScanner(false)}
          />
        </View>
      )}
    </View>
  )
}
