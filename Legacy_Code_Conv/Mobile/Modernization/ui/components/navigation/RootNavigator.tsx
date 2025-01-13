import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { useColorScheme } from 'react-native'
import { RootStackParamList, NavigationTheme } from './types'
import { MainTabNavigator } from './MainTabNavigator'
import { DeliveryDetailsScreen } from '../screens/DeliveryDetailsScreen'
import { InventoryScannerScreen } from '../screens/InventoryScannerScreen'
import { ServiceOrderScreen } from '../screens/ServiceOrderScreen'
import { SettingsScreen } from '../screens/SettingsScreen'

const Stack = createNativeStackNavigator<RootStackParamList>()

const lightTheme: NavigationTheme = {
  dark: false,
  colors: {
    primary: '#0891b2', // cyan-600
    background: '#ffffff',
    card: '#ffffff',
    text: '#0f172a', // slate-900
    border: '#e2e8f0', // slate-200
    notification: '#ef4444', // red-500
  },
}

const darkTheme: NavigationTheme = {
  dark: true,
  colors: {
    primary: '#06b6d4', // cyan-500
    background: '#0f172a', // slate-900
    card: '#1e293b', // slate-800
    text: '#f8fafc', // slate-50
    border: '#334155', // slate-700
    notification: '#ef4444', // red-500
  },
}

export function RootNavigator() {
  const colorScheme = useColorScheme()
  const theme = colorScheme === 'dark' ? darkTheme : lightTheme

  return (
    <NavigationContainer theme={theme}>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
          gestureEnabled: true,
        }}
      >
        <Stack.Screen
          name="Main"
          component={MainTabNavigator}
        />
        <Stack.Screen
          name="DeliveryDetails"
          component={DeliveryDetailsScreen}
          options={{
            headerShown: true,
            title: 'Delivery Details',
            animation: 'slide_from_right',
          }}
        />
        <Stack.Screen
          name="InventoryScanner"
          component={InventoryScannerScreen}
          options={{
            headerShown: true,
            title: 'Scan Inventory',
            animation: 'slide_from_bottom',
            presentation: 'modal',
          }}
        />
        <Stack.Screen
          name="ServiceOrder"
          component={ServiceOrderScreen}
          options={{
            headerShown: true,
            title: 'Service Order',
            animation: 'slide_from_right',
          }}
        />
        <Stack.Screen
          name="Settings"
          component={SettingsScreen}
          options={{
            headerShown: true,
            title: 'Settings',
            animation: 'slide_from_right',
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  )
}
