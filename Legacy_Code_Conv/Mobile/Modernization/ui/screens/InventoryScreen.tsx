import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  RefreshControl,
  TouchableOpacity,
  TextInput,
} from 'react-native'
import { useNavigation } from '@react-navigation/native'
import type { NativeStackNavigationProp } from '@react-navigation/native-stack'
import { RootStackParamList } from '../navigation/types'
import { useFetchInventory } from '@/hooks/useFetchInventory'
import { BarcodeScanner } from '../inventory/BarcodeScanner'
import { InventoryCard } from '../inventory/InventoryCard'
import { ScrollView } from '../ui/scroll-view'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { LoadingScreen } from '../ui/loading-screen'
import {
  Search,
  BarcodeScan,
  Filter,
  Plus,
  AlertCircle,
} from 'lucide-react-native'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

type InventoryScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'Inventory'
>

export function InventoryScreen() {
  const navigation = useNavigation<InventoryScreenNavigationProp>()
  const [searchQuery, setSearchQuery] = useState('')
  const [showScanner, setShowScanner] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const { toast } = useToast()

  const {
    inventory,
    categories,
    isLoading,
    error,
    refetch,
    isRefetching,
    searchItems,
    findByBarcode,
  } = useFetchInventory()

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query)
    searchItems(query, selectedCategory)
  }, [selectedCategory, searchItems])

  const handleScan = useCallback(async (barcode: string) => {
    try {
      const item = await findByBarcode(barcode)
      if (item) {
        navigation.navigate('InventoryDetails', { id: item.id })
      } else {
        toast({
          title: 'Item Not Found',
          description: 'No inventory item found with this barcode.',
          variant: 'destructive',
        })
      }
    } catch (error) {
      console.error('Error scanning barcode:', error)
      toast({
        title: 'Scan Error',
        description: 'Failed to process barcode. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setShowScanner(false)
    }
  }, [navigation, findByBarcode, toast])

  if (isLoading) {
    return <LoadingScreen />
  }

  if (error) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <AlertCircle
          size={48}
          className="text-destructive mb-4"
        />
        <Text className="text-lg font-medium text-center mb-2">
          Failed to load inventory
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

  return (
    <View className="flex-1 bg-background">
      {/* Header */}
      <View className="p-4 border-b border-border">
        {/* Search Bar */}
        <View className="flex-row gap-2 mb-4">
          <Input
            placeholder="Search inventory..."
            value={searchQuery}
            onChangeText={handleSearch}
            className="flex-1"
            leftIcon={<Search size={16} />}
          />
          <Button
            variant="outline"
            size="icon"
            onPress={() => setShowScanner(true)}
          >
            <BarcodeScan size={16} />
          </Button>
        </View>

        {/* Category Filter */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          className="gap-2"
        >
          <TouchableOpacity
            onPress={() => {
              setSelectedCategory(null)
              searchItems(searchQuery, null)
            }}
            className={cn(
              'px-4 py-2 rounded-full',
              !selectedCategory
                ? 'bg-primary'
                : 'bg-muted'
            )}
          >
            <Text
              className={cn(
                'text-sm font-medium',
                !selectedCategory
                  ? 'text-primary-foreground'
                  : 'text-foreground'
              )}
            >
              All
            </Text>
          </TouchableOpacity>
          {categories.map((category) => (
            <TouchableOpacity
              key={category}
              onPress={() => {
                setSelectedCategory(category)
                searchItems(searchQuery, category)
              }}
              className={cn(
                'px-4 py-2 rounded-full',
                selectedCategory === category
                  ? 'bg-primary'
                  : 'bg-muted'
              )}
            >
              <Text
                className={cn(
                  'text-sm font-medium',
                  selectedCategory === category
                    ? 'text-primary-foreground'
                    : 'text-foreground'
                )}
              >
                {category}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Inventory List */}
      <ScrollView
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
          />
        }
        className="flex-1 p-4"
      >
        {inventory.length === 0 ? (
          <View className="flex-1 items-center justify-center py-8">
            <Package
              size={48}
              className="text-muted-foreground mb-4"
            />
            <Text className="text-lg font-medium text-center mb-2">
              No items found
            </Text>
            <Text className="text-sm text-muted-foreground text-center">
              Try adjusting your search or filters
            </Text>
          </View>
        ) : (
          <View className="gap-4">
            {inventory.map((item) => (
              <InventoryCard
                key={item.id}
                item={item}
                onPress={() =>
                  navigation.navigate('InventoryDetails', { id: item.id })
                }
              />
            ))}
          </View>
        )}
      </ScrollView>

      {/* Add Item FAB */}
      <TouchableOpacity
        onPress={() => navigation.navigate('AddInventoryItem')}
        className="absolute bottom-4 right-4 w-14 h-14 bg-primary rounded-full items-center justify-center shadow-lg"
      >
        <Plus size={24} className="text-primary-foreground" />
      </TouchableOpacity>

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
