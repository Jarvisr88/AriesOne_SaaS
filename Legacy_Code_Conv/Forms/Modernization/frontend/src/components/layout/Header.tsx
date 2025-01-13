/**
 * Header component.
 * 
 * This component provides the main navigation header.
 */
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Flex,
  Button,
  IconButton,
  useColorMode,
  useColorModeValue,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Text,
  HStack,
  Avatar,
} from '@chakra-ui/react';
import {
  MoonIcon,
  SunIcon,
  ChevronDownIcon,
} from '@chakra-ui/icons';
import { useAuth } from '../../hooks/useAuth';


export const Header: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { user, logout } = useAuth();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box
      as="header"
      position="fixed"
      top={0}
      left={0}
      right={0}
      zIndex={10}
      bg={bgColor}
      borderBottomWidth={1}
      borderColor={borderColor}
      px={4}
      py={2}
    >
      <Flex
        align="center"
        justify="space-between"
        maxW="container.xl"
        mx="auto"
      >
        <HStack spacing={8}>
          <Text
            as={RouterLink}
            to="/"
            fontSize="xl"
            fontWeight="bold"
            _hover={{ textDecoration: 'none' }}
          >
            AriesOne Forms
          </Text>
          
          <HStack spacing={4}>
            <Button
              as={RouterLink}
              to="/forms"
              variant="ghost"
              size="sm"
            >
              Forms
            </Button>
            <Button
              as={RouterLink}
              to="/companies"
              variant="ghost"
              size="sm"
            >
              Companies
            </Button>
            <Button
              as={RouterLink}
              to="/submissions"
              variant="ghost"
              size="sm"
            >
              Submissions
            </Button>
          </HStack>
        </HStack>
        
        <HStack spacing={4}>
          <IconButton
            aria-label={`Switch to ${
              colorMode === 'light' ? 'dark' : 'light'
            } mode`}
            icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            onClick={toggleColorMode}
            variant="ghost"
            size="sm"
          />
          
          {user && (
            <Menu>
              <MenuButton
                as={Button}
                rightIcon={<ChevronDownIcon />}
                variant="ghost"
                size="sm"
              >
                <HStack>
                  <Avatar
                    size="xs"
                    name={user.username}
                    src={user.avatar}
                  />
                  <Text>{user.username}</Text>
                </HStack>
              </MenuButton>
              <MenuList>
                <MenuItem
                  as={RouterLink}
                  to="/profile"
                >
                  Profile
                </MenuItem>
                <MenuItem
                  as={RouterLink}
                  to="/settings"
                >
                  Settings
                </MenuItem>
                <MenuItem
                  onClick={logout}
                  color="red.500"
                >
                  Logout
                </MenuItem>
              </MenuList>
            </Menu>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};
