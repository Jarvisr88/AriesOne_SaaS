import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  Alert,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { InventoryItem } from '../inventory/types'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import {
  Tag,
  BarcodeScan,
  Printer,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

type ProductRelabelScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'ProductRelabel'
>

export function ProductRelabelScreen() {
  const navigation = useNavigation<ProductRelabelScreenNavigationProp>()
  const { toast } = useToast()

  const [showScanner, setShowScanner] = useState(false)
  const [scanningNew, setScanningNew] = useState(false)
  const [item, setItem] = useState<InventoryItem | null>(null)
  const [newBarcode, setNewBarcode] = useState('')
  const [notes, setNotes] = useState('')
  const [printing, setPrinting] = useState(false)

  const {
    isLoading,
    error,
    relabelProduct,
    printLabel,
  } = useProductRelabel()

  const handleScanOriginal = useCallback(async (barcode: string) => {
    try {
      const response = await fetch(`/api/inventory/barcode/${barcode}`)
      if (!response.ok) {
        throw new Error('Item not found')
      }

      const scannedItem = await response.json()
      setItem(scannedItem)
      setShowScanner(false)

      toast({
        title: 'Item Found',
        description: `${scannedItem.name} ready for relabeling`,
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

  const handleScanNew = useCallback(async (barcode: string) => {
    try {
      // Verify barcode is not already in use
      const response = await fetch(`/api/inventory/barcode/${barcode}/verify`)
      if (!response.ok) {
        throw new Error('Barcode already in use')
      }

      setNewBarcode(barcode)
      setShowScanner(false)
      setScanningNew(false)

      toast({
        title: 'New Barcode Set',
        description: 'Ready to relabel product',
      })
    } catch (error) {
      console.error('Error verifying barcode:', error)
      toast({
        title: 'Barcode Error',
        description: error.message,
        variant: 'destructive',
      })
    }
  }, [toast])

  const handleRelabel = useCallback(async () => {
    if (!item || !newBarcode) return

    try {
      await relabelProduct({
        itemId: item.id,
        oldBarcode: item.barcode,
        newBarcode,
        notes,
      })

      setPrinting(true)
      await printLabel({
        itemId: item.id,
        barcode: newBarcode,
      })
      setPrinting(false)

      toast({
        title: 'Relabeling Complete',
        description: 'Product has been relabeled successfully',
      })

      navigation.goBack()
    } catch (error) {
      console.error('Error relabeling product:', error)
      toast({
        title: 'Error',
        description: 'Failed to relabel product',
        variant: 'destructive',
      })
    }
  }, [item, newBarcode, notes, relabelProduct, printLabel, navigation, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        <Text className="text-xl font-bold mb-4">Relabel Product</Text>

        {!item ? (
          <Button
            onPress={() => {
              setScanningNew(false)
              setShowScanner(true)
            }}
            className="w-full"
          >
            <BarcodeScan size={16} className="mr-2" />
            Scan Original Product
          </Button>
        ) : !newBarcode ? (
          <Button
            onPress={() => {
              setScanningNew(true)
              setShowScanner(true)
            }}
            className="w-full"
          >
            <BarcodeScan size={16} className="mr-2" />
            Scan New Label
          </Button>
        ) : null}
      </View>

      <ScrollView className="flex-1 p-4">
        {item ? (
          <Card className="p-4 mb-4">
            <Text className="text-lg font-medium mb-2">Product Details</Text>
            
            {/* Original Barcode */}
            <View className="mb-4">
              <Text className="text-sm text-muted-foreground mb-1">
                Original Barcode
              </Text>
              <View className="flex-row items-center bg-muted rounded-lg p-3">
                <Tag size={16} className="mr-2" />
                <Text className="text-sm font-medium">{item.barcode}</Text>
              </View>
            </View>

            {/* New Barcode */}
            <View className="mb-4">
              <Text className="text-sm text-muted-foreground mb-1">
                New Barcode
              </Text>
              {newBarcode ? (
                <View className="flex-row items-center bg-muted rounded-lg p-3">
                  <Tag size={16} className="mr-2" />
                  <Text className="text-sm font-medium">{newBarcode}</Text>
                </View>
              ) : (
                <Text className="text-sm text-muted-foreground">
                  Scan new barcode to continue
                </Text>
              )}
            </View>

            {/* Product Info */}
            <View className="mb-4">
              <Text className="text-sm text-muted-foreground mb-1">
                Product Name
              </Text>
              <Text className="text-base">{item.name}</Text>
            </View>

            <View className="mb-4">
              <Text className="text-sm text-muted-foreground mb-1">
                Serial Number
              </Text>
              <Text className="text-base">{item.serialNumber || 'N/A'}</Text>
            </View>

            {/* Notes */}
            <View>
              <Text className="text-sm text-muted-foreground mb-2">
                Relabeling Notes
              </Text>
              <Input
                value={notes}
                onChangeText={setNotes}
                placeholder="Add notes about relabeling"
                multiline
                numberOfLines={3}
              />
            </View>
          </Card>
        ) : (
          <View className="flex-1 items-center justify-center py-8">
            <Text className="text-lg font-medium text-center mb-2">
              No Product Selected
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Scan a product to begin relabeling
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Actions */}
      {item && newBarcode && (
        <View className="p-4 border-t border-border">
          <Button
            onPress={handleRelabel}
            className="w-full"
            disabled={printing}
          >
            {printing ? (
              <>
                <Printer size={16} className="mr-2 animate-spin" />
                Printing Label...
              </>
            ) : (
              <>
                <Printer size={16} className="mr-2" />
                Relabel & Print
              </>
            )}
          </Button>
        </View>
      )}

      {/* Barcode Scanner Modal */}
      {showScanner && (
        <View className="absolute inset-0 bg-background">
          <BarcodeScanner
            onScan={scanningNew ? handleScanNew : handleScanOriginal}
            onClose={() => {
              setShowScanner(false)
              setScanningNew(false)
            }}
          />
        </View>
      )}
    </View>
  )
}
