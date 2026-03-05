import importlib.util
import sys
import pytest
from fastapi.testclient import TestClient
import os

# Dynamically import the rest-api-template.py module
current_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.abspath(
    os.path.join(current_dir, "..", "assets", "rest-api-template.py")
)

spec = importlib.util.spec_from_file_location("rest_api_template", target_path)
rest_api_template = importlib.util.module_from_spec(spec)
sys.modules["rest_api_template"] = rest_api_template
spec.loader.exec_module(rest_api_template)

# Setup test client
app = rest_api_template.app


# Override dependencies to bypass authentication
async def mock_get_current_user():
    return "mock_user"


app.dependency_overrides[rest_api_template.get_current_user] = mock_get_current_user

client = TestClient(app)


def test_list_users_default_pagination():
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] == 100
    assert data["pages"] == 5
    assert len(data["items"]) == 20
    assert data["items"][0]["id"] == "0"
    assert data["items"][19]["id"] == "19"


def test_list_users_custom_pagination():
    response = client.get("/api/users?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 10
    assert data["total"] == 100
    assert data["pages"] == 10
    assert len(data["items"]) == 10
    assert data["items"][0]["id"] == "10"
    assert data["items"][9]["id"] == "19"


def _load_module_with_env(env_vars):
    """Helper to load the rest-api-template module with specific env vars."""
    old_env = {}
    for key, value in env_vars.items():
        old_env[key] = os.environ.get(key)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        spec = importlib.util.spec_from_file_location("_rest_api_template_tmp", target_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for key, original in old_env.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original


def test_bind_host_default():
    """Verify BIND_HOST defaults to 127.0.0.1 when env var is not set."""
    module = _load_module_with_env({"BIND_HOST": None})
    assert module.BIND_HOST == "127.0.0.1"


def test_bind_host_env_override():
    """Verify BIND_HOST can be overridden via environment variable."""
    module = _load_module_with_env({"BIND_HOST": "0.0.0.0"})
    assert module.BIND_HOST == "0.0.0.0"


def test_list_users_filter_status():
    # Test that the status query parameter is handled correctly
    response = client.get("/api/users?status=active&page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["items"]) == 5
    # The template just returns everything based on calculation for mock but parameter gets parsed
    assert data["items"][0]["id"] == "0"
    assert data["items"][0]["status"] == "active"
