# EduNerve Comprehensive Test Suite

This test suite provides comprehensive testing for all backend microservices and the API gateway in the EduNerve monorepo.

## 📁 Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── pytest.ini              # Pytest configuration (in project root)
├── requirements.txt         # Test dependencies
├── run_tests.py            # Main test runner script
├── test_service.py         # Individual service test runner
├── test_utils.py           # Test utilities and helpers
├── test_structure.py       # Structure and existence tests
├── test_api_endpoints.py   # API endpoint tests
├── test_integration.py     # Integration and E2E tests
└── reports/                # Generated test reports
    ├── coverage/           # Coverage reports
    ├── test_report.html    # HTML test report
    └── service_health_report.json
```

## 🧪 Test Categories

### 1. Structure Tests (`test_structure.py`)
- **Existence**: Verify all services, API gateway, and required files exist
- **Structure**: Check directory structure and required files in each service  
- **Configuration**: Validate Dockerfiles, requirements.txt, and config files
- **Python Syntax**: Ensure all Python files have valid syntax

### 2. API Endpoint Tests (`test_api_endpoints.py`)
- **Health Checks**: Test health endpoints for all services
- **Endpoint Existence**: Verify main API endpoints exist and respond
- **Response Structure**: Validate API response data structures
- **Error Handling**: Test error responses and status codes

### 3. Integration Tests (`test_integration.py`)
- **Service Communication**: Test cross-service interactions
- **Gateway Routing**: Verify API gateway correctly routes requests
- **Authentication Flow**: Test end-to-end authentication workflows
- **Data Consistency**: Verify data persistence across services
- **End-to-End Workflows**: Complete user workflows (registration → login → access)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- All services should be running (optional for structure tests)
- PostgreSQL database (optional, for database tests)

### Run All Tests
```bash
# From project root
cd tests
python run_tests.py
```

### Run Specific Test Categories
```bash
# Structure tests only
python run_tests.py --structure-only

# API tests only  
python run_tests.py --api-only

# Integration tests only
python run_tests.py --integration-only

# Quick smoke tests
python run_tests.py --quick
```

### Run Tests for Specific Service
```bash
# All tests for auth service
python test_service.py auth

# Only API tests for admin service
python test_service.py admin --type api

# Only structure tests for gateway
python test_service.py gateway --type structure
```

## 🔧 Configuration

### Service URLs
Tests are configured to connect to services on these default ports:
- Auth Service: `http://localhost:8001`
- Admin Service: `http://localhost:8002`
- Assistant Service: `http://localhost:8003`
- Content Quiz Service: `http://localhost:8004`
- File Storage Service: `http://localhost:8005`
- Notification Service: `http://localhost:8006`
- Progress Service: `http://localhost:8007`
- Sync Messaging Service: `http://localhost:8008`
- API Gateway: `http://localhost:8000`

To change these URLs, modify the `TEST_URLS` dictionary in `conftest.py`.

### Test Database
For database integration tests, set the `TEST_DATABASE_URL` environment variable:
```bash
export TEST_DATABASE_URL="postgresql://test:test@localhost:5432/edunerve_test"
```

## 📊 Test Reports

### HTML Report
After running tests, view the comprehensive HTML report:
```bash
open tests/reports/test_report.html
```

### Coverage Report  
View code coverage report:
```bash
open tests/reports/coverage/index.html
```

### Service Health Report
JSON report of service health status:
```bash
cat tests/reports/service_health_report.json
```

## 🎯 Test Markers

Use pytest markers to run specific test types:

```bash
# Unit tests only
pytest -m unit

# Integration tests only  
pytest -m integration

# Database tests only
pytest -m database

# Skip slow tests
pytest -m "not slow"

# Authentication tests only
pytest -m auth
```

## 🐛 Troubleshooting

### Services Not Running
If services are not running, tests will be skipped with appropriate messages:
```
SKIPPED [1] test_api_endpoints.py:25: Auth service not running
```

To start services:
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
cd services/auth-service && python main.py
```

### Import Errors
If you get import errors, ensure test dependencies are installed:
```bash
pip install -r tests/requirements.txt
```

### Database Connection Issues
For database tests, ensure PostgreSQL is running and test database exists:
```bash
createdb edunerve_test
```

## 📈 Test Coverage Goals

The test suite aims for:
- **Structure Coverage**: 100% - All services and files verified
- **API Coverage**: 80% - Main endpoints tested
- **Integration Coverage**: 70% - Key workflows verified
- **Code Coverage**: 70% - Minimum code coverage threshold

## 🔄 Continuous Integration

### GitHub Actions
Add to `.github/workflows/test.yml`:
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r tests/requirements.txt
    - name: Run tests
      run: |
        cd tests && python run_tests.py --quick
```

### Pre-commit Hook
Add to `.pre-commit-config.yaml`:
```yaml
repos:
- repo: local
  hooks:
  - id: run-tests
    name: Run test suite
    entry: tests/run_tests.py --quick
    language: python
    pass_filenames: false
```

## 📝 Writing New Tests

### Adding Structure Tests
Add new structure validation to `test_structure.py`:
```python
def test_new_service_structure(self, services_dir):
    """Test new service has required structure."""
    new_service_dir = services_dir / "new-service"
    assert new_service_dir.exists()
    # Add specific checks...
```

### Adding API Tests
Add new endpoint tests to `test_api_endpoints.py`:
```python
@pytest.mark.asyncio
async def test_new_endpoint(self, test_urls):
    """Test new API endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{test_urls['service']}/endpoint")
        assert response.status_code == 200
```

### Adding Integration Tests
Add workflow tests to `test_integration.py`:
```python
@pytest.mark.asyncio  
async def test_new_workflow(self, test_urls):
    """Test new end-to-end workflow."""
    # Implement multi-step workflow test
```

## 🤝 Contributing

1. Ensure all tests pass before submitting PR
2. Add tests for new functionality
3. Update this README if adding new test categories
4. Follow existing test patterns and conventions

## 📞 Support

For test-related issues:
1. Check service health: `python run_tests.py --no-deps`
2. Run structure tests first: `python run_tests.py --structure-only`
3. Check individual services: `python test_service.py <service-name>`
4. Review test reports in `tests/reports/`

---

**Test Suite Version**: 1.0  
**Last Updated**: 2024-01-15  
**Compatible With**: EduNerve Backend v1.0+
