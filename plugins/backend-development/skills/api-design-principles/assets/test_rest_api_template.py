import pytest
from fastapi.testclient import TestClient
import importlib.util
import sys
import os

# Import the module dynamically since it has dashes in its name
module_name = "rest_api_template"
file_path = os.path.join(os.path.dirname(__file__), "rest-api-template.py")

spec = importlib.util.spec_from_file_location(module_name, file_path)
rest_api_template = importlib.util.module_from_spec(spec)
sys.modules[module_name] = rest_api_template
spec.loader.exec_module(rest_api_template)

app = rest_api_template.app

client = TestClient(app)

def test_read_docs():
    response = client.get("/api/docs")
    assert response.status_code == 200

def test_list_users_default_pagination():
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) <= 20

def test_list_users_custom_pagination():
    response = client.get("/api/users?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10

def test_list_users_invalid_pagination():
    response = client.get("/api/users?page=0")
    assert response.status_code == 422

def test_create_user_success():
    payload = {
        "email": "test@example.com",
        "name": "Test User",
        "status": "active",
        "password": "strongpassword123"
    }
    response = client.post("/api/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert data["status"] == payload["status"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_user_invalid_email():
    payload = {
        "email": "not-an-email",
        "name": "Test User",
        "password": "strongpassword123"
    }
    response = client.post("/api/users", json=payload)
    assert response.status_code == 422

def test_create_user_short_password():
    payload = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "short"
    }
    response = client.post("/api/users", json=payload)
    assert response.status_code == 422

def test_get_user_success():
    response = client.get("/api/users/123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert "email" in data
    assert "name" in data

def test_get_user_not_found():
    response = client.get("/api/users/999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "HTTPException"
    assert "User not found" in data["message"]

def test_update_user_success():
    payload = {
        "name": "Updated Name"
    }
    response = client.patch("/api/users/123", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "Updated Name"

def test_update_user_not_found():
    payload = {
        "name": "Updated Name"
    }
    response = client.patch("/api/users/999", json=payload)
    assert response.status_code == 404

def test_delete_user_success():
    response = client.delete("/api/users/123")
    assert response.status_code == 204

def test_delete_user_not_found():
    response = client.delete("/api/users/999")
    assert response.status_code == 404
