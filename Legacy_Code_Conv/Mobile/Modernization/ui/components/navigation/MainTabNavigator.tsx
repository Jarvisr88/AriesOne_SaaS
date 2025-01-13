import React from 'react'
import { Platform } from 'react-native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { useTheme } from '@react-navigation/native'
import { Home, Truck, Package, User } from 'lucide-react-native'
import { MainTabParamList } from './types'
import { HomeScreen } from '../screens/HomeScreen'
import { DeliveriesScreen } from '../screens/DeliveriesScreen'
import { InventoryScreen } from '../screens/InventoryScreen'
import { ProfileScreen } from '../screens/ProfileScreen'

const Tab = createBottomTabNavigator<MainTabParamList>()

export function MainTabNavigator() {
  const { colors } = useTheme()

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.text,
        tabBarStyle: {
          backgroundColor: colors.card,
          borderTopColor: colors.border,
          height: Platform.OS === 'ios' ? 88 : 60,
          paddingBottom: Platform.OS === 'ios' ? 28 : 8,
          paddingTop: 8,
        },
        headerStyle: {
          backgroundColor: colors.card,
        },
        headerTintColor: colors.text,
        headerShadowVisible: false,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Home
              size={size}
              color={color}
            />
          ),
        }}
      />
      <Tab.Screen
        name="Deliveries"
        component={DeliveriesScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Truck
              size={size}
              color={color}
            />
          ),
          tabBarBadge: 3, // Example: Show number of pending deliveries
        }}
      />
      <Tab.Screen
        name="Inventory"
        component={InventoryScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Package
              size={size}
              color={color}
            />
          ),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <User
              size={size}
              color={color}
            />
          ),
        }}
      />
    </Tab.Navigator>
  )
}
