import httpx
import json
from typing import Any, Dict, List

BASE_URL = "http://localhost:8000"

def print_test_result(name: str, passed: bool, details: Any = None):
    """Print test result in a readable format"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"\n{status} - {name}")
    if details and not passed:
        print(f"Details: {details}")

def test_endpoint(url: str, test_name: str) -> Dict:
    """Test an endpoint and return the response"""
    try:
        response = httpx.get(url)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
            "error": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "data": None,
            "error": str(e)
        }

def main():
    print("\n🔍 Testing ISO Files API\n")
    
    # Test root endpoint
    result = test_endpoint(f"{BASE_URL}/", "Root endpoint")
    print_test_result(
        "Root endpoint",
        result["status_code"] == 200 and result["data"] == {"message": "Welcome to the ISO Files API"},
        result
    )
    
    # Test list ISOs endpoint
    result = test_endpoint(f"{BASE_URL}/isos", "List ISOs")
    has_isos = result["status_code"] == 200 and isinstance(result["data"], list) and len(result["data"]) > 0
    print_test_result("List ISOs endpoint", has_isos, result if not has_isos else None)
    
    if has_isos:
        isos = result["data"]
        first_iso = isos[0]
        
        # Test ISO structure
        required_fields = [
            "id", "name", "size_mb", "size_human", "created_date",
            "modified_date", "path", "volume_label", "file_system",
            "is_valid_iso"
        ]
        missing_fields = [field for field in required_fields if field not in first_iso]
        print_test_result(
            "ISO data structure",
            len(missing_fields) == 0,
            f"Missing fields: {missing_fields}" if missing_fields else None
        )
        
        # Test specific ISO endpoint
        iso_id = first_iso["id"]
        result = test_endpoint(f"{BASE_URL}/isos/{iso_id}", f"Get ISO {iso_id}")
        print_test_result(
            f"Get specific ISO (ID: {iso_id})",
            result["status_code"] == 200 and result["data"]["id"] == iso_id,
            result if result["status_code"] != 200 else None
        )
        
        # Test search endpoints
        search_tests = [
            ("name=ubuntu", "Search by name (ubuntu)"),
            ("min_size=1000", "Search by minimum size"),
            ("name=ubuntu&min_size=1000&max_size=10000", "Search with multiple filters")
        ]
        
        for params, test_name in search_tests:
            result = test_endpoint(f"{BASE_URL}/isos/search/?{params}", test_name)
            print_test_result(
                test_name,
                result["status_code"] == 200 and isinstance(result["data"], list),
                result if result["status_code"] != 200 else None
            )
        
        # Test expected ISO patterns
        expected_patterns = ["ubuntu", "proxmox", "win"]
        iso_names = [iso["name"].lower() for iso in isos]
        for pattern in expected_patterns:
            found = any(pattern in name for name in iso_names)
            print_test_result(
                f"Find ISO with pattern: {pattern}",
                found,
                f"No ISO found containing '{pattern}'" if not found else None
            )
        
        # Test ISO size ranges
        invalid_sizes = []
        for iso in isos:
            if not (100 < iso["size_mb"] < 20000):
                invalid_sizes.append(f"{iso['name']}: {iso['size_mb']} MB")
        
        print_test_result(
            "ISO size ranges",
            len(invalid_sizes) == 0,
            f"Invalid sizes: {invalid_sizes}" if invalid_sizes else None
        )
    
    print("\n✨ API testing completed!\n")

if __name__ == "__main__":
    main() 