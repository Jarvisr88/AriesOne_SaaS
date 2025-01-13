/**
 * MSW request handlers for API mocking
 */
import { rest } from 'msw';

const API_URL = process.env.REACT_APP_API_URL || '';

export const handlers = [
  // Auth endpoints
  rest.post(`${API_URL}/auth/login`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        user: {
          id: 1,
          email: 'test@example.com',
          name: 'Test User',
          roles: ['user']
        },
        token: 'mock-jwt-token'
      })
    );
  }),

  rest.get(`${API_URL}/auth/me`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        roles: ['user']
      })
    );
  }),

  // Deposits endpoints
  rest.get(`${API_URL}/deposits`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          amount: 100.00,
          paymentMethod: 'cash',
          customerId: 1,
          status: 'completed',
          createdAt: new Date().toISOString()
        }
      ])
    );
  }),

  rest.post(`${API_URL}/deposits`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 2,
        ...req.body,
        status: 'pending',
        createdAt: new Date().toISOString()
      })
    );
  }),

  // Voids endpoints
  rest.get(`${API_URL}/voids`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          amount: 50.00,
          reason: 'Test void',
          status: 'pending',
          createdAt: new Date().toISOString()
        }
      ])
    );
  }),

  rest.post(`${API_URL}/voids`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 2,
        ...req.body,
        status: 'pending',
        createdAt: new Date().toISOString()
      })
    );
  }),

  // Purchase Orders endpoints
  rest.get(`${API_URL}/purchase-orders`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          vendorId: 1,
          items: [
            {
              name: 'Test Item',
              quantity: 1,
              price: 10.00
            }
          ],
          status: 'draft',
          total: 10.00,
          createdAt: new Date().toISOString()
        }
      ])
    );
  }),

  rest.post(`${API_URL}/purchase-orders`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 2,
        ...req.body,
        status: 'draft',
        createdAt: new Date().toISOString()
      })
    );
  })
];
