"""
File Upload API Test Script
Tests all file upload endpoints
"""

import requests
import json
from pathlib import Path
import io

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = None  # Will be set after login

# Test credentials (from demo)
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(test_name, success, details=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

def login():
    """Login and get auth token"""
    print_section("1. Authentication")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token")
            print_result("Login", True, f"Token received: {token[:20]}...")
            return token
        else:
            print_result("Login", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_result("Login", False, str(e))
        return None

def create_test_file(filename, content=b"Test file content", mime_type="text/plain"):
    """Create a test file in memory"""
    return (filename, io.BytesIO(content), mime_type)

def test_upload_single_file(token):
    """Test single file upload"""
    print_section("2. Upload Single File")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test PDF-like file
    test_content = b"%PDF-1.4\nTest PDF content"
    files = {"file": ("test_document.pdf", io.BytesIO(test_content), "application/pdf")}
    
    data = {
        "document_type": "PAN Card",
        "document_number": "ABCDE1234F",
        "entity_type": "customer",
        "entity_id": "test-customer-001",
        "remarks": "Test upload via API"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/files/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 201:
            result = response.json()
            file_data = result.get("data", {})
            file_id = file_data.get("id")
            print_result("Upload Single File", True, f"File ID: {file_id}")
            print(f"    Filename: {file_data.get('filename')}")
            print(f"    Size: {file_data.get('file_size')} bytes")
            return file_id
        else:
            print_result("Upload Single File", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_result("Upload Single File", False, str(e))
        return None

def test_upload_multiple_files(token):
    """Test multiple file upload"""
    print_section("3. Upload Multiple Files")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create multiple test files
    files = [
        ("files", ("doc1.pdf", io.BytesIO(b"%PDF-1.4\nDoc 1"), "application/pdf")),
        ("files", ("doc2.pdf", io.BytesIO(b"%PDF-1.4\nDoc 2"), "application/pdf")),
        ("files", ("doc3.jpg", io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF"), "image/jpeg")),
    ]
    
    data = {
        "document_type": "Bank Statement",
        "entity_type": "customer",
        "entity_id": "test-customer-001",
        "remarks": "Multiple test uploads"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/files/upload-multiple",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 201:
            result = response.json()
            files_data = result.get("data", {}).get("files", [])
            count = result.get("data", {}).get("count", 0)
            print_result("Upload Multiple Files", True, f"{count} files uploaded")
            file_ids = [f.get("id") for f in files_data]
            for i, file_data in enumerate(files_data, 1):
                print(f"    File {i}: {file_data.get('original_filename')} - {file_data.get('file_size')} bytes")
            return file_ids
        else:
            print_result("Upload Multiple Files", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print_result("Upload Multiple Files", False, str(e))
        return []

def test_get_file_metadata(token, file_id):
    """Test getting file metadata"""
    print_section("4. Get File Metadata")
    
    if not file_id:
        print_result("Get File Metadata", False, "No file ID provided")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/files/{file_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            file_data = result.get("data", {})
            print_result("Get File Metadata", True)
            print(f"    ID: {file_data.get('id')}")
            print(f"    Original Name: {file_data.get('original_filename')}")
            print(f"    Document Type: {file_data.get('document_type')}")
            print(f"    Size: {file_data.get('file_size')} bytes")
            print(f"    Entity: {file_data.get('entity_type')}/{file_data.get('entity_id')}")
        else:
            print_result("Get File Metadata", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_result("Get File Metadata", False, str(e))

def test_download_file(token, file_id):
    """Test file download"""
    print_section("5. Download File")
    
    if not file_id:
        print_result("Download File", False, "No file ID provided")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/files/{file_id}/download",
            headers=headers
        )
        
        if response.status_code == 200:
            content_disposition = response.headers.get('Content-Disposition', '')
            content_type = response.headers.get('Content-Type', '')
            content_length = len(response.content)
            print_result("Download File", True)
            print(f"    Content-Type: {content_type}")
            print(f"    Content-Disposition: {content_disposition}")
            print(f"    Size: {content_length} bytes")
        else:
            print_result("Download File", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_result("Download File", False, str(e))

def test_list_files_by_entity(token):
    """Test listing files by entity"""
    print_section("6. List Files by Entity")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/files/entity/customer/test-customer-001",
            headers=headers,
            params={"page": 1, "page_size": 10}
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            total = data.get("total", 0)
            files = data.get("files", [])
            print_result("List Files by Entity", True, f"Found {total} files")
            for i, file_data in enumerate(files, 1):
                print(f"    {i}. {file_data.get('original_filename')} - {file_data.get('document_type')}")
        else:
            print_result("List Files by Entity", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_result("List Files by Entity", False, str(e))

def test_delete_file(token, file_id):
    """Test file deletion"""
    print_section("7. Delete File")
    
    if not file_id:
        print_result("Delete File", False, "No file ID provided")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(
            f"{BASE_URL}/files/{file_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            success = result.get("data", {}).get("success", False)
            print_result("Delete File", success, "File marked as inactive")
        else:
            print_result("Delete File", False, f"Status: {response.status_code}")
            
    except Exception as e:
        print_result("Delete File", False, str(e))

def test_validation_errors(token):
    """Test validation errors"""
    print_section("8. Validation Tests")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Invalid file type
    print("\nTest 8.1: Invalid File Type")
    invalid_file = {"file": ("test.exe", io.BytesIO(b"executable"), "application/x-msdownload")}
    data = {"document_type": "PAN Card"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/files/upload",
            headers=headers,
            files=invalid_file,
            data=data
        )
        
        if response.status_code == 400:
            print_result("Invalid File Type Rejected", True, "Bad request as expected")
        else:
            print_result("Invalid File Type Rejected", False, f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_result("Invalid File Type Rejected", False, str(e))
    
    # Test 2: Too many files
    print("\nTest 8.2: Too Many Files (>10)")
    many_files = [
        ("files", (f"doc{i}.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"))
        for i in range(15)
    ]
    data = {"document_type": "Bank Statement"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/files/upload-multiple",
            headers=headers,
            files=many_files,
            data=data
        )
        
        if response.status_code == 400:
            print_result("Too Many Files Rejected", True, "Rejected >10 files as expected")
        else:
            print_result("Too Many Files Rejected", False, f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_result("Too Many Files Rejected", False, str(e))

def main():
    """Main test runner"""
    print("\n" + "=" * 70)
    print("  FILE UPLOAD API TEST SUITE")
    print("  Testing: http://localhost:8000/api/v1/files")
    print("=" * 70)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Failed to authenticate. Cannot proceed with tests.")
        print("Make sure:")
        print("  1. Backend server is running (uvicorn backend.main:app)")
        print("  2. Database is accessible")
        print("  3. Admin user exists with credentials: admin/admin123")
        return
    
    # Step 2: Upload single file
    file_id = test_upload_single_file(token)
    
    # Step 3: Upload multiple files
    file_ids = test_upload_multiple_files(token)
    
    # Step 4: Get metadata
    if file_id:
        test_get_file_metadata(token, file_id)
    
    # Step 5: Download file
    if file_id:
        test_download_file(token, file_id)
    
    # Step 6: List files by entity
    test_list_files_by_entity(token)
    
    # Step 7: Delete file
    if file_ids and len(file_ids) > 0:
        test_delete_file(token, file_ids[0])
    
    # Step 8: Validation tests
    test_validation_errors(token)
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All tests completed!")
    print("\nNext Steps:")
    print("  1. Check Swagger UI: http://localhost:8000/docs")
    print("  2. Review uploaded files in: uploads/default/")
    print("  3. Verify database records in file_uploads table")
    print("  4. Test from frontend file upload components")

if __name__ == "__main__":
    main()
