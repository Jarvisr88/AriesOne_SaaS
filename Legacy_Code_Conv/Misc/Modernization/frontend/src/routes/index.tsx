/**
 * Application routing configuration
 */
import React from 'react';
import {
  createBrowserRouter,
  RouterProvider,
  Navigate
} from 'react-router-dom';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { ProtectedRoute } from '../components/common/ProtectedRoute';
import { Layout } from '../components/layout/Layout';

// Deposits
import { DepositList } from '../components/deposits/DepositList';
import { DepositForm } from '../components/deposits/DepositForm';
import { DepositDetail } from '../components/deposits/DepositDetail';

// Voids
import { VoidList } from '../components/voids/VoidList';
import { VoidForm } from '../components/voids/VoidForm';
import { VoidDetail } from '../components/voids/VoidDetail';

// Purchase Orders
import { PurchaseOrderList } from '../components/purchase-orders/PurchaseOrderList';
import { PurchaseOrderForm } from '../components/purchase-orders/PurchaseOrderForm';
import { PurchaseOrderDetail } from '../components/purchase-orders/PurchaseOrderDetail';

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ErrorBoundary>
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      </ErrorBoundary>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/deposits" replace />
      },
      // Deposits routes
      {
        path: 'deposits',
        children: [
          {
            index: true,
            element: <DepositList />
          },
          {
            path: 'new',
            element: <DepositForm />
          },
          {
            path: ':id',
            element: <DepositDetail />
          },
          {
            path: ':id/edit',
            element: <DepositForm />
          }
        ]
      },
      // Voids routes
      {
        path: 'voids',
        children: [
          {
            index: true,
            element: <VoidList />
          },
          {
            path: 'new',
            element: <VoidForm />
          },
          {
            path: ':id',
            element: <VoidDetail />
          },
          {
            path: ':id/edit',
            element: <VoidForm />
          }
        ]
      },
      // Purchase Orders routes
      {
        path: 'purchase-orders',
        children: [
          {
            index: true,
            element: <PurchaseOrderList />
          },
          {
            path: 'new',
            element: <PurchaseOrderForm />
          },
          {
            path: ':id',
            element: <PurchaseOrderDetail />
          },
          {
            path: ':id/edit',
            element: <PurchaseOrderForm />
          },
          {
            path: ':id/receive',
            element: (
              <ProtectedRoute requiredRoles={['inventory_manager']}>
                <PurchaseOrderDetail />
              </ProtectedRoute>
            )
          }
        ]
      }
    ]
  }
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};
