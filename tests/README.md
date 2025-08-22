# API Tests

This directory contains comprehensive API tests for the AuthService using pytest and FastAPI's TestClient.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures for API tests
- `test_api.py` - Comprehensive API endpoint tests

## Test Coverage

The API tests cover all endpoints across the following areas:

### Health & Root Endpoints
- Health check endpoint
- Root endpoint with environment info

### Authentication Endpoints
- User registration
- User login
- Token refresh
- User logout

### School Management
- Create schools
- List schools
- Get school by ID
- Update schools
- Delete schools

### Campus Management
- Create campuses
- List campuses
- Get campus by ID
- Update campuses
- Delete campuses

### Role Management
- Create roles
- List roles
- Get role by ID
- Update roles
- Delete roles
- List permissions

### User Management
- Create users
- List users
- Get user by ID
- Update users
- Delete users

## Running Tests

### Prerequisites
1. Activate your virtual environment:
   ```bash
   source venv/bin/activate  # On Unix/macOS
   # or
   venv\Scripts\activate     # On Windows
   ```

2. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_api.py
```

### Run Specific Test Class
```bash
pytest tests/test_api.py::TestHealthEndpoints
```

### Run Specific Test Method
```bash
pytest tests/test_api.py::TestHealthEndpoints::test_health_check
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Print Statements
```bash
pytest -s
```

## Test Configuration

### Environment Variables
Tests automatically set the following environment variables:
- `ENVIRONMENT=test`
- `SECRET_KEY=test-secret-key-for-testing-only`
- `LOG_LEVEL=DEBUG`
- `LOG_FORMAT=text`
- `TESTING=true`

### Database Mocking
All tests use mocked database sessions to prevent real database access:
- The `mock_get_db_dependency` fixture automatically mocks `app.api.deps.get_db`
- This ensures complete isolation from production databases
- Tests can configure mock responses for different scenarios

### Mock Objects
The test suite provides mock objects for all major entities:
- `mock_user` - Mock user with realistic properties and methods
- `mock_school` - Mock school with relationships
- `mock_campus` - Mock campus with relationships
- `mock_role` - Mock role with permissions
- `mock_permission` - Mock permission
- `mock_user_session` - Mock user session
- `mock_login_history` - Mock login history

## Test Data

Sample data fixtures are provided for testing:
- `sample_user_data` - User creation data
- `sample_login_data` - Login credentials
- `sample_school_data` - School creation data
- `sample_campus_data` - Campus creation data
- `sample_role_data` - Role creation data

## Test Markers

Tests are automatically marked based on their location:
- `@pytest.mark.api` - All API tests
- `@pytest.mark.integration` - All API tests (considered integration tests)

## Best Practices

1. **Isolation**: Each test is completely isolated from others
2. **Mocking**: Real database and external dependencies are mocked
3. **Realistic Data**: Mock objects provide realistic responses
4. **Comprehensive Coverage**: All endpoints and HTTP methods are tested
5. **Error Handling**: Both success and error scenarios are covered

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure your virtual environment is activated and dependencies are installed
2. **Module Not Found**: Check that you're running tests from the project root directory
3. **Mock Issues**: Verify that mock objects are properly configured for your test case

### Debug Mode

To debug failing tests, run with verbose output and print statements:
```bash
pytest -v -s --tb=long
```

### Test Isolation

If tests are interfering with each other, ensure you're using the `mock_get_db_dependency` fixture which automatically resets the mock database session for each test. 