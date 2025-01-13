import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  Alert,
  Image,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { MaintenanceTag, InventoryItem } from '../inventory/types'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { ImagePicker } from '../ui/image-picker'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Select } from '../ui/select'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import {
  Tool,
  BarcodeScan,
  Camera,
  AlertTriangle,
  Calendar,
  Clock,
  Tag,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import { formatDate } from '@/lib/format'

type MaintenanceTagScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'MaintenanceTag'
>

const PRIORITY_OPTIONS = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Critical', value: 'critical' },
]

const MAINTENANCE_TYPES = [
  { label: 'Repair', value: 'repair' },
  { label: 'Inspection', value: 'inspection' },
  { label: 'Calibration', value: 'calibration' },
  { label: 'Cleaning', value: 'cleaning' },
  { label: 'Replacement', value: 'replacement' },
]

export function MaintenanceTagScreen() {
  const navigation = useNavigation<MaintenanceTagScreenNavigationProp>()
  const { toast } = useToast()

  const [showScanner, setShowScanner] = useState(false)
  const [showImagePicker, setShowImagePicker] = useState(false)
  const [item, setItem] = useState<InventoryItem | null>(null)
  const [tag, setTag] = useState<Partial<MaintenanceTag>>({
    type: 'repair',
    priority: 'medium',
    status: 'pending',
    description: '',
    scheduledDate: new Date().toISOString(),
    estimatedDuration: 60, // minutes
    images: [],
  })

  const {
    isLoading,
    error,
    createMaintenanceTag,
  } = useMaintenanceTags()

  const handleScan = useCallback(async (barcode: string) => {
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
        description: `${scannedItem.name} ready for maintenance tag`,
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

  const handleAddImage = useCallback((uri: string) => {
    setTag(prev => ({
      ...prev,
      images: [...(prev.images || []), uri],
    }))
    setShowImagePicker(false)
  }, [])

  const handleRemoveImage = useCallback((index: number) => {
    setTag(prev => ({
      ...prev,
      images: prev.images?.filter((_, i) => i !== index),
    }))
  }, [])

  const handleCreate = useCallback(async () => {
    if (!item || !tag.description || !tag.scheduledDate) {
      toast({
        title: 'Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      })
      return
    }

    try {
      await createMaintenanceTag({
        ...tag,
        itemId: item.id,
        createdAt: new Date().toISOString(),
        createdBy: 'current-user-id', // Replace with actual user ID
      } as MaintenanceTag)

      toast({
        title: 'Tag Created',
        description: 'Maintenance tag has been created successfully',
      })

      navigation.goBack()
    } catch (error) {
      console.error('Error creating maintenance tag:', error)
      toast({
        title: 'Error',
        description: 'Failed to create maintenance tag',
        variant: 'destructive',
      })
    }
  }, [item, tag, createMaintenanceTag, navigation, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        <Text className="text-xl font-bold mb-4">Create Maintenance Tag</Text>

        {!item && (
          <Button
            onPress={() => setShowScanner(true)}
            className="w-full"
          >
            <BarcodeScan size={16} className="mr-2" />
            Scan Product
          </Button>
        )}
      </View>

      <ScrollView className="flex-1 p-4">
        {item ? (
          <>
            {/* Product Info */}
            <Card className="p-4 mb-4">
              <Text className="text-lg font-medium mb-4">Product Details</Text>
              
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

              <View>
                <Text className="text-sm text-muted-foreground mb-1">
                  Barcode
                </Text>
                <Text className="text-base">{item.barcode}</Text>
              </View>
            </Card>

            {/* Maintenance Details */}
            <Card className="p-4 mb-4">
              <Text className="text-lg font-medium mb-4">Maintenance Details</Text>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Type
                </Text>
                <Select
                  value={tag.type}
                  onValueChange={(value) =>
                    setTag(prev => ({ ...prev, type: value }))
                  }
                  items={MAINTENANCE_TYPES}
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Priority
                </Text>
                <Select
                  value={tag.priority}
                  onValueChange={(value) =>
                    setTag(prev => ({ ...prev, priority: value }))
                  }
                  items={PRIORITY_OPTIONS}
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Description
                </Text>
                <Input
                  value={tag.description}
                  onChangeText={(text) =>
                    setTag(prev => ({ ...prev, description: text }))
                  }
                  placeholder="Describe the maintenance needed"
                  multiline
                  numberOfLines={3}
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Scheduled Date
                </Text>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onPress={() => {
                    // Show date picker
                  }}
                >
                  <Calendar size={16} className="mr-2" />
                  {formatDate(tag.scheduledDate || new Date().toISOString())}
                </Button>
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Estimated Duration (minutes)
                </Text>
                <Input
                  value={tag.estimatedDuration?.toString()}
                  onChangeText={(text) => {
                    const num = parseInt(text, 10)
                    if (!isNaN(num) && num > 0) {
                      setTag(prev => ({ ...prev, estimatedDuration: num }))
                    }
                  }}
                  keyboardType="numeric"
                />
              </View>
            </Card>

            {/* Images */}
            <Card className="p-4 mb-4">
              <View className="flex-row justify-between items-center mb-4">
                <Text className="text-lg font-medium">Images</Text>
                <Button
                  variant="outline"
                  size="sm"
                  onPress={() => setShowImagePicker(true)}
                >
                  <Camera size={16} className="mr-2" />
                  Add Image
                </Button>
              </View>

              {tag.images && tag.images.length > 0 ? (
                <ScrollView
                  horizontal
                  className="flex-row gap-2"
                >
                  {tag.images.map((uri, index) => (
                    <View key={index} className="relative">
                      <Image
                        source={{ uri }}
                        className="w-24 h-24 rounded-md"
                      />
                      <Button
                        variant="destructive"
                        size="icon"
                        className="absolute top-1 right-1"
                        onPress={() => handleRemoveImage(index)}
                      >
                        <AlertTriangle size={12} />
                      </Button>
                    </View>
                  ))}
                </ScrollView>
              ) : (
                <Text className="text-sm text-muted-foreground">
                  No images added
                </Text>
              )}
            </Card>
          </>
        ) : (
          <View className="flex-1 items-center justify-center py-8">
            <Tool
              size={48}
              className="text-muted-foreground mb-4"
            />
            <Text className="text-lg font-medium text-center mb-2">
              No Product Selected
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Scan a product to create a maintenance tag
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Actions */}
      {item && (
        <View className="p-4 border-t border-border">
          <Button
            onPress={handleCreate}
            className="w-full"
            disabled={!tag.description || !tag.scheduledDate}
          >
            Create Maintenance Tag
          </Button>
        </View>
      )}

      {/* Barcode Scanner Modal */}
      {showScanner && (
        <View className="absolute inset-0 bg-background">
          <BarcodeScanner
            onScan={handleScan}
            onClose={() => setShowScanner(false)}
          />
        </View>
      )}

      {/* Image Picker Modal */}
      {showImagePicker && (
        <ImagePicker
          onClose={() => setShowImagePicker(false)}
          onSelect={handleAddImage}
        />
      )}
    </View>
  )
}
