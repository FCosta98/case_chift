from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import get_db
from main import app
from models.models import Base, Facture
import pytest
import os
from config import API_KEY

# Create a test database (in-memory SQLite for simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply override for testing
app.dependency_overrides[get_db] = override_get_db

# Create tables for test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Test 1: Create a contact and verify it's created
def test_create_contact():
    # Send the request to create a contact
    response = client.post("/contacts/", json={"name": "John Doe", "email": "john.doe@example.com"}, headers={"X-API-Key": API_KEY})
    
    # Assert the response status code is 200 (success)
    assert response.status_code == 200
    
    # Assert the response contains the correct data
    created_contact = response.json()
    assert created_contact["name"] == "John Doe"
    assert created_contact["email"] == "john.doe@example.com"
    
    # Verify that the contact exists in the database
    response = client.get("/contacts/", headers={"X-API-Key": API_KEY})
    contacts = response.json()
    assert len(contacts) > 0
    assert contacts[-1]["name"] == "John Doe"
    assert contacts[-1]["email"] == "john.doe@example.com"

# Test 2: Retrieve a contact by ID
def test_get_contact_by_id():
    # Create a contact first
    create_response = client.post("/contacts/", json={"name": "Jane Smith", "email": "jane.smith@example.com"}, headers={"X-API-Key": API_KEY})
    created_contact = create_response.json()
    contact_id = created_contact["id"]
    
    # Retrieve the contact by ID
    response = client.get(f"/contacts/{contact_id}", headers={"X-API-Key": API_KEY})
    
    # Assert the response status code is 200 (success)
    assert response.status_code == 200
    
    # Assert the response contains the correct contact data
    contact = response.json()
    assert contact["id"] == contact_id
    assert contact["name"] == "Jane Smith"
    assert contact["email"] == "jane.smith@example.com"

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield  # Run all tests first
    if os.path.exists("test.db"):
        os.remove("test.db")
