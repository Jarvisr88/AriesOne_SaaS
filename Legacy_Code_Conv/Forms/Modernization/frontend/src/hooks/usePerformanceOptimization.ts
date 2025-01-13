/**
 * Performance optimization hooks.
 * 
 * This module provides hooks for optimizing component performance.
 */
import { useCallback, useEffect, useRef } from 'react';
import { useIntersectionObserver } from '@chakra-ui/react';


/**
 * Hook for lazy loading images when they enter the viewport.
 */
export const useLazyImage = (
  src: string,
  options?: IntersectionObserverInit
) => {
  const [ref, entry] = useIntersectionObserver(options);
  const imgRef = useRef<HTMLImageElement | null>(null);
  
  useEffect(() => {
    if (entry?.isIntersecting && imgRef.current) {
      imgRef.current.src = src;
    }
  }, [entry, src]);
  
  return { ref, imgRef };
};

/**
 * Hook for debouncing a function call.
 */
export const useDebounce = <T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): T => {
  const timeoutRef = useRef<NodeJS.Timeout>();
  
  return useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        fn(...args);
      }, delay);
    },
    [fn, delay]
  ) as T;
};

/**
 * Hook for throttling a function call.
 */
export const useThrottle = <T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): T => {
  const lastRunRef = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout>();
  
  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      
      if (now - lastRunRef.current >= limit) {
        fn(...args);
        lastRunRef.current = now;
      } else if (!timeoutRef.current) {
        timeoutRef.current = setTimeout(() => {
          fn(...args);
          lastRunRef.current = Date.now();
          timeoutRef.current = undefined;
        }, limit - (now - lastRunRef.current));
      }
    },
    [fn, limit]
  ) as T;
};

/**
 * Hook for memoizing expensive computations.
 */
export const useMemoizedValue = <T>(
  getValue: () => T,
  deps: any[]
): T => {
  const ref = useRef<{ value: T; deps: any[] }>({
    value: getValue(),
    deps,
  });
  
  const depsChanged = deps.some(
    (dep, i) => dep !== ref.current.deps[i]
  );
  
  if (depsChanged) {
    ref.current = {
      value: getValue(),
      deps,
    };
  }
  
  return ref.current.value;
};
