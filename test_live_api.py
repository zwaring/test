import pytest
import httpx
import os

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test the root endpoint"""
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ISO Files API"}

def test_list_isos_endpoint():
    """Test the list ISOs endpoint"""
    response = httpx.get(f"{BASE_URL}/isos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify the structure of the first ISO file
    iso = data[0]
    required_fields = [
        "id", "name", "size_mb", "size_human", "created_date",
        "modified_date", "path", "volume_label", "file_system",
        "is_valid_iso"
    ]
    for field in required_fields:
        assert field in iso, f"Missing field: {field}"

def test_get_specific_iso():
    """Test getting a specific ISO by ID"""
    # First get the list to ensure we have ISOs
    response = httpx.get(f"{BASE_URL}/isos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # Get the first ISO
    iso_id = data[0]["id"]
    response = httpx.get(f"{BASE_URL}/isos/{iso_id}")
    assert response.status_code == 200
    iso = response.json()
    assert iso["id"] == iso_id

def test_get_nonexistent_iso():
    """Test getting a non-existent ISO"""
    response = httpx.get(f"{BASE_URL}/isos/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "ISO file not found"

def test_search_isos_by_name():
    """Test searching ISOs by name"""
    # Search for Ubuntu ISO
    response = httpx.get(f"{BASE_URL}/isos/search/?name=ubuntu")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:  # Only check if we found matches
        assert all("ubuntu" in iso["name"].lower() for iso in data)

def test_search_isos_by_size():
    """Test searching ISOs by size"""
    response = httpx.get(f"{BASE_URL}/isos/search/?min_size=1000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:  # Only check if we found matches
        assert all(iso["size_mb"] >= 1000 for iso in data)

def test_search_isos_with_multiple_filters():
    """Test searching ISOs with multiple filters"""
    response = httpx.get(f"{BASE_URL}/isos/search/?name=ubuntu&min_size=1000&max_size=10000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:  # Only check if we found matches
        assert all(
            "ubuntu" in iso["name"].lower() and 
            1000 <= iso["size_mb"] <= 10000 
            for iso in data
        )

def test_expected_iso_files():
    """Test that we can find specific ISO files we expect"""
    response = httpx.get(f"{BASE_URL}/isos")
    assert response.status_code == 200
    data = response.json()
    
    # Get all ISO names
    iso_names = [iso["name"].lower() for iso in data]
    
    # Check for expected ISOs
    expected_patterns = ["ubuntu", "proxmox", "win"]
    for pattern in expected_patterns:
        assert any(pattern in name for name in iso_names), f"Expected to find ISO containing '{pattern}'"

def test_iso_size_ranges():
    """Test that ISO sizes are within expected ranges"""
    response = httpx.get(f"{BASE_URL}/isos")
    assert response.status_code == 200
    data = response.json()
    
    for iso in data:
        # ISOs should be at least 100MB
        assert iso["size_mb"] > 100, f"ISO {iso['name']} is suspiciously small"
        # ISOs should be less than 20GB
        assert iso["size_mb"] < 20000, f"ISO {iso['name']} is suspiciously large" 