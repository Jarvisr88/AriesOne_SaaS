"""Integration tests for Ability module."""
import asyncio
import pytest
from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ....Core.Modernization.models.user import User
from ..models.ability_models import (
    ApplicationCreate,
    ApplicationStatus,
    ApplicationResponse,
    WorkflowCreate,
    WorkflowStatus,
    WorkflowResponse
)
from ..services.application_service import ApplicationService
from ..services.workflow_service import WorkflowService


@pytest.fixture
async def test_app(db: AsyncSession) -> FastAPI:
    """Create test application."""
    from fastapi import FastAPI
    from ..api.ability_api import router
    
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    """Create test client."""
    async with AsyncClient(
        app=test_app,
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password="test_hash",
        is_active=True,
        company_id=1
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_application(
    db: AsyncSession,
    test_user: User
) -> Dict:
    """Create test application data."""
    return {
        "title": "Test Application",
        "description": "Test application description",
        "workflow_id": 1,
        "company_id": test_user.company_id,
        "metadata": {
            "priority": "high",
            "category": "test"
        }
    }


@pytest.fixture
async def test_workflow(
    db: AsyncSession,
    test_user: User
) -> Dict:
    """Create test workflow data."""
    return {
        "name": "Test Workflow",
        "description": "Test workflow description",
        "company_id": test_user.company_id,
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
    }


@pytest.mark.asyncio
async def test_create_application_workflow(
    test_client: AsyncClient,
    test_user: User,
    test_application: Dict,
    test_workflow: Dict
):
    """Test creating application with workflow."""
    # Create workflow
    response = await test_client.post(
        "/workflows",
        json=test_workflow,
        headers={"user-id": str(test_user.id)}
    )
    assert response.status_code == 201
    workflow_data = response.json()
    assert workflow_data["name"] == test_workflow["name"]
    assert workflow_data["status"] == WorkflowStatus.ACTIVE
    
    # Update application with workflow ID
    test_application["workflow_id"] = workflow_data["id"]
    
    # Create application
    response = await test_client.post(
        "/applications",
        json=test_application,
        headers={"user-id": str(test_user.id)}
    )
    assert response.status_code == 201
    app_data = response.json()
    assert app_data["title"] == test_application["title"]
    assert app_data["status"] == ApplicationStatus.PENDING
    
    # Get application with workflow
    response = await test_client.get(
        f"/applications/{app_data['id']}",
        headers={"user-id": str(test_user.id)}
    )
    assert response.status_code == 200
    app_data = response.json()
    assert app_data["workflow"]["id"] == workflow_data["id"]


@pytest.mark.asyncio
async def test_application_workflow_progression(
    test_client: AsyncClient,
    test_user: User,
    test_application: Dict,
    test_workflow: Dict
):
    """Test application workflow progression."""
    # Create workflow
    response = await test_client.post(
        "/workflows",
        json=test_workflow,
        headers={"user-id": str(test_user.id)}
    )
    workflow_data = response.json()
    test_application["workflow_id"] = workflow_data["id"]
    
    # Create application
    response = await test_client.post(
        "/applications",
        json=test_application,
        headers={"user-id": str(test_user.id)}
    )
    app_data = response.json()
    
    # Progress through workflow steps
    for step in workflow_data["steps"]:
        response = await test_client.post(
            f"/applications/{app_data['id']}/progress",
            json={
                "step_id": step["id"],
                "action": "approve",
                "comment": f"Approved step {step['name']}"
            },
            headers={"user-id": str(test_user.id)}
        )
        assert response.status_code == 200
        app_data = response.json()
        assert app_data["current_step"]["name"] == step["name"]
    
    # Verify application completed
    assert app_data["status"] == ApplicationStatus.COMPLETED


@pytest.mark.asyncio
async def test_batch_application_processing(
    test_client: AsyncClient,
    test_user: User,
    test_application: Dict,
    test_workflow: Dict
):
    """Test batch application processing."""
    # Create workflow
    response = await test_client.post(
        "/workflows",
        json=test_workflow,
        headers={"user-id": str(test_user.id)}
    )
    workflow_data = response.json()
    
    # Create multiple applications
    app_ids = []
    for i in range(5):
        app = test_application.copy()
        app["title"] = f"Test Application {i}"
        app["workflow_id"] = workflow_data["id"]
        response = await test_client.post(
            "/applications",
            json=app,
            headers={"user-id": str(test_user.id)}
        )
        app_data = response.json()
        app_ids.append(app_data["id"])
    
    # Batch process applications
    response = await test_client.post(
        "/applications/batch/process",
        json={
            "application_ids": app_ids,
            "action": "approve",
            "comment": "Batch approval"
        },
        headers={"user-id": str(test_user.id)}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result["processed"]) == 5
    assert all(
        app["status"] == ApplicationStatus.IN_PROGRESS
        for app in result["processed"]
    )


@pytest.mark.asyncio
async def test_application_rate_limiting(
    test_client: AsyncClient,
    test_user: User,
    test_application: Dict
):
    """Test application rate limiting."""
    # Create multiple applications rapidly
    responses = await asyncio.gather(*[
        test_client.post(
            "/applications",
            json=test_application,
            headers={"user-id": str(test_user.id)}
        )
        for _ in range(10)
    ])
    
    # Check if rate limiting was applied
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes  # Too Many Requests


@pytest.mark.asyncio
async def test_application_caching(
    test_client: AsyncClient,
    test_user: User,
    test_application: Dict,
    test_workflow: Dict
):
    """Test application caching."""
    # Create workflow and application
    response = await test_client.post(
        "/workflows",
        json=test_workflow,
        headers={"user-id": str(test_user.id)}
    )
    workflow_data = response.json()
    test_application["workflow_id"] = workflow_data["id"]
    
    response = await test_client.post(
        "/applications",
        json=test_application,
        headers={"user-id": str(test_user.id)}
    )
    app_data = response.json()
    
    # First request - should hit database
    start = datetime.now()
    response = await test_client.get(
        f"/applications/{app_data['id']}",
        headers={"user-id": str(test_user.id)}
    )
    first_duration = datetime.now() - start
    
    # Second request - should hit cache
    start = datetime.now()
    response = await test_client.get(
        f"/applications/{app_data['id']}",
        headers={"user-id": str(test_user.id)}
    )
    second_duration = datetime.now() - start
    
    # Cache should be faster
    assert second_duration < first_duration


@pytest.mark.asyncio
async def test_application_error_tracking(
    test_client: AsyncClient,
    test_user: User,
    test_application: Dict
):
    """Test application error tracking."""
    # Attempt to create application with invalid data
    invalid_app = test_application.copy()
    invalid_app["workflow_id"] = 999999  # Non-existent workflow
    
    response = await test_client.post(
        "/applications",
        json=invalid_app,
        headers={"user-id": str(test_user.id)}
    )
    assert response.status_code == 404
    error_data = response.json()
    assert "error_id" in error_data
    
    # Verify error was logged
    response = await test_client.get(
        f"/errors/{error_data['error_id']}",
        headers={"user-id": str(test_user.id)}
    )
    assert response.status_code == 200
    error_log = response.json()
    assert error_log["type"] == "WorkflowNotFound"
    assert error_log["status_code"] == 404
