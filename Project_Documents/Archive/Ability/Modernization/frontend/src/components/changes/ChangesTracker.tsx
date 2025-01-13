import React, { useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  IconButton,
  Spinner,
  useColorModeValue,
  Tooltip,
  Button,
} from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiRefreshCw, FiTrash2, FiAlertCircle } from 'react-icons/fi';
import { useChanges, Change } from '../../context/ChangesContext';
import { format } from 'date-fns';

const MotionBox = motion(Box);

interface ChangeItemProps {
  change: Change;
}

const ChangeItem: React.FC<ChangeItemProps> = ({ change }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const getChangeColor = (type: string) => {
    switch (type) {
      case 'create':
        return 'green';
      case 'update':
        return 'blue';
      case 'delete':
        return 'red';
      default:
        return 'gray';
    }
  };

  const formatValue = (value: any) => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  return (
    <MotionBox
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.2 }}
      p={4}
      bg={bgColor}
      borderRadius="lg"
      borderWidth="1px"
      borderColor={borderColor}
      shadow="sm"
      _hover={{ shadow: 'md' }}
    >
      <VStack align="stretch" spacing={2}>
        <HStack justify="space-between">
          <Badge colorScheme={getChangeColor(change.type)}>
            {change.type.toUpperCase()}
          </Badge>
          <Text fontSize="sm" color="gray.500">
            {format(new Date(change.timestamp), 'MMM d, yyyy HH:mm:ss')}
          </Text>
        </HStack>

        <Text fontWeight="medium">
          {change.entity} {change.field && `- ${change.field}`}
        </Text>

        {change.type === 'update' && (
          <HStack spacing={4} fontSize="sm">
            <Text color="gray.500">
              From: {formatValue(change.oldValue)}
            </Text>
            <Text color="gray.500">
              To: {formatValue(change.newValue)}
            </Text>
          </HStack>
        )}

        {change.metadata && Object.keys(change.metadata).length > 0 && (
          <Box fontSize="sm">
            <Text color="gray.500" fontWeight="medium">
              Additional Info:
            </Text>
            {Object.entries(change.metadata).map(([key, value]) => (
              <Text key={key} color="gray.500">
                {key}: {formatValue(value)}
              </Text>
            ))}
          </Box>
        )}
      </VStack>
    </MotionBox>
  );
};

export const ChangesTracker: React.FC = () => {
  const {
    changes,
    pendingChanges,
    isLoading,
    error,
    lastSyncTimestamp,
    syncChanges,
    clearChanges,
    retryFailedChanges,
  } = useChanges();

  const syncInterval = 60000; // 1 minute

  const handleSync = useCallback(async () => {
    await syncChanges();
  }, [syncChanges]);

  // Auto-sync changes periodically
  useEffect(() => {
    const interval = setInterval(handleSync, syncInterval);
    return () => clearInterval(interval);
  }, [handleSync]);

  return (
    <Box>
      <HStack mb={4} justify="space-between">
        <VStack align="start" spacing={0}>
          <Text fontSize="lg" fontWeight="bold">
            Changes Tracker
          </Text>
          <Text fontSize="sm" color="gray.500">
            Last sync:{' '}
            {lastSyncTimestamp
              ? format(new Date(lastSyncTimestamp), 'MMM d, yyyy HH:mm:ss')
              : 'Never'}
          </Text>
        </VStack>

        <HStack>
          {error && (
            <Tooltip label="Error syncing changes">
              <IconButton
                aria-label="Retry failed changes"
                icon={<FiAlertCircle />}
                colorScheme="red"
                onClick={retryFailedChanges}
              />
            </Tooltip>
          )}

          <Tooltip label="Sync changes">
            <IconButton
              aria-label="Sync changes"
              icon={isLoading ? <Spinner size="sm" /> : <FiRefreshCw />}
              onClick={handleSync}
              isLoading={isLoading}
            />
          </Tooltip>

          <Tooltip label="Clear changes">
            <IconButton
              aria-label="Clear changes"
              icon={<FiTrash2 />}
              onClick={clearChanges}
            />
          </Tooltip>
        </HStack>
      </HStack>

      {pendingChanges.length > 0 && (
        <Box mb={4}>
          <Text fontSize="sm" fontWeight="medium" mb={2}>
            Pending Changes
          </Text>
          <VStack spacing={2}>
            {pendingChanges.map((change) => (
              <ChangeItem key={change.id} change={change} />
            ))}
          </VStack>
        </Box>
      )}

      <AnimatePresence>
        <VStack spacing={2}>
          {changes.map((change) => (
            <ChangeItem key={change.id} change={change} />
          ))}
        </VStack>
      </AnimatePresence>

      {changes.length === 0 && !isLoading && (
        <Box
          p={8}
          textAlign="center"
          color="gray.500"
          bg={useColorModeValue('gray.50', 'gray.900')}
          borderRadius="lg"
        >
          <Text>No changes tracked yet</Text>
        </Box>
      )}
    </Box>
  );
};
