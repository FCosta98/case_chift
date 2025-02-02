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

# 1️ Test: Create a facture and verify it exists in the list
def test_create_facture():
    response = client.post("/factures/", json={"title": "Test Facture", "company": "Test Company", "amount": 99.99}, headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    created_facture = response.json()
    assert created_facture["title"] == "Test Facture"
    assert created_facture["company"] == "Test Company"
    assert created_facture["amount"] == 99.99

    # Get all factures and check if the new one is in the list
    response = client.get("/factures/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    factures = response.json()
    assert any(f["title"] == "Test Facture" for f in factures)

# 2️ Test: Retrieve a facture by its ID
def test_get_facture_by_id():
    # First, create a facture
    response = client.post("/factures/", json={"title": "Facture 2", "company": "Another Company", "amount": 150.75}, headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    facture_id = response.json()["id"]

    # Now retrieve it
    response = client.get(f"/factures/{facture_id}", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    facture = response.json()
    assert facture["id"] == facture_id
    assert facture["title"] == "Facture 2"
    assert facture["company"] == "Another Company"
    assert facture["amount"] == 150.75

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield  # Run all tests first
    if os.path.exists("test.db"):
        os.remove("test.db")
