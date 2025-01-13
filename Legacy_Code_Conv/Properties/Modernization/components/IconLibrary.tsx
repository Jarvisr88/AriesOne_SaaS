import React from 'react';
import { cn } from '@/lib/utils';

export interface IconProps extends React.SVGProps<SVGSVGElement> {
  size?: number | string;
  className?: string;
}

export const CheckedIcon: React.FC<IconProps> = ({ size = 24, className, ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn('text-primary', className)}
    {...props}
  >
    <path
      d="M20 6L9 17L4 12"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const UncheckedIcon: React.FC<IconProps> = ({ size = 24, className, ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn('text-muted', className)}
    {...props}
  >
    <rect
      x="4"
      y="4"
      width="16"
      height="16"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
    />
  </svg>
);

export const IndeterminateIcon: React.FC<IconProps> = ({ size = 24, className, ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn('text-primary', className)}
    {...props}
  >
    <rect
      x="4"
      y="4"
      width="16"
      height="16"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
    />
    <path
      d="M8 12H16"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

export const ReloadIcon: React.FC<IconProps> = ({ size = 24, className, ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn('text-primary', className)}
    {...props}
  >
    <path
      d="M4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M12 8L8 4L12 0"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const Reload2Icon: React.FC<IconProps> = ({ size = 24, className, ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className={cn('text-primary', className)}
    {...props}
  >
    <path
      d="M20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M12 16L16 20L12 24"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
