import pytest
from fastapi.testclient import TestClient
from api import app
import os
from pathlib import Path
import shutil

# Create a test directory with sample ISO files
TEST_DIR = "test_isos"
SAMPLE_ISO = "test.iso"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with sample ISO files"""
    # Create test directory
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # Create a sample ISO file (empty file for testing)
    sample_iso_path = Path(TEST_DIR) / SAMPLE_ISO
    sample_iso_path.touch()
    
    # Set environment variable for test directory
    os.environ["ISO_DIR"] = TEST_DIR
    
    yield
    
    # Cleanup
    shutil.rmtree(TEST_DIR)

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ISO Files API"}

def test_list_isos_endpoint(client):
    """Test the list ISOs endpoint"""
    response = client.get("/isos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify the structure of the first ISO file
    iso = data[0]
    assert "id" in iso
    assert "name" in iso
    assert "size_mb" in iso
    assert "size_human" in iso
    assert "created_date" in iso
    assert "modified_date" in iso
    assert "path" in iso
    assert "volume_label" in iso
    assert "file_system" in iso
    assert "is_valid_iso" in iso

def test_get_specific_iso(client):
    """Test getting a specific ISO by ID"""
    # First get the list to ensure we have ISOs
    response = client.get("/isos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # Get the first ISO
    iso_id = data[0]["id"]
    response = client.get(f"/isos/{iso_id}")
    assert response.status_code == 200
    iso = response.json()
    assert iso["id"] == iso_id

def test_get_nonexistent_iso(client):
    """Test getting a non-existent ISO"""
    response = client.get("/isos/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "ISO file not found"

def test_search_isos_by_name(client):
    """Test searching ISOs by name"""
    response = client.get("/isos/search/?name=ubuntu")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("ubuntu" in iso["name"].lower() for iso in data)

def test_search_isos_by_size(client):
    """Test searching ISOs by size"""
    response = client.get("/isos/search/?min_size=1000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(iso["size_mb"] >= 1000 for iso in data)

def test_search_isos_by_volume_label(client):
    """Test searching ISOs by volume label"""
    response = client.get("/isos/search/?volume_label=ubuntu")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_search_isos_with_multiple_filters(client):
    """Test searching ISOs with multiple filters"""
    response = client.get("/isos/search/?name=ubuntu&min_size=1000&max_size=10000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(
        "ubuntu" in iso["name"].lower() and 
        1000 <= iso["size_mb"] <= 10000 
        for iso in data
    )

def test_iso_metadata_structure(client):
    """Test that ISO metadata has the correct structure"""
    response = client.get("/isos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    iso = data[0]
    # Check all required fields
    required_fields = [
        "id", "name", "size_mb", "size_human", "created_date",
        "modified_date", "path", "volume_label", "file_system",
        "is_valid_iso", "iso_creation_date", "iso_modification_date",
        "iso_application_id", "iso_publisher_id", "iso_preparer_id"
    ]
    
    for field in required_fields:
        assert field in iso, f"Missing field: {field}" 