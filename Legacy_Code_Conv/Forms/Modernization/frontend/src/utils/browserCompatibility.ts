/**
 * Browser compatibility utilities.
 * 
 * This module provides utilities for handling browser compatibility.
 */

/**
 * Check if a CSS property is supported.
 */
export const isCSSPropertySupported = (
  property: string,
  value?: string
): boolean => {
  const element = document.createElement('div');
  
  if (value) {
    try {
      element.style[property as any] = value;
      return element.style[property as any] === value;
    } catch {
      return false;
    }
  }
  
  return property in element.style;
};

/**
 * Check if a browser feature is supported.
 */
export const isFeatureSupported = (feature: string): boolean => {
  const features: Record<string, () => boolean> = {
    webp: () => {
      const canvas = document.createElement('canvas');
      if (canvas.getContext && canvas.getContext('2d')) {
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
      }
      return false;
    },
    webgl: () => {
      try {
        const canvas = document.createElement('canvas');
        return !!(
          window.WebGLRenderingContext &&
          (canvas.getContext('webgl') ||
            canvas.getContext('experimental-webgl'))
        );
      } catch {
        return false;
      }
    },
    webworker: () => typeof Worker !== 'undefined',
    websocket: () => typeof WebSocket !== 'undefined',
    webrtc: () =>
      !!(
        navigator.mediaDevices?.getUserMedia ||
        (navigator as any).webkitGetUserMedia ||
        (navigator as any).mozGetUserMedia ||
        (navigator as any).msGetUserMedia
      ),
    indexeddb: () =>
      !!(
        window.indexedDB ||
        (window as any).mozIndexedDB ||
        (window as any).webkitIndexedDB ||
        (window as any).msIndexedDB
      ),
    localstorage: () => {
      try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
        return true;
      } catch {
        return false;
      }
    },
  };
  
  return features[feature]?.() ?? false;
};

/**
 * Get browser information.
 */
export const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  const browserInfo = {
    name: '',
    version: '',
    os: '',
  };
  
  // Browser name and version
  if (ua.includes('Firefox/')) {
    browserInfo.name = 'Firefox';
    browserInfo.version = ua.split('Firefox/')[1];
  } else if (ua.includes('Chrome/')) {
    browserInfo.name = 'Chrome';
    browserInfo.version = ua.split('Chrome/')[1].split(' ')[0];
  } else if (ua.includes('Safari/')) {
    browserInfo.name = 'Safari';
    browserInfo.version = ua.split('Version/')[1]?.split(' ')[0];
  } else if (ua.includes('Edge/')) {
    browserInfo.name = 'Edge';
    browserInfo.version = ua.split('Edge/')[1];
  }
  
  // Operating system
  if (ua.includes('Windows')) {
    browserInfo.os = 'Windows';
  } else if (ua.includes('Mac OS')) {
    browserInfo.os = 'macOS';
  } else if (ua.includes('Linux')) {
    browserInfo.os = 'Linux';
  } else if (ua.includes('Android')) {
    browserInfo.os = 'Android';
  } else if (ua.includes('iOS')) {
    browserInfo.os = 'iOS';
  }
  
  return browserInfo;
};

/**
 * Check if the browser is supported.
 */
export const isBrowserSupported = (): {
  supported: boolean;
  warnings: string[];
} => {
  const warnings: string[] = [];
  const requiredFeatures = [
    'localstorage',
    'indexeddb',
    'webworker',
    'websocket',
  ];
  
  // Check required features
  for (const feature of requiredFeatures) {
    if (!isFeatureSupported(feature)) {
      warnings.push(
        `Browser does not support required feature: ${feature}`
      );
    }
  }
  
  // Check browser version
  const { name, version } = getBrowserInfo();
  const minVersions: Record<string, number> = {
    Chrome: 80,
    Firefox: 75,
    Safari: 13,
    Edge: 80,
  };
  
  const currentVersion = parseFloat(version);
  const minVersion = minVersions[name];
  
  if (minVersion && currentVersion < minVersion) {
    warnings.push(
      `Browser version ${currentVersion} is below minimum required version ${minVersion}`
    );
  }
  
  return {
    supported: warnings.length === 0,
    warnings,
  };
};
