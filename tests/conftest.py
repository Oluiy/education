import os
import sys
import pytest
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add all service directories to path
services_dir = project_root / "services"
for service_dir in services_dir.iterdir():
    if service_dir.is_dir():
        sys.path.insert(0, str(service_dir))

# Add API gateway to path
api_gateway_dir = project_root / "api-gateway"
sys.path.insert(0, str(api_gateway_dir))

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def services_dir(project_root):
    """Return the services directory."""
    return project_root / "services"

@pytest.fixture(scope="session")
def api_gateway_dir(project_root):
    """Return the API gateway directory."""
    return project_root / "api-gateway"

# Service URLs for testing
TEST_URLS = {
    "auth": "http://localhost:8001",
    "admin": "http://localhost:8002", 
    "assistant": "http://localhost:8003",
    "content-quiz": "http://localhost:8004",
    "file-storage": "http://localhost:8005",
    "notification": "http://localhost:8006",
    "progress": "http://localhost:8007",
    "sync-messaging": "http://localhost:8008",
    "gateway": "http://localhost:8000"
}

@pytest.fixture(scope="session")
def test_urls():
    """Return test URLs for all services."""
    return TEST_URLS

# Database test configuration
@pytest.fixture(scope="session")
def test_db_url():
    """Return test database URL."""
    return os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/edunerve_test")

# Authentication fixtures
@pytest.fixture
def test_user_data():
    """Return test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "student"
    }

@pytest.fixture
def test_admin_data():
    """Return test admin data."""
    return {
        "email": "admin@example.com", 
        "password": "adminpassword123",
        "full_name": "Test Admin",
        "role": "admin"
    }

@pytest.fixture
def test_teacher_data():
    """Return test teacher data."""
    return {
        "email": "teacher@example.com",
        "password": "teacherpassword123", 
        "full_name": "Test Teacher",
        "role": "teacher"
    }
