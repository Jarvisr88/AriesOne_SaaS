/**
 * Browser warning component.
 * 
 * This component displays warnings for unsupported browsers.
 */
import React from 'react';
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Box,
  Button,
  Link,
  List,
  ListItem,
  useDisclosure,
} from '@chakra-ui/react';
import {
  isBrowserSupported,
  getBrowserInfo,
} from '../../utils/browserCompatibility';


export const BrowserWarning: React.FC = () => {
  const { isOpen, onClose } = useDisclosure({ defaultIsOpen: true });
  const { supported, warnings } = isBrowserSupported();
  const browserInfo = getBrowserInfo();
  
  if (!isOpen || supported) {
    return null;
  }
  
  return (
    <Alert
      status="warning"
      variant="solid"
      flexDirection="column"
      alignItems="start"
      p={4}
      borderRadius="md"
    >
      <Box mb={4}>
        <AlertIcon />
        <AlertTitle>Browser Compatibility Warning</AlertTitle>
        <AlertDescription>
          Your browser ({browserInfo.name} {browserInfo.version}) may not be fully compatible with this application.
        </AlertDescription>
      </Box>
      
      <List spacing={2} mb={4}>
        {warnings.map((warning, index) => (
          <ListItem key={index}>
            • {warning}
          </ListItem>
        ))}
      </List>
      
      <Box>
        <Button
          size="sm"
          colorScheme="orange"
          mr={4}
          onClick={onClose}
        >
          Continue Anyway
        </Button>
        
        <Link
          href="https://www.google.com/chrome/"
          isExternal
          color="white"
          textDecoration="underline"
        >
          Download Chrome
        </Link>
      </Box>
    </Alert>
  );
};
