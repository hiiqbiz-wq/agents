import pytest
from pydantic import ValidationError
from .rest_api_template import UserCreate, UserStatus

def test_user_create_valid():
    """Test UserCreate with valid data."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123",
        "status": UserStatus.ACTIVE
    }
    user = UserCreate(**user_data)
    assert user.email == user_data["email"]
    assert user.name == user_data["name"]
    assert user.password == user_data["password"]
    assert user.status == UserStatus.ACTIVE

def test_user_create_default_status():
    """Test UserCreate with default status."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123"
    }
    user = UserCreate(**user_data)
    assert user.status == UserStatus.ACTIVE

def test_user_create_invalid_email():
    """Test UserCreate with invalid email."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="invalid-email",
            name="Test User",
            password="password123"
        )
    assert "email" in str(exc_info.value)

def test_user_create_short_password():
    """Test UserCreate with short password."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            name="Test User",
            password="short"
        )
    assert "password" in str(exc_info.value)
    assert "at least 8 characters" in str(exc_info.value)

def test_user_create_empty_name():
    """Test UserCreate with empty name."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            name="",
            password="password123"
        )
    assert "name" in str(exc_info.value)
    assert "at least 1 character" in str(exc_info.value)

def test_user_create_long_name():
    """Test UserCreate with name exceeding max length."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            name="a" * 101,
            password="password123"
        )
    assert "name" in str(exc_info.value)
    assert "at most 100 characters" in str(exc_info.value)

def test_user_create_invalid_status():
    """Test UserCreate with invalid status."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            name="Test User",
            password="password123",
            status="invalid-status"
        )
    assert "status" in str(exc_info.value)

def test_user_create_missing_fields():
    """Test UserCreate with missing required fields."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate()

    errors = str(exc_info.value)
    assert "email" in errors
    assert "name" in errors
    assert "password" in errors
