import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.core.config import settings
from app.models.ability import Ability, AbilityStatus
from app.models.user import User
from app.models.company import Company
from app.models.order import Order
from app.services.ability_service import AbilityService
from app.services.rate_limiter import RateLimiter
from app.services.cache_manager import CacheManager

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def db_session():
    from app.db.session import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_company(db_session: Session):
    company = Company(
        name="Test Company",
        status="active",
        subscription_tier="enterprise"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_user(db_session: Session, test_company: Company):
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        company_id=test_company.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_ability(db_session: Session, test_company: Company):
    ability = Ability(
        name="Test Ability",
        company_id=test_company.id,
        status=AbilityStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db_session.add(ability)
    db_session.commit()
    db_session.refresh(ability)
    return ability

@pytest.fixture
def auth_headers(test_user: User):
    from app.core.security import create_access_token
    access_token = create_access_token(
        data={"sub": str(test_user.id)}
    )
    return {"Authorization": f"Bearer {access_token}"}

class TestAbilityWorkflow:
    def test_create_ability(self, test_client: TestClient, auth_headers: dict):
        response = test_client.post(
            "/api/v1/abilities/",
            headers=auth_headers,
            json={
                "name": "New Ability",
                "description": "Test description",
                "status": "active"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Ability"
        assert data["status"] == "active"

    def test_get_ability(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        response = test_client.get(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_ability.id
        assert data["name"] == test_ability.name

    def test_update_ability(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        response = test_client.put(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers,
            json={
                "name": "Updated Ability",
                "status": "inactive"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Ability"
        assert data["status"] == "inactive"

    def test_delete_ability(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        response = test_client.delete(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers
        )
        assert response.status_code == 204

    def test_list_abilities(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        response = test_client.get(
            "/api/v1/abilities/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(ability["id"] == test_ability.id for ability in data)

class TestBatchProcessing:
    def test_bulk_create_abilities(self, test_client: TestClient, auth_headers: dict):
        abilities = [
            {"name": f"Bulk Ability {i}", "status": "active"}
            for i in range(5)
        ]
        response = test_client.post(
            "/api/v1/abilities/bulk",
            headers=auth_headers,
            json=abilities
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 5

    def test_bulk_update_abilities(self, test_client: TestClient, auth_headers: dict):
        # First create abilities
        abilities = [
            {"name": f"Bulk Ability {i}", "status": "active"}
            for i in range(3)
        ]
        create_response = test_client.post(
            "/api/v1/abilities/bulk",
            headers=auth_headers,
            json=abilities
        )
        created_abilities = create_response.json()
        
        # Update them
        updates = [
            {
                "id": ability["id"],
                "status": "inactive"
            }
            for ability in created_abilities
        ]
        response = test_client.put(
            "/api/v1/abilities/bulk",
            headers=auth_headers,
            json=updates
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(ability["status"] == "inactive" for ability in data)

class TestRateLimiting:
    def test_rate_limit_exceeded(self, test_client: TestClient, auth_headers: dict):
        # Make requests up to the limit
        for _ in range(settings.RATE_LIMIT_PER_MINUTE):
            response = test_client.get(
                "/api/v1/abilities/",
                headers=auth_headers
            )
            assert response.status_code == 200

        # Next request should be rate limited
        response = test_client.get(
            "/api/v1/abilities/",
            headers=auth_headers
        )
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_rate_limit_recovery(self, test_client: TestClient, auth_headers: dict):
        # Make requests up to the limit
        for _ in range(settings.RATE_LIMIT_PER_MINUTE):
            test_client.get("/api/v1/abilities/", headers=auth_headers)

        # Wait for rate limit window to reset
        import time
        time.sleep(60)

        # Should be able to make requests again
        response = test_client.get(
            "/api/v1/abilities/",
            headers=auth_headers
        )
        assert response.status_code == 200

class TestCaching:
    def test_cache_hit(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        # First request should cache
        response1 = test_client.get(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers
        )
        assert response1.status_code == 200
        assert "X-Cache" not in response1.headers

        # Second request should hit cache
        response2 = test_client.get(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers
        )
        assert response2.status_code == 200
        assert response2.headers.get("X-Cache") == "HIT"

    def test_cache_invalidation(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        # Get ability to cache it
        test_client.get(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers
        )

        # Update ability
        test_client.put(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )

        # Next get should be a cache miss
        response = test_client.get(
            f"/api/v1/abilities/{test_ability.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "X-Cache" not in response.headers

class TestErrorHandling:
    def test_not_found_error(self, test_client: TestClient, auth_headers: dict):
        response = test_client.get(
            "/api/v1/abilities/999999",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_validation_error(self, test_client: TestClient, auth_headers: dict):
        response = test_client.post(
            "/api/v1/abilities/",
            headers=auth_headers,
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422
        assert "validation error" in response.json()["detail"].lower()

    def test_unauthorized_access(self, test_client: TestClient):
        response = test_client.get("/api/v1/abilities/")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_forbidden_access(self, test_client: TestClient, auth_headers: dict, test_ability: Ability):
        # Create ability for different company
        other_company = Company(name="Other Company", status="active")
        other_ability = Ability(
            name="Other Ability",
            company_id=other_company.id,
            status=AbilityStatus.ACTIVE
        )
        
        response = test_client.get(
            f"/api/v1/abilities/{other_ability.id}",
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "forbidden" in response.json()["detail"].lower()

if __name__ == "__main__":
    pytest.main([__file__])
