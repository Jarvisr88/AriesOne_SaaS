import React from 'react';
import {
  Box,
  Flex,
  useColorMode,
  useColorModeValue,
  IconButton,
  HStack,
  VStack,
  Heading,
  Text,
  Drawer,
  DrawerContent,
  useDisclosure,
  BoxProps,
  FlexProps,
  Container,
  useBreakpointValue,
} from '@chakra-ui/react';
import {
  FiMenu,
  FiX,
  FiSun,
  FiMoon,
  FiHome,
  FiTruck,
  FiPackage,
  FiBarChart2,
  FiSettings,
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const MotionBox = motion(Box);

interface NavItemProps extends FlexProps {
  icon: React.ReactElement;
  children: string;
  path: string;
}

const NavItem = ({ icon, children, path, ...rest }: NavItemProps) => {
  const location = useLocation();
  const isActive = location.pathname === path;
  const activeBg = useColorModeValue('brand.50', 'brand.900');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');

  return (
    <Link to={path}>
      <MotionBox
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Flex
          align="center"
          p="4"
          mx="4"
          borderRadius="lg"
          role="group"
          cursor="pointer"
          bg={isActive ? activeBg : 'transparent'}
          color={isActive ? 'brand.500' : 'inherit'}
          _hover={{
            bg: hoverBg,
          }}
          {...rest}
        >
          {React.cloneElement(icon, {
            size: "20",
            style: { marginRight: '12px' },
          })}
          {children}
        </Flex>
      </MotionBox>
    </Link>
  );
};

const SidebarContent = ({ ...props }: BoxProps) => {
  return (
    <Box
      bg={useColorModeValue('white', 'gray.900')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...props}
    >
      <VStack h="20" align="center" mx="8" justifyContent="center">
        <Text fontSize="2xl" fontWeight="bold" color="brand.500">
          AriesOne
        </Text>
      </VStack>
      <VStack spacing={4} align="stretch">
        <NavItem icon={<FiHome />} path="/">
          Dashboard
        </NavItem>
        <NavItem icon={<FiTruck />} path="/deliveries">
          Deliveries
        </NavItem>
        <NavItem icon={<FiPackage />} path="/inventory">
          Inventory
        </NavItem>
        <NavItem icon={<FiBarChart2 />} path="/analytics">
          Analytics
        </NavItem>
        <NavItem icon={<FiSettings />} path="/settings">
          Settings
        </NavItem>
      </VStack>
    </Box>
  );
};

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();
  const isMobile = useBreakpointValue({ base: true, md: false });

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.800')}>
      <SidebarContent display={{ base: 'none', md: 'block' }} />
      <Drawer
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full"
      >
        <DrawerContent>
          <SidebarContent onClose={onClose} />
        </DrawerContent>
      </Drawer>

      {/* Navbar */}
      <Flex
        ml={{ base: 0, md: 60 }}
        px={{ base: 4, md: 6 }}
        height="20"
        alignItems="center"
        bg={useColorModeValue('white', 'gray.900')}
        borderBottomWidth="1px"
        borderBottomColor={useColorModeValue('gray.200', 'gray.700')}
        justifyContent="space-between"
      >
        <IconButton
          display={{ base: 'flex', md: 'none' }}
          onClick={onOpen}
          variant="outline"
          aria-label="open menu"
          icon={<FiMenu />}
        />

        <HStack spacing={8} alignItems="center">
          {isMobile && (
            <Text fontSize="2xl" fontWeight="bold" color="brand.500">
              AriesOne
            </Text>
          )}
        </HStack>

        <HStack spacing={4}>
          <IconButton
            aria-label={`Switch to ${colorMode === 'light' ? 'dark' : 'light'} mode`}
            icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
            onClick={toggleColorMode}
            variant="ghost"
          />
        </HStack>
      </Flex>

      {/* Main Content */}
      <Box
        ml={{ base: 0, md: 60 }}
        p={{ base: 4, md: 8 }}
      >
        <Container maxW="container.xl">
          {children}
        </Container>
      </Box>
    </Box>
  );
};
