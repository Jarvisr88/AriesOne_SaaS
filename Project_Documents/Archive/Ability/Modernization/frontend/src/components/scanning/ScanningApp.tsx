import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  IconButton,
  useToast,
  Spinner,
  Badge,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Switch,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { FiCamera, FiWifi, FiWifiOff, FiUpload, FiList } from 'react-icons/fi';
import { useQuery, useMutation } from '@tanstack/react-query';
import { format } from 'date-fns';

interface ScanResult {
  type: string;
  data: string;
  timestamp: string;
}

interface OfflineScan {
  type: string;
  image?: string;
  epc?: string;
  timestamp: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  device_id: string;
}

const ScanningApp: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [isOfflineMode, setIsOfflineMode] = useState(false);
  const [offlineScans, setOfflineScans] = useState<OfflineScan[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Check online status
  useEffect(() => {
    const handleOnline = () => setIsOfflineMode(false);
    const handleOffline = () => setIsOfflineMode(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Camera setup
  useEffect(() => {
    if (isScanning && videoRef.current) {
      navigator.mediaDevices
        .getUserMedia({ video: { facingMode: 'environment' } })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch((err) => {
          toast({
            title: 'Camera Error',
            description: err.message,
            status: 'error',
          });
        });
    }

    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, [isScanning, toast]);

  // Scan processing
  const processFrame = async () => {
    if (!canvasRef.current || !videoRef.current) return;

    const context = canvasRef.current.getContext('2d');
    if (!context) return;

    // Draw video frame to canvas
    context.drawImage(
      videoRef.current,
      0,
      0,
      canvasRef.current.width,
      canvasRef.current.height
    );

    // Get frame data
    const imageData = canvasRef.current.toDataURL('image/jpeg');

    try {
      if (isOfflineMode) {
        // Store scan offline
        const offlineScan: OfflineScan = {
          type: 'barcode',
          image: imageData,
          timestamp: new Date().toISOString(),
          device_id: 'mobile-device-1',
        };

        // Add location if available
        if ('geolocation' in navigator) {
          try {
            const position = await new Promise<GeolocationPosition>(
              (resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject);
              }
            );
            offlineScan.location = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            };
          } catch (error) {
            console.warn('Location not available:', error);
          }
        }

        setOfflineScans((prev) => [...prev, offlineScan]);
        
        toast({
          title: 'Scan Stored Offline',
          status: 'info',
        });
      } else {
        // Process scan online
        const response = await fetch('/api/scan', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image: imageData }),
        });

        if (!response.ok) throw new Error('Scan failed');

        const result = await response.json();
        
        toast({
          title: 'Scan Successful',
          description: result.data,
          status: 'success',
        });
      }
    } catch (error) {
      toast({
        title: 'Scan Error',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
      });
    }
  };

  // Sync offline scans
  const syncOfflineScans = async () => {
    try {
      const response = await fetch('/api/sync-offline-scans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scans: offlineScans }),
      });

      if (!response.ok) throw new Error('Sync failed');

      const result = await response.json();
      
      setOfflineScans([]);
      
      toast({
        title: 'Sync Successful',
        description: `${result.processed} scans synchronized`,
        status: 'success',
      });
    } catch (error) {
      toast({
        title: 'Sync Error',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
      });
    }
  };

  return (
    <Box p={4}>
      <VStack spacing={4} align="stretch">
        <HStack justify="space-between">
          <Text fontSize="xl" fontWeight="bold">
            Scanning App
          </Text>
          <HStack>
            <IconButton
              aria-label="Connection status"
              icon={isOfflineMode ? <FiWifiOff /> : <FiWifi />}
              colorScheme={isOfflineMode ? 'orange' : 'green'}
            />
            {isOfflineMode && offlineScans.length > 0 && (
              <IconButton
                aria-label="Sync offline scans"
                icon={<FiUpload />}
                onClick={syncOfflineScans}
              />
            )}
            <IconButton
              aria-label="View scan history"
              icon={<FiList />}
              onClick={onOpen}
            />
          </HStack>
        </HStack>

        <Box
          position="relative"
          width="100%"
          height="400px"
          bg="gray.900"
          borderRadius="lg"
          overflow="hidden"
        >
          {isScanning ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
              <canvas
                ref={canvasRef}
                style={{ display: 'none' }}
                width={1280}
                height={720}
              />
              <Box
                position="absolute"
                top="50%"
                left="50%"
                transform="translate(-50%, -50%)"
                width="80%"
                height="200px"
                border="2px solid"
                borderColor="green.500"
                opacity={0.5}
              />
            </>
          ) : (
            <VStack
              justify="center"
              align="center"
              height="100%"
              color="white"
              spacing={4}
            >
              <FiCamera size={48} />
              <Text>Press Start to begin scanning</Text>
            </VStack>
          )}
        </Box>

        <Button
          colorScheme={isScanning ? 'red' : 'green'}
          onClick={() => setIsScanning(!isScanning)}
          leftIcon={<FiCamera />}
        >
          {isScanning ? 'Stop Scanning' : 'Start Scanning'}
        </Button>

        {/* Offline Scans Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Scan History</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4} align="stretch" pb={4}>
                {offlineScans.map((scan, index) => (
                  <Box
                    key={index}
                    p={4}
                    borderWidth={1}
                    borderRadius="md"
                    position="relative"
                  >
                    <HStack justify="space-between">
                      <Badge colorScheme={scan.type === 'barcode' ? 'blue' : 'purple'}>
                        {scan.type}
                      </Badge>
                      <Text fontSize="sm" color="gray.500">
                        {format(new Date(scan.timestamp), 'MMM d, yyyy HH:mm:ss')}
                      </Text>
                    </HStack>
                    {scan.location && (
                      <Text fontSize="sm" mt={2}>
                        📍 {scan.location.latitude.toFixed(6)},{' '}
                        {scan.location.longitude.toFixed(6)}
                      </Text>
                    )}
                  </Box>
                ))}
                {offlineScans.length === 0 && (
                  <Text textAlign="center" color="gray.500">
                    No scans available
                  </Text>
                )}
              </VStack>
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default ScanningApp;
