import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  Alert,
  TouchableOpacity,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { InventoryTransfer, TransferItem } from '../inventory/types'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Select } from '../ui/select'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import {
  Truck,
  Warehouse,
  BarcodeScan,
  Plus,
  Trash2,
  ArrowRight,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

type InventoryTransferScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'InventoryTransfer'
>

export function InventoryTransferScreen() {
  const navigation = useNavigation<InventoryTransferScreenNavigationProp>()
  const { toast } = useToast()

  const [showScanner, setShowScanner] = useState(false)
  const [transfer, setTransfer] = useState<InventoryTransfer>({
    id: '', // Will be set when created
    status: 'draft',
    sourceType: 'vehicle',
    sourceId: '', // Current vehicle ID
    destinationType: 'warehouse',
    destinationId: '',
    items: [],
    notes: '',
    createdAt: new Date().toISOString(),
    createdBy: '', // Current user ID
  })

  const {
    vehicles,
    warehouses,
    isLoading,
    error,
    createTransfer,
    updateTransfer,
    completeTransfer,
  } = useInventoryTransfer()

  const handleScan = useCallback(async (barcode: string) => {
    try {
      const response = await fetch(`/api/inventory/barcode/${barcode}`)
      if (!response.ok) {
        throw new Error('Item not found')
      }

      const item = await response.json()
      setTransfer(prev => ({
        ...prev,
        items: [
          ...prev.items,
          {
            itemId: item.id,
            barcode,
            quantity: 1,
            notes: '',
          },
        ],
      }))
      setShowScanner(false)

      toast({
        title: 'Item Added',
        description: `${item.name} added to transfer`,
      })
    } catch (error) {
      console.error('Error scanning item:', error)
      toast({
        title: 'Scan Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }, [toast])

  const handleUpdateItem = useCallback((
    index: number,
    updates: Partial<TransferItem>
  ) => {
    setTransfer(prev => ({
      ...prev,
      items: prev.items.map((item, i) =>
        i === index ? { ...item, ...updates } : item
      ),
    }))
  }, [])

  const handleRemoveItem = useCallback((index: number) => {
    setTransfer(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }))
  }, [])

  const handleComplete = useCallback(async () => {
    if (transfer.items.length === 0) {
      toast({
        title: 'Error',
        description: 'Add at least one item to transfer',
        variant: 'destructive',
      })
      return
    }

    if (!transfer.destinationId) {
      toast({
        title: 'Error',
        description: 'Select a destination',
        variant: 'destructive',
      })
      return
    }

    try {
      await completeTransfer({
        ...transfer,
        status: 'completed',
      })

      toast({
        title: 'Transfer Complete',
        description: 'Inventory transfer has been completed',
      })

      navigation.goBack()
    } catch (error) {
      console.error('Error completing transfer:', error)
      toast({
        title: 'Error',
        description: 'Failed to complete transfer',
        variant: 'destructive',
      })
    }
  }, [transfer, completeTransfer, navigation, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        <Text className="text-xl font-bold mb-4">Transfer Inventory</Text>

        {/* Source & Destination */}
        <View className="flex-row items-center gap-4 mb-4">
          <View className="flex-1">
            <Text className="text-sm text-muted-foreground mb-2">From</Text>
            <View className="flex-row items-center bg-muted rounded-lg p-3">
              <Truck size={20} className="mr-2" />
              <Text className="text-sm font-medium">Current Vehicle</Text>
            </View>
          </View>
          <ArrowRight size={20} className="text-muted-foreground" />
          <View className="flex-1">
            <Text className="text-sm text-muted-foreground mb-2">To</Text>
            <Select
              value={transfer.destinationId}
              onValueChange={(value) =>
                setTransfer(prev => ({
                  ...prev,
                  destinationId: value,
                }))
              }
              items={warehouses.map(w => ({
                label: w.name,
                value: w.id,
              }))}
              placeholder="Select Warehouse"
            />
          </View>
        </View>

        {/* Add Item Button */}
        <Button
          onPress={() => setShowScanner(true)}
          className="w-full"
        >
          <BarcodeScan size={16} className="mr-2" />
          Scan Item
        </Button>
      </View>

      {/* Items List */}
      <ScrollView className="flex-1 p-4">
        {transfer.items.length === 0 ? (
          <View className="flex-1 items-center justify-center py-8">
            <Text className="text-lg font-medium text-center mb-2">
              No items added
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Scan items to add them to the transfer
            </Text>
          </View>
        ) : (
          <View className="gap-4">
            {transfer.items.map((item, index) => (
              <Card
                key={`${item.itemId}-${index}`}
                className="p-4"
              >
                <View className="flex-row justify-between items-start mb-4">
                  <View className="flex-1">
                    <Text className="text-base font-medium mb-1">
                      {item.itemId}
                    </Text>
                    <Text className="text-sm text-muted-foreground">
                      Barcode: {item.barcode}
                    </Text>
                  </View>
                  <Button
                    variant="ghost"
                    size="icon"
                    onPress={() => handleRemoveItem(index)}
                  >
                    <Trash2 size={16} className="text-destructive" />
                  </Button>
                </View>

                <View className="flex-row gap-4 mb-4">
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-2">
                      Quantity
                    </Text>
                    <Input
                      value={item.quantity.toString()}
                      onChangeText={(text) => {
                        const num = parseInt(text, 10)
                        if (!isNaN(num) && num > 0) {
                          handleUpdateItem(index, { quantity: num })
                        }
                      }}
                      keyboardType="numeric"
                    />
                  </View>
                </View>

                <View>
                  <Text className="text-sm text-muted-foreground mb-2">
                    Notes
                  </Text>
                  <Input
                    value={item.notes}
                    onChangeText={(text) =>
                      handleUpdateItem(index, { notes: text })
                    }
                    placeholder="Add notes"
                    multiline
                    numberOfLines={2}
                  />
                </View>
              </Card>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Actions */}
      <View className="p-4 border-t border-border">
        <View className="flex-row gap-4">
          <Button
            variant="outline"
            className="flex-1"
            onPress={() => navigation.goBack()}
          >
            Cancel
          </Button>
          <Button
            className="flex-1"
            onPress={handleComplete}
            disabled={transfer.items.length === 0 || !transfer.destinationId}
          >
            Complete Transfer
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
