import React, { useEffect, useState } from 'react';
import { useIconContext } from './IconProvider';
import { loadIcon } from '../utils/assetLoader';
import { cn } from '@/lib/utils';

interface LazyIconProps extends React.SVGProps<SVGSVGElement> {
  name: string;
  size?: number | string;
  className?: string;
  fallback?: React.ReactNode;
}

export const LazyIcon: React.FC<LazyIconProps> = ({
  name,
  size = 24,
  className,
  fallback = null,
  ...props
}) => {
  const { baseUrl, isDark } = useIconContext();
  const [iconContent, setIconContent] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadIconContent = async () => {
      try {
        const content = await loadIcon(name, isDark ? 'dark' : 'light', baseUrl);
        if (mounted) {
          setIconContent(content);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
          console.error(`Failed to load icon: ${name}`, err);
        }
      }
    };

    loadIconContent();

    return () => {
      mounted = false;
    };
  }, [name, isDark, baseUrl]);

  if (error) {
    return fallback as React.ReactElement || null;
  }

  if (!iconContent) {
    return (
      <div
        style={{ width: size, height: size }}
        className={cn('animate-pulse bg-muted rounded', className)}
        {...props}
      />
    );
  }

  // Parse SVG content and apply props
  const parser = new DOMParser();
  const doc = parser.parseFromString(iconContent, 'image/svg+xml');
  const svg = doc.querySelector('svg');

  if (!svg) {
    return fallback as React.ReactElement || null;
  }

  // Apply size and other props
  svg.setAttribute('width', size.toString());
  svg.setAttribute('height', size.toString());
  svg.setAttribute('class', cn(svg.getAttribute('class'), className));

  // Convert SVG to string with applied props
  const serializer = new XMLSerializer();
  const svgString = serializer.serializeToString(svg);

  return (
    <div
      dangerouslySetInnerHTML={{ __html: svgString }}
      style={{ width: size, height: size }}
      {...props}
    />
  );
};
