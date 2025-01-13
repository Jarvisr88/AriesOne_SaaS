/**
 * Protected route component for authentication
 */
import React from 'react';
import {
  Navigate,
  useLocation
} from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { LoadingSpinner } from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles = []
}) => {
  const location = useLocation();
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Checking authentication..." />;
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        state={{ from: location }}
        replace
      />
    );
  }

  if (
    requiredRoles.length > 0 &&
    !requiredRoles.some(role => user.roles.includes(role))
  ) {
    return (
      <Navigate
        to="/unauthorized"
        state={{ from: location }}
        replace
      />
    );
  }

  return <>{children}</>;
};
