import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native'
import { useRoute, useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { InventoryItem, StockMovement } from '../inventory/types'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Card } from '../ui/card'
import { Progress } from '../ui/progress'
import { LoadingScreen } from '../ui/loading-screen'
import {
  Package,
  Truck,
  ArrowLeftRight,
  AlertTriangle,
  BarcodeScan,
  Edit,
  Trash,
  Plus,
  Minus,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

type InventoryDetailsScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'InventoryDetails'
>

export function InventoryDetailsScreen() {
  const navigation = useNavigation<InventoryDetailsScreenNavigationProp>()
  const route = useRoute()
  const [showScanner, setShowScanner] = useState(false)
  const [quantity, setQuantity] = useState('')
  const { toast } = useToast()

  const {
    item,
    movements,
    isLoading,
    error,
    refetch,
    updateStock,
    deleteItem,
  } = useInventoryDetails(route.params?.id)

  const handleStockUpdate = useCallback(async (type: 'receive' | 'dispatch') => {
    if (!quantity || isNaN(Number(quantity))) {
      toast({
        title: 'Invalid Quantity',
        description: 'Please enter a valid number.',
        variant: 'destructive',
      })
      return
    }

    try {
      await updateStock({
        itemId: item.id,
        type,
        quantity: Number(quantity),
        notes: `Manual ${type}`,
      })
      setQuantity('')
      refetch()
      toast({
        title: 'Stock Updated',
        description: `Successfully ${type}ed ${quantity} units.`,
      })
    } catch (error) {
      console.error('Error updating stock:', error)
      toast({
        title: 'Update Failed',
        description: error.message,
        variant: 'destructive',
      })
    }
  }, [item?.id, quantity, updateStock, refetch, toast])

  const handleDelete = useCallback(() => {
    Alert.alert(
      'Delete Item',
      'Are you sure you want to delete this item? This action cannot be undone.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteItem(item.id)
              navigation.goBack()
              toast({
                title: 'Item Deleted',
                description: 'Successfully deleted inventory item.',
              })
            } catch (error) {
              console.error('Error deleting item:', error)
              toast({
                title: 'Delete Failed',
                description: error.message,
                variant: 'destructive',
              })
            }
          },
        },
      ]
    )
  }, [item?.id, deleteItem, navigation, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  if (error || !item) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <AlertTriangle
          size={48}
          className="text-destructive mb-4"
        />
        <Text className="text-lg font-medium text-center mb-2">
          Failed to load item details
        </Text>
        <Text className="text-sm text-muted-foreground text-center mb-4">
          {error?.message || 'Item not found'}
        </Text>
        <Button onPress={() => navigation.goBack()}>
          Go Back
        </Button>
      </View>
    )
  }

  return (
    <View className="flex-1 bg-background">
      <ScrollView className="flex-1">
        {/* Header */}
        <View className="p-4 border-b border-border">
          <Text className="text-2xl font-bold mb-2">
            {item.name}
          </Text>
          <Text className="text-base text-muted-foreground mb-4">
            SKU: {item.sku}
          </Text>

          {/* Quick Actions */}
          <View className="flex-row gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onPress={() => navigation.navigate('EditInventoryItem', { id: item.id })}
            >
              <Edit size={16} className="mr-2" />
              Edit
            </Button>
            <Button
              variant="destructive"
              className="flex-1"
              onPress={handleDelete}
            >
              <Trash size={16} className="mr-2" />
              Delete
            </Button>
          </View>
        </View>

        {/* Stock Level */}
        <Card className="m-4 p-4">
          <Text className="text-lg font-medium mb-4">Stock Level</Text>
          <View className="flex-row justify-between items-center mb-2">
            <Text className="text-base text-muted-foreground">
              Current Stock
            </Text>
            <Text className="text-lg font-medium">
              {item.quantity} / {item.maximumStock} {item.unit}
            </Text>
          </View>
          <Progress
            value={(item.quantity / item.maximumStock) * 100}
            className="h-2 mb-4"
          />

          {/* Stock Alerts */}
          {item.quantity <= item.reorderPoint && (
            <View className="flex-row items-center p-2 rounded-md bg-warning/10 mb-4">
              <AlertTriangle
                size={16}
                className="text-warning mr-2"
              />
              <Text className="text-sm text-warning">
                Low stock - Reorder point: {item.reorderPoint} {item.unit}
              </Text>
            </View>
          )}

          {/* Stock Movement */}
          <View className="flex-row gap-2">
            <View className="flex-1">
              <Input
                placeholder="Quantity"
                value={quantity}
                onChangeText={setQuantity}
                keyboardType="numeric"
                className="mb-2"
              />
            </View>
            <Button
              variant="outline"
              onPress={() => handleStockUpdate('receive')}
              className="mb-2"
            >
              <Plus size={16} className="mr-2" />
              Receive
            </Button>
            <Button
              variant="outline"
              onPress={() => handleStockUpdate('dispatch')}
              className="mb-2"
            >
              <Minus size={16} className="mr-2" />
              Dispatch
            </Button>
          </View>
        </Card>

        {/* Details */}
        <Card className="m-4 p-4">
          <Text className="text-lg font-medium mb-4">Details</Text>
          
          <View className="mb-4">
            <Text className="text-sm text-muted-foreground mb-1">Category</Text>
            <Text className="text-base">{item.category}</Text>
          </View>

          <View className="mb-4">
            <Text className="text-sm text-muted-foreground mb-1">Location</Text>
            <Text className="text-base">
              {item.location.warehouse} • Zone {item.location.zone} • 
              Shelf {item.location.shelf} • Bin {item.location.bin}
            </Text>
          </View>

          {item.expirationDate && (
            <View className="mb-4">
              <Text className="text-sm text-muted-foreground mb-1">
                Expiration Date
              </Text>
              <Text className="text-base">
                {new Date(item.expirationDate).toLocaleDateString()}
              </Text>
            </View>
          )}

          {item.batchNumber && (
            <View className="mb-4">
              <Text className="text-sm text-muted-foreground mb-1">
                Batch Number
              </Text>
              <Text className="text-base">{item.batchNumber}</Text>
            </View>
          )}

          <View className="mb-4">
            <Text className="text-sm text-muted-foreground mb-1">Supplier</Text>
            <Text className="text-base">{item.supplier.name}</Text>
            <Text className="text-sm text-muted-foreground">
              Lead Time: {item.supplier.leadTime} days
            </Text>
          </View>

          <View className="mb-4">
            <Text className="text-sm text-muted-foreground mb-1">Barcodes</Text>
            <View className="flex-row flex-wrap gap-2">
              {item.barcodes.map((barcode) => (
                <View
                  key={barcode}
                  className="flex-row items-center bg-muted rounded-md p-2"
                >
                  <BarcodeScan size={16} className="mr-2" />
                  <Text className="text-sm">{barcode}</Text>
                </View>
              ))}
            </View>
          </View>

          {item.notes && (
            <View>
              <Text className="text-sm text-muted-foreground mb-1">Notes</Text>
              <Text className="text-base">{item.notes}</Text>
            </View>
          )}
        </Card>

        {/* Movement History */}
        <Card className="m-4 p-4">
          <Text className="text-lg font-medium mb-4">Movement History</Text>
          {movements.map((movement) => (
            <View
              key={movement.id}
              className="flex-row items-center py-2 border-b border-border"
            >
              {movement.type === 'receive' ? (
                <Plus size={16} className="text-success mr-2" />
              ) : movement.type === 'dispatch' ? (
                <Minus size={16} className="text-destructive mr-2" />
              ) : (
                <ArrowLeftRight size={16} className="text-primary mr-2" />
              )}
              <View className="flex-1">
                <Text className="text-base">
                  {movement.type.charAt(0).toUpperCase() + movement.type.slice(1)}
                </Text>
                <Text className="text-sm text-muted-foreground">
                  {new Date(movement.timestamp).toLocaleString()}
                </Text>
              </View>
              <Text className="text-base font-medium">
                {movement.type === 'receive' ? '+' : '-'}
                {movement.quantity} {item.unit}
              </Text>
            </View>
          ))}
        </Card>
      </ScrollView>

      {/* Barcode Scanner Modal */}
      {showScanner && (
        <View className="absolute inset-0 bg-background">
          <BarcodeScanner
            onScan={(barcode) => {
              // Handle barcode scan
              setShowScanner(false)
            }}
            onClose={() => setShowScanner(false)}
          />
        </View>
      )}
    </View>
  )
}
