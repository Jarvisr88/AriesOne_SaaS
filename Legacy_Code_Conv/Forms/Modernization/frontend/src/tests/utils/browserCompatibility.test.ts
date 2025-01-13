/**
 * Browser compatibility utilities tests.
 */
import {
  isCSSPropertySupported,
  isFeatureSupported,
  getBrowserInfo,
  isBrowserSupported,
} from '../../utils/browserCompatibility';


describe('browserCompatibility', () => {
  describe('isCSSPropertySupported', () => {
    it('detects supported CSS properties', () => {
      expect(isCSSPropertySupported('color')).toBe(true);
      expect(isCSSPropertySupported('display')).toBe(true);
    });
    
    it('detects unsupported CSS properties', () => {
      expect(isCSSPropertySupported('nonexistent')).toBe(false);
    });
    
    it('validates property values', () => {
      expect(isCSSPropertySupported('display', 'flex')).toBe(true);
      expect(isCSSPropertySupported('display', 'invalid')).toBe(false);
    });
  });
  
  describe('isFeatureSupported', () => {
    beforeEach(() => {
      // Mock browser features
      Object.defineProperty(window, 'WebSocket', {
        value: class WebSocket {},
      });
      
      Object.defineProperty(window, 'Worker', {
        value: class Worker {},
      });
      
      Object.defineProperty(window, 'localStorage', {
        value: {
          setItem: jest.fn(),
          removeItem: jest.fn(),
        },
      });
    });
    
    it('detects supported features', () => {
      expect(isFeatureSupported('websocket')).toBe(true);
      expect(isFeatureSupported('webworker')).toBe(true);
      expect(isFeatureSupported('localstorage')).toBe(true);
    });
    
    it('detects unsupported features', () => {
      expect(isFeatureSupported('nonexistent')).toBe(false);
    });
  });
  
  describe('getBrowserInfo', () => {
    beforeEach(() => {
      // Mock user agent
      Object.defineProperty(window.navigator, 'userAgent', {
        value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        configurable: true,
      });
    });
    
    it('extracts browser information correctly', () => {
      const info = getBrowserInfo();
      
      expect(info.name).toBe('Chrome');
      expect(info.version).toBe('91.0.4472.124');
      expect(info.os).toBe('Windows');
    });
  });
  
  describe('isBrowserSupported', () => {
    it('validates browser support requirements', () => {
      // Mock supported environment
      Object.defineProperty(window, 'WebSocket', {
        value: class WebSocket {},
      });
      Object.defineProperty(window, 'Worker', {
        value: class Worker {},
      });
      Object.defineProperty(window, 'localStorage', {
        value: {
          setItem: jest.fn(),
          removeItem: jest.fn(),
        },
      });
      Object.defineProperty(window, 'indexedDB', {
        value: {},
      });
      
      const { supported, warnings } = isBrowserSupported();
      
      expect(supported).toBe(true);
      expect(warnings).toHaveLength(0);
    });
    
    it('detects missing features', () => {
      // Mock unsupported environment
      Object.defineProperty(window, 'WebSocket', {
        value: undefined,
      });
      Object.defineProperty(window, 'Worker', {
        value: undefined,
      });
      
      const { supported, warnings } = isBrowserSupported();
      
      expect(supported).toBe(false);
      expect(warnings.length).toBeGreaterThan(0);
      expect(warnings).toContain(
        expect.stringContaining('websocket')
      );
      expect(warnings).toContain(
        expect.stringContaining('webworker')
      );
    });
  });
});
