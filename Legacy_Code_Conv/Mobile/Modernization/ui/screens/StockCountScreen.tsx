import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  RefreshControl,
  TouchableOpacity,
  Alert,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { InventoryCount } from '../inventory/types'
import { StockCount } from '../inventory/StockCount'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { ScrollView } from '../ui/scroll-view'
import { LoadingScreen } from '../ui/loading-screen'
import {
  ClipboardList,
  Calendar,
  User,
  AlertTriangle,
  Plus,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'
import { formatDate, formatTime } from '@/lib/format'

type StockCountScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'StockCount'
>

export function StockCountScreen() {
  const navigation = useNavigation<StockCountScreenNavigationProp>()
  const [activeCount, setActiveCount] = useState<InventoryCount | null>(null)
  const { toast } = useToast()

  const {
    counts,
    isLoading,
    error,
    refetch,
    isRefetching,
    startCount,
    completeCount,
    cancelCount,
  } = useStockCounts()

  const handleStartCount = useCallback(async () => {
    try {
      const newCount = await startCount()
      setActiveCount(newCount)
    } catch (error) {
      console.error('Error starting count:', error)
      toast({
        title: 'Error',
        description: 'Failed to start stock count',
        variant: 'destructive',
      })
    }
  }, [startCount, toast])

  const handleCompleteCount = useCallback(async (count: InventoryCount) => {
    try {
      await completeCount(count)
      setActiveCount(null)
      toast({
        title: 'Count Completed',
        description: 'Stock count has been completed successfully.',
      })
    } catch (error) {
      console.error('Error completing count:', error)
      toast({
        title: 'Error',
        description: 'Failed to complete stock count',
        variant: 'destructive',
      })
    }
  }, [completeCount, toast])

  const handleCancelCount = useCallback(async () => {
    if (!activeCount) return

    Alert.alert(
      'Cancel Count',
      'Are you sure you want to cancel this stock count?',
      [
        {
          text: 'Continue Counting',
          style: 'cancel',
        },
        {
          text: 'Cancel Count',
          style: 'destructive',
          onPress: async () => {
            try {
              await cancelCount(activeCount.id)
              setActiveCount(null)
              toast({
                title: 'Count Cancelled',
                description: 'Stock count has been cancelled.',
              })
            } catch (error) {
              console.error('Error cancelling count:', error)
              toast({
                title: 'Error',
                description: 'Failed to cancel stock count',
                variant: 'destructive',
              })
            }
          },
        },
      ]
    )
  }, [activeCount, cancelCount, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  if (error) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <AlertTriangle
          size={48}
          className="text-destructive mb-4"
        />
        <Text className="text-lg font-medium text-center mb-2">
          Failed to load stock counts
        </Text>
        <Text className="text-sm text-muted-foreground text-center mb-4">
          {error.message}
        </Text>
        <Button onPress={() => refetch()}>
          Try Again
        </Button>
      </View>
    )
  }

  if (activeCount) {
    return (
      <StockCount
        count={activeCount}
        onComplete={handleCompleteCount}
        onCancel={handleCancelCount}
      />
    )
  }

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        <Text className="text-xl font-bold mb-2">Stock Counts</Text>
        <Button
          onPress={handleStartCount}
          className="w-full"
        >
          <Plus size={16} className="mr-2" />
          Start New Count
        </Button>
      </View>

      {/* Count List */}
      <ScrollView
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
          />
        }
        className="flex-1 p-4"
      >
        {counts.length === 0 ? (
          <View className="flex-1 items-center justify-center py-8">
            <ClipboardList
              size={48}
              className="text-muted-foreground mb-4"
            />
            <Text className="text-lg font-medium text-center mb-2">
              No stock counts
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Start a new count to track inventory
            </Text>
          </View>
        ) : (
          <View className="gap-4">
            {counts.map((count) => (
              <Card
                key={count.id}
                className="p-4"
              >
                {/* Header */}
                <View className="flex-row justify-between items-start mb-4">
                  <View className="flex-1">
                    <Text className="text-lg font-medium mb-1">
                      Count #{count.id}
                    </Text>
                    <Text
                      className={cn(
                        'text-sm font-medium',
                        count.status === 'completed'
                          ? 'text-success'
                          : count.status === 'cancelled'
                          ? 'text-destructive'
                          : 'text-primary'
                      )}
                    >
                      {count.status.charAt(0).toUpperCase() + count.status.slice(1)}
                    </Text>
                  </View>
                  <View className="items-end">
                    <Text className="text-sm text-muted-foreground">
                      {formatDate(count.startTime)}
                    </Text>
                    <Text className="text-sm text-muted-foreground">
                      {formatTime(count.startTime)}
                    </Text>
                  </View>
                </View>

                {/* Location */}
                <View className="mb-4">
                  <Text className="text-sm text-muted-foreground mb-1">
                    Location
                  </Text>
                  <Text className="text-base">
                    {count.location.warehouse} • Zone {count.location.zone}
                    {count.location.shelf && ` • Shelf ${count.location.shelf}`}
                    {count.location.bin && ` • Bin ${count.location.bin}`}
                  </Text>
                </View>

                {/* Stats */}
                <View className="flex-row gap-4 mb-4">
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-1">
                      Items
                    </Text>
                    <Text className="text-base font-medium">
                      {count.items.length}
                    </Text>
                  </View>
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-1">
                      Variances
                    </Text>
                    <Text className="text-base font-medium">
                      {count.items.filter(item => item.variance !== 0).length}
                    </Text>
                  </View>
                  <View className="flex-1">
                    <Text className="text-sm text-muted-foreground mb-1">
                      Duration
                    </Text>
                    <Text className="text-base font-medium">
                      {count.endTime
                        ? formatDuration(
                            new Date(count.startTime),
                            new Date(count.endTime)
                          )
                        : '-'}
                    </Text>
                  </View>
                </View>

                {/* Assigned Users */}
                <View className="mb-4">
                  <Text className="text-sm text-muted-foreground mb-2">
                    Assigned To
                  </Text>
                  <View className="flex-row flex-wrap gap-2">
                    {count.assignedTo.map((userId) => (
                      <View
                        key={userId}
                        className="flex-row items-center bg-muted rounded-full px-3 py-1"
                      >
                        <User size={12} className="mr-2" />
                        <Text className="text-sm">{userId}</Text>
                      </View>
                    ))}
                  </View>
                </View>

                {/* Actions */}
                <View className="flex-row gap-2">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onPress={() =>
                      navigation.navigate('StockCountDetails', { id: count.id })
                    }
                  >
                    View Details
                  </Button>
                  {count.status === 'completed' && (
                    <Button
                      variant="outline"
                      className="flex-1"
                      onPress={() =>
                        navigation.navigate('StockCountReport', { id: count.id })
                      }
                    >
                      View Report
                    </Button>
                  )}
                </View>
              </Card>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  )
}
