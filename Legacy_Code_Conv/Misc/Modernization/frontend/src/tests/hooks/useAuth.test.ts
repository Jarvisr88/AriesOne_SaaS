/**
 * Authentication hook tests
 */
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../../hooks/useAuth';
import { server } from '../mocks/server';
import { rest } from 'msw';

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('initializes with no user', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
  });

  it('logs in successfully', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    expect(result.current.user).toEqual({
      id: 1,
      email: 'test@example.com',
      name: 'Test User',
      roles: ['user']
    });
    expect(result.current.token).toBeTruthy();
    expect(result.current.isAuthenticated).toBeTruthy();
    expect(localStorage.getItem('token')).toBeTruthy();
  });

  it('handles login failure', async () => {
    server.use(
      rest.post('/auth/login', (req, res, ctx) =>
        res(ctx.status(401), ctx.json({ message: 'Invalid credentials' }))
      )
    );

    const { result } = renderHook(() => useAuth());

    try {
      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'wrongpassword'
        });
      });
    } catch (error) {
      expect(error.message).toBe('Invalid credentials');
    }

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('logs out successfully', async () => {
    const { result } = renderHook(() => useAuth());

    // First login
    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    // Then logout
    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBeFalsy();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('checks role permissions correctly', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password123'
      });
    });

    expect(result.current.hasRoles(['user'])).toBeTruthy();
    expect(result.current.hasRoles(['admin'])).toBeFalsy();
  });
});
