import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Image,
} from 'react-native'
import { useNavigation, useRoute } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { StockAudit, StockAuditItem } from '../inventory/types'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Select } from '../ui/select'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import { ImagePicker } from '../ui/image-picker'
import {
  AlertTriangle,
  Camera,
  Check,
  FileText,
  Plus,
  Trash2,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import { formatDate, formatTime } from '@/lib/format'

type StockAuditScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'StockAudit'
>

export function StockAuditScreen() {
  const navigation = useNavigation<StockAuditScreenNavigationProp>()
  const route = useRoute()
  const { toast } = useToast()

  const {
    audit,
    isLoading,
    error,
    refetch,
    isRefetching,
    updateAudit,
    resolveAudit,
    cancelAudit,
  } = useStockAudit(route.params?.id)

  const [selectedItem, setSelectedItem] = useState<StockAuditItem | null>(null)
  const [showImagePicker, setShowImagePicker] = useState(false)

  const handleUpdateItem = useCallback(async (
    itemId: string,
    updates: Partial<StockAuditItem>
  ) => {
    if (!audit) return

    try {
      const updatedItems = audit.items.map(item =>
        item.itemId === itemId ? { ...item, ...updates } : item
      )

      await updateAudit({
        ...audit,
        items: updatedItems,
      })

      toast({
        title: 'Item Updated',
        description: 'Audit item has been updated successfully.',
      })
    } catch (error) {
      console.error('Error updating item:', error)
      toast({
        title: 'Error',
        description: 'Failed to update audit item',
        variant: 'destructive',
      })
    }
  }, [audit, updateAudit, toast])

  const handleAddImage = useCallback(async (itemId: string, uri: string) => {
    if (!audit) return

    try {
      const item = audit.items.find(i => i.itemId === itemId)
      if (!item) return

      await handleUpdateItem(itemId, {
        images: [...(item.images || []), uri],
      })

      setShowImagePicker(false)
    } catch (error) {
      console.error('Error adding image:', error)
      toast({
        title: 'Error',
        description: 'Failed to add image',
        variant: 'destructive',
      })
    }
  }, [audit, handleUpdateItem, toast])

  const handleResolveAudit = useCallback(async (
    action: StockAudit['resolution']['action']
  ) => {
    if (!audit) return

    try {
      await resolveAudit({
        ...audit,
        status: 'resolved',
        resolution: {
          action,
          resolvedBy: 'current-user-id', // Replace with actual user ID
          resolvedAt: new Date().toISOString(),
          notes: '',
        },
      })

      toast({
        title: 'Audit Resolved',
        description: 'Stock audit has been resolved successfully.',
      })

      navigation.goBack()
    } catch (error) {
      console.error('Error resolving audit:', error)
      toast({
        title: 'Error',
        description: 'Failed to resolve audit',
        variant: 'destructive',
      })
    }
  }, [audit, resolveAudit, navigation, toast])

  const handleCancelAudit = useCallback(() => {
    if (!audit) return

    Alert.alert(
      'Cancel Audit',
      'Are you sure you want to cancel this audit?',
      [
        {
          text: 'Continue Audit',
          style: 'cancel',
        },
        {
          text: 'Cancel Audit',
          style: 'destructive',
          onPress: async () => {
            try {
              await cancelAudit(audit.id)
              toast({
                title: 'Audit Cancelled',
                description: 'Stock audit has been cancelled.',
              })
              navigation.goBack()
            } catch (error) {
              console.error('Error cancelling audit:', error)
              toast({
                title: 'Error',
                description: 'Failed to cancel audit',
                variant: 'destructive',
              })
            }
          },
        },
      ]
    )
  }, [audit, cancelAudit, navigation, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  if (error || !audit) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <AlertTriangle
          size={48}
          className="text-destructive mb-4"
        />
        <Text className="text-lg font-medium text-center mb-2">
          Failed to load audit
        </Text>
        <Text className="text-sm text-muted-foreground text-center mb-4">
          {error?.message || 'Audit not found'}
        </Text>
        <Button onPress={() => navigation.goBack()}>
          Go Back
        </Button>
      </View>
    )
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        <View className="flex-row justify-between items-center mb-2">
          <Text className="text-xl font-bold">
            Audit #{audit.id}
          </Text>
          <Text
            className={cn(
              'text-sm font-medium',
              audit.status === 'resolved'
                ? 'text-success'
                : audit.status === 'cancelled'
                ? 'text-destructive'
                : 'text-primary'
            )}
          >
            {audit.status.charAt(0).toUpperCase() + audit.status.slice(1)}
          </Text>
        </View>
        <Text className="text-sm text-muted-foreground">
          Created on {formatDate(audit.createdAt)} at {formatTime(audit.createdAt)}
        </Text>
      </View>

      {/* Content */}
      <ScrollView
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
          />
        }
        className="flex-1"
      >
        {/* Type and Notes */}
        <View className="p-4 border-b border-border">
          <Text className="text-sm font-medium mb-2">Type</Text>
          <Text className="text-base mb-4">
            {audit.type.charAt(0).toUpperCase() + audit.type.slice(1)}
          </Text>

          <Text className="text-sm font-medium mb-2">Notes</Text>
          <Text className="text-base">{audit.notes || 'No notes'}</Text>
        </View>

        {/* Items */}
        <View className="p-4">
          <Text className="text-lg font-medium mb-4">Items</Text>
          {audit.items.map((item) => (
            <Card
              key={item.itemId}
              className="mb-4 p-4"
            >
              <View className="flex-row justify-between items-start mb-4">
                <View className="flex-1">
                  <Text className="text-base font-medium mb-1">
                    {item.itemId}
                  </Text>
                  <Text className="text-sm text-destructive">
                    Variance: {item.variance}
                  </Text>
                </View>
                {item.action && (
                  <View className="items-end">
                    <Text className="text-sm font-medium">
                      Action: {item.action}
                    </Text>
                  </View>
                )}
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Reason
                </Text>
                <Input
                  value={item.reason}
                  onChangeText={(text) =>
                    handleUpdateItem(item.itemId, { reason: text })
                  }
                  placeholder="Enter reason"
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Action
                </Text>
                <Select
                  value={item.action}
                  onValueChange={(value) =>
                    handleUpdateItem(item.itemId, {
                      action: value as StockAuditItem['action'],
                    })
                  }
                  items={[
                    { label: 'Adjust', value: 'adjust' },
                    { label: 'Recount', value: 'recount' },
                    { label: 'Investigate', value: 'investigate' },
                    { label: 'Write Off', value: 'write_off' },
                  ]}
                  placeholder="Select action"
                />
              </View>

              <View className="mb-4">
                <Text className="text-sm text-muted-foreground mb-2">
                  Notes
                </Text>
                <Input
                  value={item.notes}
                  onChangeText={(text) =>
                    handleUpdateItem(item.itemId, { notes: text })
                  }
                  placeholder="Enter notes"
                  multiline
                  numberOfLines={3}
                />
              </View>

              {/* Images */}
              <View>
                <View className="flex-row justify-between items-center mb-2">
                  <Text className="text-sm text-muted-foreground">
                    Images
                  </Text>
                  <Button
                    variant="ghost"
                    size="sm"
                    onPress={() => {
                      setSelectedItem(item)
                      setShowImagePicker(true)
                    }}
                  >
                    <Camera size={16} className="mr-2" />
                    Add Image
                  </Button>
                </View>
                {item.images && item.images.length > 0 ? (
                  <ScrollView
                    horizontal
                    className="flex-row gap-2"
                  >
                    {item.images.map((uri, index) => (
                      <TouchableOpacity
                        key={index}
                        onPress={() => {
                          // Handle image preview
                        }}
                      >
                        <Image
                          source={{ uri }}
                          className="w-20 h-20 rounded-md"
                        />
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                ) : (
                  <Text className="text-sm text-muted-foreground">
                    No images
                  </Text>
                )}
              </View>
            </Card>
          ))}
        </View>
      </ScrollView>

      {/* Actions */}
      {audit.status === 'open' && (
        <View className="p-4 border-t border-border">
          <View className="flex-row gap-4">
            <Button
              variant="outline"
              className="flex-1"
              onPress={handleCancelAudit}
            >
              Cancel Audit
            </Button>
            <Button
              className="flex-1"
              onPress={() => {
                Alert.alert(
                  'Resolve Audit',
                  'Select an action to resolve this audit',
                  [
                    {
                      text: 'Cancel',
                      style: 'cancel',
                    },
                    {
                      text: 'Adjust',
                      onPress: () => handleResolveAudit('adjust'),
                    },
                    {
                      text: 'Recount',
                      onPress: () => handleResolveAudit('recount'),
                    },
                    {
                      text: 'Investigate',
                      onPress: () => handleResolveAudit('investigate'),
                    },
                    {
                      text: 'Write Off',
                      style: 'destructive',
                      onPress: () => handleResolveAudit('write_off'),
                    },
                  ]
                )
              }}
            >
              Resolve Audit
            </Button>
          </View>
        </View>
      )}

      {/* Image Picker Modal */}
      {showImagePicker && selectedItem && (
        <ImagePicker
          onClose={() => {
            setShowImagePicker(false)
            setSelectedItem(null)
          }}
          onSelect={(uri) => {
            handleAddImage(selectedItem.itemId, uri)
          }}
        />
      )}
    </View>
  )
}
