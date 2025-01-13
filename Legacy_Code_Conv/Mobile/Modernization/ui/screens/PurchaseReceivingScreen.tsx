import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  Alert,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { PurchaseOrder, PurchaseReceival } from '../inventory/types'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Select } from '../ui/select'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import {
  Package,
  BarcodeScan,
  Warehouse,
  Check,
  AlertTriangle,
  Search,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

type PurchaseReceivingScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'PurchaseReceiving'
>

export function PurchaseReceivingScreen() {
  const navigation = useNavigation<PurchaseReceivingScreenNavigationProp>()
  const { toast } = useToast()

  const [showScanner, setShowScanner] = useState(false)
  const [purchaseOrder, setPurchaseOrder] = useState<PurchaseOrder | null>(null)
  const [selectedWarehouse, setSelectedWarehouse] = useState('')
  const [receivedItems, setReceivedItems] = useState<Record<string, number>>({})
  const [notes, setNotes] = useState<Record<string, string>>({})

  const {
    warehouses,
    isLoading,
    error,
    searchPurchaseOrder,
    receivePurchaseOrder,
  } = usePurchaseReceiving()

  const handleScanPO = useCallback(async (barcode: string) => {
    try {
      const po = await searchPurchaseOrder(barcode)
      setPurchaseOrder(po)
      setShowScanner(false)

      // Initialize received quantities
      const quantities: Record<string, number> = {}
      po.items.forEach(item => {
        quantities[item.itemId] = 0
      })
      setReceivedItems(quantities)

      toast({
        title: 'Purchase Order Found',
        description: `PO #${po.id} loaded for receiving`,
      })
    } catch (error) {
      console.error('Error scanning PO:', error)
      toast({
        title: 'Scan Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }, [searchPurchaseOrder, toast])

  const handleUpdateQuantity = useCallback((
    itemId: string,
    quantity: string
  ) => {
    const num = parseInt(quantity, 10)
    if (!isNaN(num) && num >= 0) {
      setReceivedItems(prev => ({ ...prev, [itemId]: num }))
    }
  }, [])

  const handleUpdateNotes = useCallback((
    itemId: string,
    note: string
  ) => {
    setNotes(prev => ({ ...prev, [itemId]: note }))
  }, [])

  const handleReceive = useCallback(async () => {
    if (!purchaseOrder || !selectedWarehouse) {
      toast({
        title: 'Error',
        description: 'Please select a warehouse',
        variant: 'destructive',
      })
      return
    }

    // Validate received quantities
    const invalidItems = purchaseOrder.items.filter(
      item => receivedItems[item.itemId] > item.quantity
    )

    if (invalidItems.length > 0) {
      toast({
        title: 'Error',
        description: 'Received quantity cannot exceed ordered quantity',
        variant: 'destructive',
      })
      return
    }

    try {
      const receival: PurchaseReceival = {
        purchaseOrderId: purchaseOrder.id,
        warehouseId: selectedWarehouse,
        receivedAt: new Date().toISOString(),
        receivedBy: 'current-user-id', // Replace with actual user ID
        items: purchaseOrder.items.map(item => ({
          itemId: item.itemId,
          orderedQuantity: item.quantity,
          receivedQuantity: receivedItems[item.itemId],
          notes: notes[item.itemId] || '',
        })),
      }

      await receivePurchaseOrder(receival)

      toast({
        title: 'Receiving Complete',
        description: 'Items have been added to warehouse inventory',
      })

      navigation.goBack()
    } catch (error) {
      console.error('Error receiving PO:', error)
      toast({
        title: 'Error',
        description: 'Failed to receive purchase order',
        variant: 'destructive',
      })
    }
  }, [
    purchaseOrder,
    selectedWarehouse,
    receivedItems,
    notes,
    receivePurchaseOrder,
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
        <Text className="text-xl font-bold mb-4">Receive Purchase Order</Text>

        {!purchaseOrder ? (
          <Button
            onPress={() => setShowScanner(true)}
            className="w-full"
          >
            <BarcodeScan size={16} className="mr-2" />
            Scan Purchase Order
          </Button>
        ) : (
          <View>
            <Text className="text-base font-medium mb-2">
              PO #{purchaseOrder.id}
            </Text>
            <Select
              value={selectedWarehouse}
              onValueChange={setSelectedWarehouse}
              items={warehouses.map(w => ({
                label: w.name,
                value: w.id,
              }))}
              placeholder="Select Receiving Warehouse"
            />
          </View>
        )}
      </View>

      <ScrollView className="flex-1 p-4">
        {purchaseOrder ? (
          <View className="gap-4">
            {purchaseOrder.items.map((item) => (
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
                      Ordered: {item.quantity}
                    </Text>
                  </View>
                  {receivedItems[item.itemId] > item.quantity && (
                    <AlertTriangle
                      size={16}
                      className="text-destructive"
                    />
                  )}
                </View>

                <View className="flex-row gap-4 mb-4">
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-2">
                      Received Quantity
                    </Text>
                    <Input
                      value={receivedItems[item.itemId]?.toString()}
                      onChangeText={(text) =>
                        handleUpdateQuantity(item.itemId, text)
                      }
                      keyboardType="numeric"
                    />
                  </View>
                </View>

                <View>
                  <Text className="text-sm text-muted-foreground mb-2">
                    Notes
                  </Text>
                  <Input
                    value={notes[item.itemId] || ''}
                    onChangeText={(text) =>
                      handleUpdateNotes(item.itemId, text)
                    }
                    placeholder="Add notes about received items"
                    multiline
                    numberOfLines={2}
                  />
                </View>
              </Card>
            ))}
          </View>
        ) : (
          <View className="flex-1 items-center justify-center py-8">
            <Package
              size={48}
              className="text-muted-foreground mb-4"
            />
            <Text className="text-lg font-medium text-center mb-2">
              No Purchase Order Selected
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Scan a purchase order to begin receiving
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Actions */}
      {purchaseOrder && (
        <View className="p-4 border-t border-border">
          <Button
            onPress={handleReceive}
            className="w-full"
            disabled={!selectedWarehouse}
          >
            Complete Receiving
          </Button>
        </View>
      )}

      {/* Barcode Scanner Modal */}
      {showScanner && (
        <View className="absolute inset-0 bg-background">
          <BarcodeScanner
            onScan={handleScanPO}
            onClose={() => setShowScanner(false)}
          />
        </View>
      )}
    </View>
  )
}
