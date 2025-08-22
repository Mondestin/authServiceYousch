"""
Pytest configuration and fixtures for API tests only
Provides common test setup and shared fixtures for API endpoint testing
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from app.core.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """Test settings fixture - override environment for testing"""
    # Override settings for testing
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FORMAT"] = "text"
    os.environ["TESTING"] = "true"
    
    # Force reload of settings
    from app.core.config import get_settings
    settings = get_settings()
    
    yield settings
    
    # Clean up test environment variables
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture(scope="function", autouse=True)
def mock_get_db_dependency():
    """Mock the get_db dependency to prevent real database access in tests"""
    with patch('app.api.deps.get_db') as mock_get_db:
        # Create a mock session
        mock_session = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.close = Mock()
        mock_session.add = Mock()
        mock_session.refresh = Mock()
        
        # Mock query method with proper chaining
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.count.return_value = 0
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        def mock_filter_by(**kwargs):
            mock_result = Mock()
            mock_result.first.return_value = None
            mock_result.all.return_value = []
            mock_result.count.return_value = 0
            return mock_result
        
        mock_query.filter_by = mock_filter_by
        mock_session.query = Mock(return_value=mock_query)
        
        mock_get_db.return_value = mock_session
        
        yield mock_session


@pytest.fixture(scope="function")
def mock_user():
    """Mock user object for testing"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    user.phone = "+1234567890"
    user.school_id = 1
    user.campus_id = None
    user.role_id = 1
    user.is_active = True
    user.is_verified = True
    user.hashed_password = "hashed_password_123"
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = None
    user.created_at = Mock()
    user.updated_at = Mock()
    
    # Mock properties
    user.full_name = "Test User"
    user.is_locked = False
    user.can_login = True
    
    # Mock methods
    user.lock_account = Mock()
    user.reset_failed_login_attempts = Mock()
    user.increment_failed_login_attempts = Mock()
    user.update_last_login = Mock()
    user.to_dict = Mock(return_value={
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "school_id": 1,
        "campus_id": None,
        "role_id": 1,
        "is_active": True,
        "is_verified": True
    })
    
    return user


@pytest.fixture(scope="function")
def mock_school():
    """Mock school object for testing"""
    school = Mock()
    school.id = 1
    school.name = "Test School"
    school.code = "TEST"
    school.domain = "https://test-school.com"
    school.created_at = Mock()
    school.updated_at = Mock()
    
    # Mock relationships
    school.campuses = []
    school.users = []
    school.roles = []
    
    # Mock methods
    school.to_dict = Mock(return_value={
        "id": 1,
        "name": "Test School",
        "code": "TEST",
        "domain": "https://test-school.com"
    })
    
    return school


@pytest.fixture(scope="function")
def mock_campus():
    """Mock campus object for testing"""
    campus = Mock()
    campus.id = 1
    campus.school_id = 1
    campus.name = "Test Campus"
    campus.address_street = "123 Test St"
    campus.address_city = "Test City"
    campus.address_postal = "12345"
    campus.address_country = "Test Country"
    campus.contact_email = "campus@test-school.com"
    campus.contact_phone = "+1234567890"
    campus.created_at = Mock()
    campus.updated_at = Mock()
    
    # Mock relationships
    campus.school = Mock()  # Don't call mock_school() directly
    campus.users = []
    campus.roles = []
    
    # Mock methods
    campus.to_dict = Mock(return_value={
        "id": 1,
        "school_id": 1,
        "name": "Test Campus",
        "address_street": "123 Test St",
        "address_city": "Test City"
    })
    
    return campus


@pytest.fixture(scope="function")
def mock_role():
    """Mock role object for testing"""
    role = Mock()
    role.id = 1
    role.name = "Test Role"
    role.description = "A test role"
    role.school_id = 1
    role.campus_id = None
    role.is_default = False
    role.created_at = Mock()
    role.updated_at = Mock()
    
    # Mock relationships
    role.school = Mock()  # Don't call mock_school() directly
    role.campus = None
    role.users = []
    role.permissions = []
    
    # Mock properties
    role.is_global = False
    role.is_school_level = True
    role.is_campus_level = False
    
    # Mock methods
    role.to_dict = Mock(return_value={
        "id": 1,
        "name": "Test Role",
        "description": "A test role",
        "school_id": 1,
        "campus_id": None,
        "is_default": False
    })
    
    return role


@pytest.fixture(scope="function")
def mock_permission():
    """Mock permission object for testing"""
    permission = Mock()
    permission.id = 1
    permission.name = "test.permission"
    permission.description = "A test permission"
    permission.created_at = Mock()
    
    # Mock relationships
    permission.roles = []
    
    # Mock methods
    permission.to_dict = Mock(return_value={
        "id": 1,
        "name": "test.permission",
        "description": "A test permission"
    })
    
    return permission


@pytest.fixture(scope="function")
def mock_user_session():
    """Mock user session object for testing"""
    session = Mock()
    session.id = 1
    session.user_id = 1
    session.session_token = "session_token_123"
    session.refresh_token = "refresh_token_123"
    session.ip_address = "192.168.1.1"
    session.user_agent = "Test Browser"
    session.is_active = True
    session.expires_at = Mock()
    session.created_at = Mock()
    session.last_used = Mock()
    
    # Mock methods
    session.is_expired = Mock(return_value=False)
    session.deactivate = Mock()
    session.update_last_used = Mock()
    
    return session


@pytest.fixture(scope="function")
def mock_login_history():
    """Mock login history object for testing"""
    history = Mock()
    history.id = 1
    history.user_id = 1
    history.ip_address = "192.168.1.100"
    history.device_info = "Test Device"
    history.login_time = Mock()
    history.status = "success"
    
    # Mock properties
    history.is_successful = True
    history.is_failed = False
    
    # Mock methods
    history.to_dict = Mock(return_value={
        "id": 1,
        "user_id": 1,
        "ip_address": "192.168.1.100",
        "device_info": "Test Device",
        "status": "success"
    })
    
    return history


@pytest.fixture(scope="function")
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashed_password_123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "school_id": 1,
        "role_id": 1
    }


@pytest.fixture(scope="function")
def sample_login_data():
    """Sample login data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture(scope="function")
def sample_school_data():
    """Sample school data for testing"""
    return {
        "name": "Test School",
        "code": "TEST",
        "domain": "https://test-school.com"
    }


@pytest.fixture(scope="function")
def sample_campus_data():
    """Sample campus data for testing"""
    return {
        "school_id": 1,
        "name": "Test Campus",
        "address_street": "123 Test St",
        "address_city": "Test City",
        "address_postal": "12345",
        "address_country": "Test Country",
        "contact_email": "campus@test-school.com",
        "contact_phone": "+1234567890"
    }


@pytest.fixture(scope="function")
def sample_role_data():
    """Sample role data for testing"""
    return {
        "name": "Test Role",
        "description": "A test role",
        "school_id": 1,
        "campus_id": None,
        "is_default": False
    }


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Mark tests based on file location
        if "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
            item.add_marker(pytest.mark.integration)


# Test session setup and teardown
@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """Setup test session"""
    print("\n🚀 Setting up test session for API tests...")
    
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "test"
    
    yield
    
    print("\n🧹 Cleaning up test session...")
    
    # Clean up test environment variables
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture(scope="function", autouse=True)
def setup_test_function():
    """Setup each test function"""
    # Reset any global state if needed
    pass
    
    yield
    
    # Clean up after each test
    pass 