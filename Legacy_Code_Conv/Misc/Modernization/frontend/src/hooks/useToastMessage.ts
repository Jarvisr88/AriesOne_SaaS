/**
 * Custom hook for consistent toast notifications
 */
import { useToast, UseToastOptions } from '@chakra-ui/react';

interface ToastConfig {
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

const defaultConfig: UseToastOptions = {
  duration: 5000,
  isClosable: true,
  position: 'top-right'
};

export const useToastMessage = (): ToastConfig => {
  const toast = useToast();

  const success = (message: string, title?: string) => {
    toast({
      ...defaultConfig,
      title: title || 'Success',
      description: message,
      status: 'success',
      duration: 3000
    });
  };

  const error = (message: string, title?: string) => {
    toast({
      ...defaultConfig,
      title: title || 'Error',
      description: message,
      status: 'error'
    });
  };

  const warning = (message: string, title?: string) => {
    toast({
      ...defaultConfig,
      title: title || 'Warning',
      description: message,
      status: 'warning'
    });
  };

  const info = (message: string, title?: string) => {
    toast({
      ...defaultConfig,
      title: title || 'Info',
      description: message,
      status: 'info'
    });
  };

  return {
    success,
    error,
    warning,
    info
  };
};
