"""
EduNerve File Storage Service - Test Script
Tests all major endpoints and functionality with database storage
"""

import asyncio
import aiohttp
import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, Any

class FileStorageServiceTester:
    """Test suite for file storage service"""
    
    def __init__(self):
        self.base_url = "http://localhost:8005"
        self.auth_token = None
        self.test_files = []
        self.test_collections = []
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        print("🧪 Starting EduNerve File Storage Service Tests")
        print("=" * 50)
        
        start_time = time.time()
        
        # Health check
        await self.test_health_check()
        
        # Authentication (mock)
        await self.setup_auth()
        
        # File upload tests
        await self.test_single_file_upload()
        await self.test_multiple_file_upload()
        await self.test_file_upload_validation()
        
        # File management tests
        await self.test_file_retrieval()
        await self.test_file_download()
        await self.test_file_update()
        
        # File search tests
        await self.test_file_search()
        await self.test_file_listing()
        
        # File sharing tests
        await self.test_file_sharing()
        await self.test_public_link_sharing()
        
        # Collections tests
        await self.test_file_collections()
        
        # Analytics tests
        await self.test_file_analytics()
        await self.test_quota_management()
        
        # Bulk operations tests
        await self.test_bulk_operations()
        
        # Cleanup tests
        await self.test_file_deletion()
        
        end_time = time.time()
        
        # Print results
        self.print_test_results(end_time - start_time)
    
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_success("Health Check", f"Service is {data['status']}")
                        return True
                    else:
                        self.log_error("Health Check", f"Status: {response.status}")
                        return False
        except Exception as e:
            self.log_error("Health Check", str(e))
            return False
    
    async def setup_auth(self):
        """Setup authentication (mock token)"""
        # In real implementation, this would call auth service
        self.auth_token = "mock-jwt-token-for-testing"
        self.log_success("Authentication", "Mock token created")
    
    async def test_single_file_upload(self):
        """Test single file upload"""
        try:
            # Create a test file
            test_content = b"This is a test file content for EduNerve"
            
            async with aiohttp.ClientSession() as session:
                # Create form data
                data = aiohttp.FormData()
                data.add_field('file', test_content, filename='test_document.txt', content_type='text/plain')
                data.add_field('entity_type', 'content')
                data.add_field('entity_id', 'test_content_123')
                data.add_field('access_level', 'school')
                data.add_field('tags', 'test,document,sample')
                
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.post(f"{self.base_url}/api/v1/files/upload", 
                                      data=data, headers=headers) as response:
                    if response.status == 200:
                        file_data = await response.json()
                        self.test_files.append(file_data)
                        self.log_success("Single File Upload", 
                                       f"File uploaded: {file_data['original_filename']}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("Single File Upload", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("Single File Upload", str(e))
            return False
    
    async def test_multiple_file_upload(self):
        """Test multiple file upload"""
        try:
            # Create test files
            test_files = [
                (b"First test file", "file1.txt", "text/plain"),
                (b"Second test file", "file2.txt", "text/plain"),
                (b"Third test file", "file3.txt", "text/plain")
            ]
            
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                
                for content, filename, content_type in test_files:
                    data.add_field('files', content, filename=filename, content_type=content_type)
                
                data.add_field('entity_type', 'batch_upload')
                data.add_field('access_level', 'private')
                
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.post(f"{self.base_url}/api/v1/files/upload-multiple", 
                                      data=data, headers=headers) as response:
                    if response.status == 200:
                        files_data = await response.json()
                        self.test_files.extend(files_data)
                        self.log_success("Multiple File Upload", 
                                       f"Uploaded {len(files_data)} files")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("Multiple File Upload", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("Multiple File Upload", str(e))
            return False
    
    async def test_file_upload_validation(self):
        """Test file upload validation"""
        try:
            # Test oversized file (mock large file)
            large_content = b"x" * (100 * 1024 * 1024)  # 100MB
            
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file', large_content, filename='large_file.txt', content_type='text/plain')
                
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.post(f"{self.base_url}/api/v1/files/upload", 
                                      data=data, headers=headers) as response:
                    if response.status == 413:  # Payload too large
                        self.log_success("File Upload Validation", "Large file rejected correctly")
                        return True
                    else:
                        self.log_error("File Upload Validation", f"Expected 413, got {response.status}")
                        return False
        except Exception as e:
            self.log_error("File Upload Validation", str(e))
            return False
    
    async def test_file_retrieval(self):
        """Test file metadata retrieval"""
        if not self.test_files:
            self.log_error("File Retrieval", "No test files available")
            return False
        
        try:
            file_id = self.test_files[0]['file_id']
            
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.get(f"{self.base_url}/api/v1/files/{file_id}", 
                                     headers=headers) as response:
                    if response.status == 200:
                        file_data = await response.json()
                        self.log_success("File Retrieval", 
                                       f"Retrieved file: {file_data['original_filename']}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Retrieval", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Retrieval", str(e))
            return False
    
    async def test_file_download(self):
        """Test file download"""
        if not self.test_files:
            self.log_error("File Download", "No test files available")
            return False
        
        try:
            file_id = self.test_files[0]['file_id']
            
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.get(f"{self.base_url}/api/v1/files/{file_id}/download", 
                                     headers=headers) as response:
                    if response.status == 200:
                        content = await response.read()
                        self.log_success("File Download", 
                                       f"Downloaded {len(content)} bytes")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Download", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Download", str(e))
            return False
    
    async def test_file_update(self):
        """Test file metadata update"""
        if not self.test_files:
            self.log_error("File Update", "No test files available")
            return False
        
        try:
            file_id = self.test_files[0]['file_id']
            
            update_data = {
                "filename": "updated_filename.txt",
                "tags": ["updated", "modified", "test"],
                "access_level": "public"
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.put(f"{self.base_url}/api/v1/files/{file_id}", 
                                     json=update_data, headers=headers) as response:
                    if response.status == 200:
                        file_data = await response.json()
                        self.log_success("File Update", 
                                       f"Updated file: {file_data['filename']}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Update", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Update", str(e))
            return False
    
    async def test_file_search(self):
        """Test file search functionality"""
        try:
            search_data = {
                "query": "test",
                "file_type": "document",
                "limit": 10,
                "offset": 0
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(f"{self.base_url}/api/v1/files/search", 
                                      json=search_data, headers=headers) as response:
                    if response.status == 200:
                        results = await response.json()
                        self.log_success("File Search", 
                                       f"Found {len(results.get('files', []))} files")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Search", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Search", str(e))
            return False
    
    async def test_file_listing(self):
        """Test file listing"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.get(f"{self.base_url}/api/v1/files?limit=20", 
                                     headers=headers) as response:
                    if response.status == 200:
                        results = await response.json()
                        self.log_success("File Listing", 
                                       f"Listed {len(results.get('files', []))} files")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Listing", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Listing", str(e))
            return False
    
    async def test_file_sharing(self):
        """Test file sharing"""
        if not self.test_files:
            self.log_error("File Sharing", "No test files available")
            return False
        
        try:
            file_id = self.test_files[0]['file_id']
            
            share_data = {
                "shared_with": [2, 3, 4],  # User IDs
                "can_download": True,
                "can_edit": False,
                "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(f"{self.base_url}/api/v1/files/{file_id}/share", 
                                      json=share_data, headers=headers) as response:
                    if response.status == 200:
                        share_result = await response.json()
                        self.log_success("File Sharing", 
                                       f"Shared with {len(share_data['shared_with'])} users")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Sharing", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Sharing", str(e))
            return False
    
    async def test_public_link_sharing(self):
        """Test public link sharing"""
        if not self.test_files:
            self.log_error("Public Link Sharing", "No test files available")
            return False
        
        try:
            file_id = self.test_files[0]['file_id']
            
            # Get existing shares
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.get(f"{self.base_url}/api/v1/files/{file_id}/shares", 
                                     headers=headers) as response:
                    if response.status == 200:
                        shares = await response.json()
                        self.log_success("Public Link Sharing", 
                                       f"Retrieved {len(shares)} shares")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("Public Link Sharing", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("Public Link Sharing", str(e))
            return False
    
    async def test_file_collections(self):
        """Test file collections"""
        if len(self.test_files) < 2:
            self.log_error("File Collections", "Need at least 2 test files")
            return False
        
        try:
            collection_data = {
                "name": "Test Collection",
                "description": "A collection of test files",
                "collection_type": "lesson",
                "file_ids": [f['file_id'] for f in self.test_files[:2]],
                "access_level": "school"
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(f"{self.base_url}/api/v1/collections", 
                                      json=collection_data, headers=headers) as response:
                    if response.status == 200:
                        collection = await response.json()
                        self.test_collections.append(collection)
                        self.log_success("File Collections", 
                                       f"Created collection: {collection['name']}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Collections", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Collections", str(e))
            return False
    
    async def test_file_analytics(self):
        """Test file analytics"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.get(f"{self.base_url}/api/v1/files/analytics", 
                                     headers=headers) as response:
                    if response.status == 200:
                        analytics = await response.json()
                        self.log_success("File Analytics", 
                                       f"Total files: {analytics['total_files']}, "
                                       f"Total size: {analytics['total_size']} bytes")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Analytics", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Analytics", str(e))
            return False
    
    async def test_quota_management(self):
        """Test quota management"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.get(f"{self.base_url}/api/v1/files/quota", 
                                     headers=headers) as response:
                    if response.status == 200:
                        quota = await response.json()
                        self.log_success("Quota Management", 
                                       f"Used: {quota['used_quota']}/{quota['total_quota']} bytes "
                                       f"({quota['usage_percentage']:.1f}%)")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("Quota Management", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("Quota Management", str(e))
            return False
    
    async def test_bulk_operations(self):
        """Test bulk operations"""
        if len(self.test_files) < 2:
            self.log_error("Bulk Operations", "Need at least 2 test files")
            return False
        
        try:
            bulk_data = {
                "file_ids": [f['file_id'] for f in self.test_files[:2]],
                "operation": "update",
                "parameters": {
                    "tags": ["bulk", "updated", "test"]
                }
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(f"{self.base_url}/api/v1/files/bulk", 
                                      json=bulk_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.log_success("Bulk Operations", 
                                       f"Updated {result['successful']} files")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("Bulk Operations", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("Bulk Operations", str(e))
            return False
    
    async def test_file_deletion(self):
        """Test file deletion"""
        if not self.test_files:
            self.log_error("File Deletion", "No test files available")
            return False
        
        try:
            file_id = self.test_files[-1]['file_id']  # Delete last file
            
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.auth_token}'}
                
                async with session.delete(f"{self.base_url}/api/v1/files/{file_id}", 
                                        headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.log_success("File Deletion", result['message'])
                        return True
                    else:
                        error_text = await response.text()
                        self.log_error("File Deletion", f"Status: {response.status}, Error: {error_text}")
                        return False
        except Exception as e:
            self.log_error("File Deletion", str(e))
            return False
    
    def log_success(self, test_name: str, message: str):
        """Log successful test"""
        result = f"✅ {test_name}: {message}"
        print(result)
        self.test_results.append(("PASS", test_name, message))
    
    def log_error(self, test_name: str, message: str):
        """Log failed test"""
        result = f"❌ {test_name}: {message}"
        print(result)
        self.test_results.append(("FAIL", test_name, message))
    
    def print_test_results(self, duration: float):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("🧪 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result[0] == "PASS")
        failed = sum(1 for result in self.test_results if result[0] == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for status, test_name, message in self.test_results:
                if status == "FAIL":
                    print(f"  - {test_name}: {message}")
        
        print("\n" + "=" * 50)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! File Storage Service is working correctly.")
        else:
            print(f"⚠️  {failed} tests failed. Please check the service configuration.")
        
        print("=" * 50)

async def main():
    """Run the test suite"""
    tester = FileStorageServiceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
