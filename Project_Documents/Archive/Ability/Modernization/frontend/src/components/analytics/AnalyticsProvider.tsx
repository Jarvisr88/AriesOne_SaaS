import React, { createContext, useContext, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import mixpanel from 'mixpanel-browser';
import posthog from 'posthog-js';
import { useAuth } from '../auth/AuthContext';

interface AnalyticsContextType {
  trackEvent: (eventName: string, properties?: Record<string, any>) => void;
  trackPageView: (pageName: string, properties?: Record<string, any>) => void;
  identifyUser: (userId: string, traits?: Record<string, any>) => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

interface AnalyticsProviderProps {
  children: React.ReactNode;
  mixpanelToken?: string;
  posthogToken?: string;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({
  children,
  mixpanelToken,
  posthogToken,
}) => {
  const location = useLocation();
  const { user } = useAuth();

  useEffect(() => {
    // Initialize analytics services
    if (mixpanelToken) {
      mixpanel.init(mixpanelToken);
    }
    if (posthogToken) {
      posthog.init(posthogToken, {
        api_host: 'https://app.posthog.com',
      });
    }
  }, [mixpanelToken, posthogToken]);

  useEffect(() => {
    // Track page views
    const pageName = location.pathname;
    trackPageView(pageName);
  }, [location]);

  const trackEvent = (eventName: string, properties?: Record<string, any>) => {
    try {
      // Track in Mixpanel
      if (mixpanelToken) {
        mixpanel.track(eventName, {
          ...properties,
          timestamp: new Date().toISOString(),
        });
      }

      // Track in PostHog
      if (posthogToken) {
        posthog.capture(eventName, {
          ...properties,
          timestamp: new Date().toISOString(),
        });
      }

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Analytics Event:', {
          eventName,
          properties,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Analytics tracking error:', error);
    }
  };

  const trackPageView = (pageName: string, properties?: Record<string, any>) => {
    try {
      // Track in Mixpanel
      if (mixpanelToken) {
        mixpanel.track('Page View', {
          page: pageName,
          ...properties,
          timestamp: new Date().toISOString(),
        });
      }

      // Track in PostHog
      if (posthogToken) {
        posthog.capture('$pageview', {
          page: pageName,
          ...properties,
          timestamp: new Date().toISOString(),
        });
      }

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Page View:', {
          page: pageName,
          properties,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Page view tracking error:', error);
    }
  };

  const identifyUser = (userId: string, traits?: Record<string, any>) => {
    try {
      // Identify in Mixpanel
      if (mixpanelToken) {
        mixpanel.identify(userId);
        if (traits) {
          mixpanel.people.set(traits);
        }
      }

      // Identify in PostHog
      if (posthogToken) {
        posthog.identify(userId, traits);
      }

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log('User Identified:', {
          userId,
          traits,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('User identification error:', error);
    }
  };

  useEffect(() => {
    // Identify user when they log in
    if (user?.id) {
      identifyUser(user.id, {
        email: user.email,
        name: user.name,
        role: user.role,
        lastLogin: new Date().toISOString(),
      });
    }
  }, [user]);

  return (
    <AnalyticsContext.Provider value={{ trackEvent, trackPageView, identifyUser }}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};
