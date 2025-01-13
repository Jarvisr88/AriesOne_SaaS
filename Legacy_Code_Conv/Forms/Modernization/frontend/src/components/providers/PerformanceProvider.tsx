/**
 * Performance provider component.
 * 
 * This component provides performance optimizations for the application.
 */
import React from 'react';
import {
  createContext,
  useContext,
  useEffect,
  useCallback,
  useMemo,
} from 'react';


interface PerformanceContextValue {
  measurePerformance: (name: string) => () => void;
  logMetrics: () => void;
}

const PerformanceContext = createContext<PerformanceContextValue>({
  measurePerformance: () => () => {},
  logMetrics: () => {},
});

interface Metric {
  name: string;
  startTime: number;
  endTime?: number;
  duration?: number;
}

interface PerformanceProviderProps {
  children: React.ReactNode;
}

export const PerformanceProvider: React.FC<PerformanceProviderProps> = ({
  children,
}) => {
  const metrics = useMemo(() => new Map<string, Metric[]>(), []);
  
  const measurePerformance = useCallback((name: string) => {
    const metric: Metric = {
      name,
      startTime: performance.now(),
    };
    
    const existingMetrics = metrics.get(name) || [];
    metrics.set(name, [...existingMetrics, metric]);
    
    return () => {
      metric.endTime = performance.now();
      metric.duration = metric.endTime - metric.startTime;
    };
  }, [metrics]);
  
  const logMetrics = useCallback(() => {
    const summary: Record<string, {
      count: number;
      avgDuration: number;
      minDuration: number;
      maxDuration: number;
    }> = {};
    
    metrics.forEach((metricList, name) => {
      const durations = metricList
        .filter((m) => m.duration !== undefined)
        .map((m) => m.duration!);
      
      if (durations.length > 0) {
        summary[name] = {
          count: durations.length,
          avgDuration:
            durations.reduce((a, b) => a + b, 0) / durations.length,
          minDuration: Math.min(...durations),
          maxDuration: Math.max(...durations),
        };
      }
    });
    
    console.table(summary);
  }, [metrics]);
  
  // Monitor long tasks
  useEffect(() => {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.duration > 50) {
            console.warn(
              'Long task detected:',
              entry.name,
              'Duration:',
              entry.duration.toFixed(2),
              'ms'
            );
          }
        });
      });
      
      observer.observe({ entryTypes: ['longtask'] });
      return () => observer.disconnect();
    }
  }, []);
  
  // Monitor layout shifts
  useEffect(() => {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry: any) => {
          if (entry.value > 0.1) {
            console.warn(
              'Large layout shift detected:',
              'Score:',
              entry.value.toFixed(3),
              'Source:',
              entry.sources?.[0]?.node?.nodeName
            );
          }
        });
      });
      
      observer.observe({ entryTypes: ['layout-shift'] });
      return () => observer.disconnect();
    }
  }, []);
  
  // Monitor first paint and contentful paint
  useEffect(() => {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          console.log(
            `${entry.name}:`,
            entry.startTime.toFixed(2),
            'ms'
          );
        });
      });
      
      observer.observe({
        entryTypes: ['paint'],
      });
      
      return () => observer.disconnect();
    }
  }, []);
  
  const value = useMemo(
    () => ({
      measurePerformance,
      logMetrics,
    }),
    [measurePerformance, logMetrics]
  );
  
  return (
    <PerformanceContext.Provider value={value}>
      {children}
    </PerformanceContext.Provider>
  );
};

export const usePerformance = () => {
  const context = useContext(PerformanceContext);
  
  if (!context) {
    throw new Error(
      'usePerformance must be used within a PerformanceProvider'
    );
  }
  
  return context;
};
