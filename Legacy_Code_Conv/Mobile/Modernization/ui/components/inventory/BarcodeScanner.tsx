import React, { useState, useEffect, useCallback } from 'react'
import { View, Text, StyleSheet, Vibration } from 'react-native'
import { Camera, CameraType } from 'react-native-vision-camera'
import { useScanBarcodes, BarcodeFormat } from 'vision-camera-code-scanner'
import { useIsFocused } from '@react-navigation/native'
import { Button } from '../ui/button'
import { useToast } from '@/hooks/useToast'
import { cn } from '@/lib/utils'

interface BarcodeScannerProps {
  onScan: (barcode: string) => void
  onClose: () => void
  className?: string
}

export function BarcodeScanner({
  onScan,
  onClose,
  className,
}: BarcodeScannerProps) {
  const [hasPermission, setHasPermission] = useState(false)
  const [isActive, setIsActive] = useState(true)
  const isFocused = useIsFocused()
  const { toast } = useToast()

  const [frameProcessor, barcodes] = useScanBarcodes([
    BarcodeFormat.ALL_FORMATS,
  ])

  // Request camera permissions
  useEffect(() => {
    const requestPermission = async () => {
      const status = await Camera.requestCameraPermission()
      setHasPermission(status === 'authorized')
    }

    requestPermission()
  }, [])

  // Handle barcode detection
  useEffect(() => {
    if (barcodes.length > 0 && isActive) {
      const barcode = barcodes[0]
      if (barcode.rawValue) {
        setIsActive(false) // Prevent multiple scans
        Vibration.vibrate() // Haptic feedback
        onScan(barcode.rawValue)
      }
    }
  }, [barcodes, isActive, onScan])

  const handleError = useCallback((error: Error) => {
    console.error('Camera error:', error)
    toast({
      title: 'Camera Error',
      description: error.message,
      variant: 'destructive',
    })
  }, [toast])

  if (!hasPermission) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <Text className="text-lg font-medium text-center mb-4">
          Camera permission is required to scan barcodes
        </Text>
        <Button
          onPress={() => Camera.requestCameraPermission()}
          className="mb-2"
        >
          Request Permission
        </Button>
        <Button
          variant="outline"
          onPress={onClose}
        >
          Cancel
        </Button>
      </View>
    )
  }

  return (
    <View className={cn('flex-1', className)}>
      <Camera
        style={StyleSheet.absoluteFill}
        device={devices.back}
        isActive={isActive && isFocused}
        frameProcessor={frameProcessor}
        frameProcessorFps={5}
        onError={handleError}
      />

      {/* Scanning overlay */}
      <View className="flex-1 items-center justify-center">
        <View className="w-72 h-72 border-2 border-primary rounded-lg">
          <View className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-primary" />
          <View className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-primary" />
          <View className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-primary" />
          <View className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-primary" />
        </View>
        <Text className="text-sm text-muted-foreground mt-4">
          Position barcode within the frame
        </Text>
      </View>

      {/* Controls */}
      <View className="absolute bottom-0 left-0 right-0 p-4">
        <Button
          variant="outline"
          onPress={onClose}
          className="bg-background/80"
        >
          Cancel
        </Button>
      </View>
    </View>
  )
}
