import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from super_admin_service.app.main import app
from super_admin_service.app.database import get_db
from super_admin_service.app.models import Base, School, SchoolAdmin, SchoolSubscription, PlatformStats

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_super_admin.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_school_data():
    return {
        "name": "Test High School",
        "domain": "testschool.edu",
        "contact_email": "admin@testschool.edu",
        "phone_number": "+1234567890",
        "address": "123 Education St, Test City"
    }

@pytest.fixture
def sample_admin_data():
    return {
        "full_name": "John Admin",
        "email": "admin@testschool.edu",
        "phone_number": "+1234567890"
    }

class TestSuperAdminService:
    """Test cases for Super Admin Service"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient, setup_database):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "super-admin-service"

    @pytest.mark.asyncio
    async def test_create_school(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test school creation"""
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        
        response = await client.post("/schools", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == sample_school_data["name"]
        assert data["domain"] == sample_school_data["domain"]
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_duplicate_school_domain(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test creating school with duplicate domain"""
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        
        # Create first school
        await client.post("/schools", json=payload)
        
        # Try to create duplicate
        response = await client.post("/schools", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_schools(self, client: AsyncClient, setup_database):
        """Test getting schools list"""
        response = await client.get("/schools")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_suspend_school(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test school suspension"""
        # Create school first
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        create_response = await client.post("/schools", json=payload)
        school_id = create_response.json()["id"]
        
        # Suspend school
        response = await client.patch(f"/schools/{school_id}/suspend")
        assert response.status_code == 200
        
        # Verify suspension
        get_response = await client.get(f"/schools/{school_id}")
        assert get_response.json()["status"] == "suspended"

    @pytest.mark.asyncio
    async def test_activate_school(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test school activation"""
        # Create and suspend school first
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        create_response = await client.post("/schools", json=payload)
        school_id = create_response.json()["id"]
        
        await client.patch(f"/schools/{school_id}/suspend")
        
        # Activate school
        response = await client.patch(f"/schools/{school_id}/activate")
        assert response.status_code == 200
        
        # Verify activation
        get_response = await client.get(f"/schools/{school_id}")
        assert get_response.json()["status"] == "active"

    @pytest.mark.asyncio
    async def test_platform_analytics(self, client: AsyncClient, setup_database):
        """Test platform analytics endpoint"""
        response = await client.get("/analytics/platform")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_schools" in data
        assert "active_schools" in data

    @pytest.mark.asyncio
    async def test_revenue_analytics(self, client: AsyncClient, setup_database):
        """Test revenue analytics endpoint"""
        response = await client.get("/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        assert "monthly_revenue" in data
        assert "total_revenue" in data
        assert "revenue_by_plan" in data

    @pytest.mark.asyncio
    async def test_invalid_school_id(self, client: AsyncClient, setup_database):
        """Test handling of invalid school ID"""
        response = await client.get("/schools/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_school(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test school update"""
        # Create school first
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        create_response = await client.post("/schools", json=payload)
        school_id = create_response.json()["id"]
        
        # Update school
        update_data = {"name": "Updated School Name"}
        response = await client.put(f"/schools/{school_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated School Name"

    @pytest.mark.asyncio
    async def test_school_pagination(self, client: AsyncClient, setup_database):
        """Test school list pagination"""
        response = await client.get("/schools?skip=0&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    @pytest.mark.asyncio
    async def test_school_status_filter(self, client: AsyncClient, setup_database):
        """Test filtering schools by status"""
        response = await client.get("/schools?status=active")
        assert response.status_code == 200
        
        data = response.json()
        for school in data:
            assert school["status"] == "active"

class TestServiceIntegration:
    """Integration tests for service interactions"""

    @pytest.mark.asyncio
    async def test_school_admin_relationship(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test school-admin relationship creation"""
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        
        response = await client.post("/schools", json=payload)
        school_id = response.json()["id"]
        
        # Get school admins
        admins_response = await client.get(f"/schools/{school_id}/admins")
        assert admins_response.status_code == 200
        
        admins = admins_response.json()
        assert len(admins) == 1
        assert admins[0]["email"] == sample_admin_data["email"]

    @pytest.mark.asyncio
    async def test_user_count_updates(self, client: AsyncClient, setup_database, sample_school_data, sample_admin_data):
        """Test updating school user counts"""
        # Create school first
        payload = {
            "school_data": sample_school_data,
            "admin_data": sample_admin_data
        }
        create_response = await client.post("/schools", json=payload)
        school_id = create_response.json()["id"]
        
        # Update user counts
        counts_data = {
            "students": 100,
            "teachers": 10,
            "admins": 2
        }
        response = await client.patch(f"/schools/{school_id}/user-counts", json=counts_data)
        assert response.status_code == 200
        
        # Verify counts updated
        get_response = await client.get(f"/schools/{school_id}")
        school_data = get_response.json()
        assert school_data["total_students"] == 100
        assert school_data["total_teachers"] == 10
        assert school_data["total_admins"] == 2

class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_malformed_json(self, client: AsyncClient, setup_database):
        """Test handling of malformed JSON"""
        response = await client.post("/schools", content="invalid json")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client: AsyncClient, setup_database):
        """Test handling of missing required fields"""
        payload = {
            "school_data": {"name": "Test School"},  # Missing required fields
            "admin_data": {"email": "test@example.com"}  # Missing required fields
        }
        
        response = await client.post("/schools", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_email_format(self, client: AsyncClient, setup_database):
        """Test handling of invalid email format"""
        payload = {
            "school_data": {
                "name": "Test School",
                "domain": "test.edu",
                "contact_email": "invalid-email"
            },
            "admin_data": {
                "full_name": "Admin User",
                "email": "invalid-email",
                "phone_number": "+1234567890"
            }
        }
        
        response = await client.post("/schools", json=payload)
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
