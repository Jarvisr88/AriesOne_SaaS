/**
 * Test setup file.
 */
import '@testing-library/jest-dom';
import 'jest-canvas-mock';


// Mock IntersectionObserver
const mockIntersectionObserver = jest.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
window.IntersectionObserver = mockIntersectionObserver;

// Mock ResizeObserver
const mockResizeObserver = jest.fn();
mockResizeObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
window.ResizeObserver = mockResizeObserver;

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.URL
const mockCreateObjectURL = jest.fn();
Object.defineProperty(window.URL, 'createObjectURL', {
  writable: true,
  value: mockCreateObjectURL,
});

// Mock window.scroll
Object.defineProperty(window, 'scroll', {
  writable: true,
  value: jest.fn(),
});
