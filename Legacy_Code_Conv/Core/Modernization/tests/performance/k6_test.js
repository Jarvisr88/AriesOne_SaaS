/**
 * K6 Performance Tests
 * Version: 1.0.0
 * Last Updated: 2025-01-10
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // 95% of requests must complete below 500ms
    'http_req_failed': ['rate<0.01'],    // Less than 1% of requests can fail
  },
};

const BASE_URL = 'http://localhost:8000';

// Utility function to generate random data
function generateRandomData() {
  return {
    email: `user_${randomString(10)}@example.com`,
    password: 'testpass123',
    firstName: `Test_${randomString(5)}`,
    lastName: `User_${randomString(5)}`,
    tenantName: `Tenant_${randomString(8)}`,
    tenantSlug: `tenant-${randomString(8)}`.toLowerCase(),
  };
}

// Main test scenario
export default function() {
  const data = generateRandomData();
  let token, tenantId, itemId;

  // Register user
  let registerRes = http.post(`${BASE_URL}/auth/register`, JSON.stringify({
    email: data.email,
    password: data.password,
    first_name: data.firstName,
    last_name: data.lastName,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(registerRes, {
    'register successful': (r) => r.status === 200,
  });

  // Login
  let loginRes = http.post(`${BASE_URL}/auth/token`, {
    username: data.email,
    password: data.password,
  });

  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  token = loginRes.json('access_token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  // Create tenant
  let tenantRes = http.post(`${BASE_URL}/tenants`, JSON.stringify({
    name: data.tenantName,
    slug: data.tenantSlug,
    subscription_plan: 'premium',
  }), { headers });

  check(tenantRes, {
    'tenant creation successful': (r) => r.status === 200,
  });

  tenantId = tenantRes.json('id');

  // Create inventory items
  for (let i = 0; i < 3; i++) {
    let itemRes = http.post(`${BASE_URL}/inventory`, JSON.stringify({
      name: `Item_${randomString(8)}`,
      description: `Description_${randomString(15)}`,
      category: 'equipment',
      status: 'available',
      quantity: randomIntBetween(1, 100),
      unit_price: randomIntBetween(10, 1000),
      tenant_id: tenantId,
    }), { headers });

    check(itemRes, {
      'inventory creation successful': (r) => r.status === 200,
    });

    if (i === 0) {
      itemId = itemRes.json('id');
    }
  }

  // List inventory
  let listInventoryRes = http.get(`${BASE_URL}/inventory`, { headers });

  check(listInventoryRes, {
    'inventory list successful': (r) => r.status === 200,
  });

  // Create order
  let orderRes = http.post(`${BASE_URL}/orders`, JSON.stringify({
    customer_name: `Customer_${randomString(8)}`,
    customer_email: `customer_${randomString(8)}@example.com`,
    shipping_address: `Address_${randomString(15)}`,
    billing_address: `Address_${randomString(15)}`,
    status: 'pending',
    tenant_id: tenantId,
    items: [{
      inventory_item_id: itemId,
      quantity: randomIntBetween(1, 5),
      unit_price: randomIntBetween(10, 1000),
      discount: randomIntBetween(0, 20),
    }],
  }), { headers });

  check(orderRes, {
    'order creation successful': (r) => r.status === 200,
  });

  // List orders
  let listOrdersRes = http.get(`${BASE_URL}/orders`, { headers });

  check(listOrdersRes, {
    'order list successful': (r) => r.status === 200,
  });

  // Refresh token
  let refreshRes = http.post(`${BASE_URL}/auth/refresh`, JSON.stringify({
    refresh_token: token,
  }), { headers });

  check(refreshRes, {
    'token refresh successful': (r) => r.status === 200,
  });

  sleep(1);
}
