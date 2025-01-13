/**
 * Breadcrumbs navigation component
 */
import React from 'react';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Text
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { ChevronRightIcon } from '@chakra-ui/icons';

const routeMap: Record<string, string> = {
  'deposits': 'Deposits',
  'voids': 'Voids',
  'purchase-orders': 'Purchase Orders',
  'new': 'New',
  'edit': 'Edit',
  'receive': 'Receive Items'
};

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathSegments = location.pathname
    .split('/')
    .filter(segment => segment);

  const breadcrumbs = pathSegments.map((segment, index) => {
    const url = `/${pathSegments.slice(0, index + 1).join('/')}`;
    const isNumber = !isNaN(Number(segment));
    const label = isNumber
      ? `#${segment}`
      : (routeMap[segment] || segment);
    const isLast = index === pathSegments.length - 1;

    return (
      <BreadcrumbItem
        key={url}
        isCurrentPage={isLast}
      >
        {isLast ? (
          <Text color="gray.600">
            {label}
          </Text>
        ) : (
          <BreadcrumbLink
            as={RouterLink}
            to={url}
            color="blue.500"
          >
            {label}
          </BreadcrumbLink>
        )}
      </BreadcrumbItem>
    );
  });

  return (
    <Breadcrumb
      spacing="8px"
      separator={<ChevronRightIcon color="gray.500" />}
      mb={4}
    >
      <BreadcrumbItem>
        <BreadcrumbLink
          as={RouterLink}
          to="/"
          color="blue.500"
        >
          Home
        </BreadcrumbLink>
      </BreadcrumbItem>
      {breadcrumbs}
    </Breadcrumb>
  );
};
