/**
 * Login form component
 */
import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  FormErrorMessage,
  useToast,
  Heading,
  Text,
  Container
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { loginSchema } from '../../utils/validationSchemas';
import type { z } from 'zod';

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data);
      
      // Redirect to the page they tried to visit or home
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
      
      toast({
        title: 'Welcome back!',
        status: 'success',
        duration: 3000
      });
    } catch (error) {
      toast({
        title: 'Login failed',
        description: error.message || 'Please check your credentials',
        status: 'error',
        duration: 5000
      });
    }
  };

  return (
    <Container maxW="md" py={12}>
      <VStack spacing={8}>
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            Welcome Back
          </Heading>
          <Text color="gray.600">
            Please sign in to continue
          </Text>
        </Box>

        <Box
          as="form"
          onSubmit={handleSubmit(onSubmit)}
          w="100%"
        >
          <VStack spacing={4}>
            <FormControl isInvalid={!!errors.email}>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                {...register('email')}
                autoComplete="email"
              />
              <FormErrorMessage>
                {errors.email?.message}
              </FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.password}>
              <FormLabel>Password</FormLabel>
              <Input
                type="password"
                {...register('password')}
                autoComplete="current-password"
              />
              <FormErrorMessage>
                {errors.password?.message}
              </FormErrorMessage>
            </FormControl>

            <Button
              type="submit"
              colorScheme="blue"
              size="lg"
              width="100%"
              isLoading={isSubmitting}
              loadingText="Signing in..."
            >
              Sign In
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  );
};
