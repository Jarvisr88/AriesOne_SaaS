"""
Performance Test Module
Version: 1.0.0
Last Updated: 2025-01-10

This module contains performance tests using Locust.
"""
import json
import random
from typing import Dict, Optional
from uuid import UUID

from locust import FastHttpUser, between, task


class AriesOneUser(FastHttpUser):
    """Simulated user for performance testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    tenant_id: Optional[UUID] = None
    access_token: Optional[str] = None
    inventory_items: list[Dict] = []
    
    def on_start(self):
        """Setup before starting tasks."""
        # Register and get access token
        response = self.client.post(
            "/auth/register",
            json={
                "email": f"user_{random.randint(1, 1000000)}@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        if response.status_code != 200:
            raise Exception("Failed to register user")
        
        # Login to get token
        response = self.client.post(
            "/auth/token",
            data={
                "username": response.json()["email"],
                "password": "testpass123"
            }
        )
        
        if response.status_code != 200:
            raise Exception("Failed to get token")
        
        self.access_token = response.json()["access_token"]
        self.client.headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Create tenant
        response = self.client.post(
            "/tenants",
            json={
                "name": f"Test Tenant {random.randint(1, 1000000)}",
                "slug": f"test-tenant-{random.randint(1, 1000000)}",
                "subscription_plan": "premium"
            }
        )
        
        if response.status_code != 200:
            raise Exception("Failed to create tenant")
        
        self.tenant_id = response.json()["id"]
    
    @task(2)
    def view_inventory(self):
        """View inventory items."""
        with self.client.get(
            "/inventory",
            name="/inventory - List Items",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.inventory_items = response.json()
                response.success()
            else:
                response.failure("Failed to list inventory items")
    
    @task(1)
    def create_inventory_item(self):
        """Create new inventory item."""
        with self.client.post(
            "/inventory",
            name="/inventory - Create Item",
            catch_response=True,
            json={
                "name": f"Item {random.randint(1, 1000000)}",
                "description": "Test description",
                "category": "equipment",
                "status": "available",
                "quantity": random.randint(1, 100),
                "unit_price": round(random.uniform(10, 1000), 2),
                "tenant_id": self.tenant_id
            }
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Failed to create inventory item")
    
    @task(1)
    def create_order(self):
        """Create new order."""
        if not self.inventory_items:
            return
        
        # Select random items for order
        order_items = random.sample(
            self.inventory_items,
            min(random.randint(1, 3), len(self.inventory_items))
        )
        
        with self.client.post(
            "/orders",
            name="/orders - Create Order",
            catch_response=True,
            json={
                "customer_name": "Test Customer",
                "customer_email": f"customer_{random.randint(1, 1000000)}@example.com",
                "shipping_address": "123 Test St",
                "billing_address": "123 Test St",
                "status": "pending",
                "tenant_id": self.tenant_id,
                "items": [
                    {
                        "inventory_item_id": item["id"],
                        "quantity": random.randint(1, 5),
                        "unit_price": item["unit_price"],
                        "discount": random.randint(0, 20)
                    }
                    for item in order_items
                ]
            }
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Failed to create order")
    
    @task(2)
    def view_orders(self):
        """View orders."""
        with self.client.get(
            "/orders",
            name="/orders - List Orders",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Failed to list orders")
    
    @task(1)
    def refresh_token(self):
        """Refresh access token."""
        with self.client.post(
            "/auth/refresh",
            name="/auth/refresh - Refresh Token",
            catch_response=True,
            json={"refresh_token": self.access_token}
        ) as response:
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                self.client.headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                response.success()
            else:
                response.failure("Failed to refresh token")
