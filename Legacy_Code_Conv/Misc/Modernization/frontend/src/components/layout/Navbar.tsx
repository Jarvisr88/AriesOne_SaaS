/**
 * Navigation bar component
 */
import React from 'react';
import {
  Box,
  Container,
  Flex,
  HStack,
  Link,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  Text,
  useColorModeValue
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { ChevronDownIcon } from '@chakra-ui/icons';
import { useAuth } from '../../hooks/useAuth';

const NavLink: React.FC<{
  to: string;
  children: React.ReactNode;
}> = ({ to, children }) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);

  return (
    <Link
      as={RouterLink}
      to={to}
      px={4}
      py={2}
      rounded="md"
      color={isActive ? 'blue.500' : 'gray.600'}
      fontWeight={isActive ? 'semibold' : 'normal'}
      bg={isActive ? 'blue.50' : 'transparent'}
      _hover={{
        textDecoration: 'none',
        bg: 'gray.100'
      }}
    >
      {children}
    </Link>
  );
};

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      bg={bgColor}
      borderBottom="1px"
      borderColor={borderColor}
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Container maxW="container.xl">
        <Flex
          h={16}
          alignItems="center"
          justifyContent="space-between"
        >
          <HStack spacing={8} alignItems="center">
            <Text
              fontSize="xl"
              fontWeight="bold"
              color="blue.500"
            >
              AriesOne
            </Text>
            <HStack
              as="nav"
              spacing={4}
              display={{ base: 'none', md: 'flex' }}
            >
              <NavLink to="/deposits">
                Deposits
              </NavLink>
              <NavLink to="/voids">
                Voids
              </NavLink>
              <NavLink to="/purchase-orders">
                Purchase Orders
              </NavLink>
            </HStack>
          </HStack>

          <Menu>
            <MenuButton
              as={Button}
              variant="ghost"
              rightIcon={<ChevronDownIcon />}
            >
              <HStack>
                <Avatar
                  size="sm"
                  name={user?.name}
                  src={user?.avatar}
                />
                <Text display={{ base: 'none', md: 'block' }}>
                  {user?.name}
                </Text>
              </HStack>
            </MenuButton>
            <MenuList>
              <MenuItem as={RouterLink} to="/profile">
                Profile
              </MenuItem>
              <MenuItem as={RouterLink} to="/settings">
                Settings
              </MenuItem>
              <MenuItem onClick={logout}>
                Logout
              </MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </Container>
    </Box>
  );
};
