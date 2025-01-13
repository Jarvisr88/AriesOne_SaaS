"""Load testing configuration for Ability module."""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Optional

from locust import HttpUser, TaskSet, between, task
from locust.clients import ResponseContextManager


class ApplicationWorkflow(TaskSet):
    """Application workflow simulation."""
    
    def on_start(self):
        """Initialize user session."""
        # Login
        response = self.client.post(
            "/auth/login",
            json={
                "email": f"user_{self.user_id}@example.com",
                "password": "test_password"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create test workflow
        response = self.client.post(
            "/workflows",
            json={
                "name": f"Test Workflow {self.user_id}",
                "company_id": self.company_id,
                "steps": [
                    {
                        "name": "Review",
                        "order": 1,
                        "required_role": "reviewer"
                    },
                    {
                        "name": "Approve",
                        "order": 2,
                        "required_role": "approver"
                    }
                ]
            },
            headers=self.headers
        )
        self.workflow_id = response.json()["id"]
    
    def create_application(self) -> ResponseContextManager:
        """Create new application."""
        return self.client.post(
            "/applications",
            json={
                "title": f"Test Application {datetime.utcnow()}",
                "description": "Load test application",
                "workflow_id": self.workflow_id,
                "company_id": self.company_id,
                "metadata": {
                    "priority": random.choice(
                        ["low", "medium", "high"]
                    ),
                    "category": random.choice(
                        ["sales", "support", "billing"]
                    )
                }
            },
            headers=self.headers
        )
    
    @task(3)
    def view_applications(self):
        """View applications list."""
        params = {
            "company_id": self.company_id,
            "page": random.randint(1, 10),
            "page_size": 20
        }
        
        # Randomly add filters
        if random.random() < 0.3:
            params["status"] = random.choice([
                "pending",
                "in_progress",
                "completed"
            ])
        
        if random.random() < 0.2:
            params["created_after"] = (
                datetime.utcnow() - timedelta(days=30)
            ).isoformat()
        
        self.client.get(
            "/applications",
            params=params,
            headers=self.headers
        )
    
    @task(2)
    def search_applications(self):
        """Search applications."""
        self.client.get(
            "/applications/search",
            params={
                "company_id": self.company_id,
                "query": random.choice([
                    "high priority",
                    "sales",
                    "support ticket",
                    "urgent",
                    "review needed"
                ])
            },
            headers=self.headers
        )
    
    @task(1)
    def create_and_process_application(self):
        """Create and process application."""
        # Create application
        response = self.create_application()
        app_id = response.json()["id"]
        
        # Progress through workflow steps
        for step in range(2):  # Two-step workflow
            self.client.post(
                f"/applications/{app_id}/progress",
                json={
                    "action": "approve",
                    "comment": f"Approved step {step + 1}"
                },
                headers=self.headers
            )
    
    @task(1)
    def batch_operations(self):
        """Perform batch operations."""
        # Create multiple applications
        app_ids = []
        for _ in range(5):
            response = self.create_application()
            app_ids.append(response.json()["id"])
        
        # Batch process
        self.client.post(
            "/applications/batch/process",
            json={
                "application_ids": app_ids,
                "action": "approve",
                "comment": "Batch approval"
            },
            headers=self.headers
        )


class ApplicationUser(HttpUser):
    """Simulated application user."""
    tasks = [ApplicationWorkflow]
    wait_time = between(1, 5)
    
    def __init__(self, *args, **kwargs):
        """Initialize user."""
        super().__init__(*args, **kwargs)
        self.user_id = random.randint(1, 1000)
        self.company_id = random.randint(1, 100)


class ReportingUser(HttpUser):
    """Simulated reporting user."""
    wait_time = between(5, 15)
    
    def on_start(self):
        """Initialize user session."""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "reporter@example.com",
                "password": "test_password"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(1)
    def generate_reports(self):
        """Generate various reports."""
        # Application statistics
        self.client.get(
            "/reports/applications/stats",
            params={
                "start_date": (
                    datetime.utcnow() - timedelta(days=30)
                ).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            headers=self.headers
        )
        
        # Workflow analytics
        self.client.get(
            "/reports/workflows/analytics",
            params={
                "company_id": random.randint(1, 100)
            },
            headers=self.headers
        )
        
        # Performance metrics
        self.client.get(
            "/reports/performance",
            headers=self.headers
        )


class AdminUser(HttpUser):
    """Simulated admin user."""
    wait_time = between(10, 30)
    
    def on_start(self):
        """Initialize user session."""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "admin_password"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(1)
    def monitor_system(self):
        """Monitor system health."""
        # System metrics
        self.client.get(
            "/admin/metrics",
            headers=self.headers
        )
        
        # Error logs
        self.client.get(
            "/admin/errors",
            params={
                "severity": random.choice([
                    "warning",
                    "error",
                    "critical"
                ])
            },
            headers=self.headers
        )
        
        # Cache stats
        self.client.get(
            "/admin/cache/stats",
            headers=self.headers
        )
        
        # Database stats
        self.client.get(
            "/admin/database/stats",
            headers=self.headers
        )
