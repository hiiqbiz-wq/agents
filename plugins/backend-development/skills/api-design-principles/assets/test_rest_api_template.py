import pytest
from fastapi.testclient import TestClient
import importlib.util
import sys
import os

# Dynamically import the rest-api-template.py script
script_path = os.path.join(os.path.dirname(__file__), "rest-api-template.py")
spec = importlib.util.spec_from_file_location("rest_api_template", script_path)
rest_api_template = importlib.util.module_from_spec(spec)
sys.modules["rest_api_template"] = rest_api_template
spec.loader.exec_module(rest_api_template)

client = TestClient(rest_api_template.app, base_url="http://localhost")

def test_get_user_not_found():
    response = client.get("/api/users/999", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "HTTPException"
    assert data["message"] == "User not found"
    assert data["details"][0]["code"] == "not_found"
    assert data["details"][0]["field"] == "user_id"

def test_get_user_success():
    response = client.get("/api/users/123", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["email"] == "user@example.com"
    assert data["name"] == "User Name"
