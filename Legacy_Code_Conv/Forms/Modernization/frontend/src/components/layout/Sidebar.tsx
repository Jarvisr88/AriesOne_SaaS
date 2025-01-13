/**
 * Sidebar component.
 * 
 * This component provides navigation and context-specific actions.
 */
import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Box,
  VStack,
  Link,
  Icon,
  Text,
  useColorModeValue,
  Divider,
} from '@chakra-ui/react';
import {
  FiHome,
  FiFileText,
  FiUsers,
  FiInbox,
  FiSettings,
  FiHelpCircle,
} from 'react-icons/fi';


interface NavItemProps {
  to: string;
  icon: React.ElementType;
  children: React.ReactNode;
}

const NavItem: React.FC<NavItemProps> = ({
  to,
  icon,
  children,
}) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);
  
  const bgColor = useColorModeValue('gray.100', 'gray.700');
  const activeColor = useColorModeValue('blue.500', 'blue.200');
  
  return (
    <Link
      as={RouterLink}
      to={to}
      w="full"
      p={3}
      borderRadius="md"
      display="flex"
      alignItems="center"
      color={isActive ? activeColor : undefined}
      bg={isActive ? bgColor : undefined}
      _hover={{
        textDecoration: 'none',
        bg: bgColor,
      }}
    >
      <Icon as={icon} mr={3} />
      <Text fontWeight={isActive ? 'medium' : 'normal'}>
        {children}
      </Text>
    </Link>
  );
};

export const Sidebar: React.FC = () => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box
      as="nav"
      position="fixed"
      top={16}
      left={0}
      bottom={0}
      w={64}
      bg={useColorModeValue('white', 'gray.800')}
      borderRightWidth={1}
      borderColor={borderColor}
      py={6}
      px={4}
      overflowY="auto"
    >
      <VStack spacing={2} align="stretch">
        <NavItem to="/" icon={FiHome}>
          Dashboard
        </NavItem>
        <NavItem to="/forms" icon={FiFileText}>
          Forms
        </NavItem>
        <NavItem to="/companies" icon={FiUsers}>
          Companies
        </NavItem>
        <NavItem to="/submissions" icon={FiInbox}>
          Submissions
        </NavItem>
        
        <Divider my={4} />
        
        <NavItem to="/settings" icon={FiSettings}>
          Settings
        </NavItem>
        <NavItem to="/help" icon={FiHelpCircle}>
          Help & Support
        </NavItem>
      </VStack>
    </Box>
  );
};
