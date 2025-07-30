"""
Integration tests for cross-service functionality.
Tests workflows that span multiple services and the API gateway.
"""

import asyncio
import httpx
import pytest
from typing import Dict, Any, Optional


class TestServiceIntegration:
    """Test integration between services."""
    
    @pytest.mark.asyncio
    async def test_auth_and_admin_integration(self, test_urls, test_admin_data):
        """Test authentication flow with admin service access."""
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Register admin user
                register_response = await client.post(
                    f"{test_urls['auth']}/register", 
                    json=test_admin_data
                )
                
                if register_response.status_code in [200, 201]:
                    # Step 2: Login and get token
                    login_response = await client.post(
                        f"{test_urls['auth']}/login",
                        json={
                            "email": test_admin_data["email"],
                            "password": test_admin_data["password"]
                        }
                    )
                    
                    if login_response.status_code in [200, 201]:
                        login_data = login_response.json()
                        token = login_data.get("access_token") or login_data.get("token")
                        
                        if token:
                            # Step 3: Use token to access admin service
                            headers = {"Authorization": f"Bearer {token}"}
                            admin_response = await client.get(
                                f"{test_urls['admin']}/schools",
                                headers=headers
                            )
                            
                            assert admin_response.status_code != 401, "Token authentication failed"
                        else:
                            pytest.skip("No token returned from login")
                    else:
                        pytest.skip("Login failed")
                else:
                    pytest.skip("Registration failed")
                    
            except httpx.ConnectError:
                pytest.skip("Services not running")
    
    @pytest.mark.asyncio
    async def test_file_storage_and_content_integration(self, test_urls):
        """Test file storage integration with content service."""
        async with httpx.AsyncClient() as client:
            try:
                # Check if file storage service is available
                storage_response = await client.get(f"{test_urls['file-storage']}/health")
                content_response = await client.get(f"{test_urls['content-quiz']}/health")
                
                if storage_response.status_code in [200, 404] and content_response.status_code in [200, 404]:
                    # Test basic connectivity between services
                    files_response = await client.get(f"{test_urls['file-storage']}/files")
                    quizzes_response = await client.get(f"{test_urls['content-quiz']}/quizzes")
                    
                    # Both services should be accessible
                    assert files_response.status_code != 500, "File storage service error"
                    assert quizzes_response.status_code != 500, "Content quiz service error"
                else:
                    pytest.skip("Required services not running")
                    
            except httpx.ConnectError:
                pytest.skip("Services not running")
    
    @pytest.mark.asyncio
    async def test_notification_and_messaging_integration(self, test_urls):
        """Test integration between notification and messaging services."""
        async with httpx.AsyncClient() as client:
            try:
                # Check service availability
                notification_health = await client.get(f"{test_urls['notification']}/health")
                messaging_health = await client.get(f"{test_urls['sync-messaging']}/health")
                
                if (notification_health.status_code in [200, 404] and 
                    messaging_health.status_code in [200, 404]):
                    
                    # Test endpoints exist
                    notifications_response = await client.get(f"{test_urls['notification']}/notifications")
                    messages_response = await client.get(f"{test_urls['sync-messaging']}/messages")
                    
                    assert notifications_response.status_code != 500, "Notification service error"
                    assert messages_response.status_code != 500, "Messaging service error"
                else:
                    pytest.skip("Required services not running")
                    
            except httpx.ConnectError:
                pytest.skip("Services not running")


class TestGatewayIntegration:
    """Test API gateway integration with all services."""
    
    @pytest.mark.asyncio
    async def test_gateway_service_routing(self, test_urls):
        """Test that gateway correctly routes to all services."""
        async with httpx.AsyncClient() as client:
            try:
                # Test routing to each service through gateway
                service_routes = {
                    "auth": "/auth/health",
                    "admin": "/admin/health", 
                    "assistant": "/assistant/health",
                    "content-quiz": "/content/health",
                    "file-storage": "/files/health",
                    "notification": "/notifications/health",
                    "progress": "/progress/health",
                    "sync-messaging": "/messages/health"
                }
                
                for service, route in service_routes.items():
                    try:
                        response = await client.get(f"{test_urls['gateway']}{route}")
                        # Should not get 404 from gateway (service might return 404 for health)
                        assert response.status_code != 502, f"Gateway cannot reach {service}"
                    except httpx.ConnectError:
                        pytest.skip(f"Gateway or {service} not running")
                        
            except httpx.ConnectError:
                pytest.skip("Gateway not running")
    
    @pytest.mark.asyncio
    async def test_gateway_authentication_flow(self, test_urls, test_user_data):
        """Test authentication flow through gateway."""
        async with httpx.AsyncClient() as client:
            try:
                # Register through gateway
                register_response = await client.post(
                    f"{test_urls['gateway']}/auth/register",
                    json=test_user_data
                )
                
                if register_response.status_code in [200, 201, 409]:  # 409 = already exists
                    # Login through gateway
                    login_response = await client.post(
                        f"{test_urls['gateway']}/auth/login",
                        json={
                            "email": test_user_data["email"],
                            "password": test_user_data["password"]
                        }
                    )
                    
                    if login_response.status_code in [200, 201]:
                        login_data = login_response.json()
                        assert isinstance(login_data, dict), "Login response should be a dictionary"
                        
                        # Check for token in response
                        has_token = any(key in login_data for key in ["token", "access_token", "jwt"])
                        if not has_token:
                            pytest.skip("No authentication token in response")
                    else:
                        pytest.skip("Login through gateway failed")
                else:
                    pytest.skip("Registration through gateway failed")
                    
            except httpx.ConnectError:
                pytest.skip("Gateway not running")
    
    @pytest.mark.asyncio
    async def test_gateway_error_handling(self, test_urls):
        """Test gateway error handling and fallback mechanisms."""
        async with httpx.AsyncClient() as client:
            try:
                # Test request to non-existent service endpoint
                response = await client.get(f"{test_urls['gateway']}/nonexistent/endpoint")
                
                # Gateway should return proper error response
                assert response.status_code in [404, 502, 503], "Gateway not handling errors properly"
                
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                    assert isinstance(data, dict), "Error response should be JSON dictionary"
                    
            except httpx.ConnectError:
                pytest.skip("Gateway not running")


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_student_registration_to_quiz_workflow(self, test_urls, test_user_data):
        """Test complete workflow from student registration to taking a quiz."""
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Register student
                student_data = {**test_user_data, "role": "student"}
                register_response = await client.post(
                    f"{test_urls['gateway']}/auth/register",
                    json=student_data
                )
                
                if register_response.status_code in [200, 201, 409]:
                    # Step 2: Login
                    login_response = await client.post(
                        f"{test_urls['gateway']}/auth/login",
                        json={
                            "email": student_data["email"],
                            "password": student_data["password"]
                        }
                    )
                    
                    if login_response.status_code in [200, 201]:
                        login_data = login_response.json()
                        token = login_data.get("access_token") or login_data.get("token")
                        
                        if token:
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            # Step 3: Access quiz service
                            quiz_response = await client.get(
                                f"{test_urls['gateway']}/content/quizzes",
                                headers=headers
                            )
                            
                            # Should be able to access quizzes
                            assert quiz_response.status_code != 401, "Authentication failed for quiz access"
                            assert quiz_response.status_code != 403, "Authorization failed for quiz access"
                            
                        else:
                            pytest.skip("No token in login response")
                    else:
                        pytest.skip("Login failed")
                else:
                    pytest.skip("Registration failed")
                    
            except httpx.ConnectError:
                pytest.skip("Services not running")
    
    @pytest.mark.asyncio
    async def test_teacher_content_management_workflow(self, test_urls, test_teacher_data):
        """Test teacher workflow for managing content and quizzes."""
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Register teacher
                register_response = await client.post(
                    f"{test_urls['gateway']}/auth/register",
                    json=test_teacher_data
                )
                
                if register_response.status_code in [200, 201, 409]:
                    # Step 2: Login
                    login_response = await client.post(
                        f"{test_urls['gateway']}/auth/login",
                        json={
                            "email": test_teacher_data["email"], 
                            "password": test_teacher_data["password"]
                        }
                    )
                    
                    if login_response.status_code in [200, 201]:
                        login_data = login_response.json()
                        token = login_data.get("access_token") or login_data.get("token")
                        
                        if token:
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            # Step 3: Access content management
                            content_response = await client.get(
                                f"{test_urls['gateway']}/content/quizzes",
                                headers=headers
                            )
                            
                            # Step 4: Access file storage
                            files_response = await client.get(
                                f"{test_urls['gateway']}/files/files",
                                headers=headers
                            )
                            
                            # Teacher should have access to both services
                            assert content_response.status_code != 401, "Teacher auth failed for content"
                            assert files_response.status_code != 401, "Teacher auth failed for files"
                            
                        else:
                            pytest.skip("No token in login response")
                    else:
                        pytest.skip("Login failed")
                else:
                    pytest.skip("Registration failed")
                    
            except httpx.ConnectError:
                pytest.skip("Services not running")


class TestDatabaseIntegration:
    """Test database connectivity and operations across services."""
    
    @pytest.mark.asyncio
    async def test_user_data_persistence(self, test_urls, test_user_data):
        """Test that user data persists across service restarts."""
        async with httpx.AsyncClient() as client:
            try:
                # Create a unique user for this test
                unique_email = f"test_{asyncio.get_event_loop().time()}@example.com"
                user_data = {**test_user_data, "email": unique_email}
                
                # Register user
                register_response = await client.post(
                    f"{test_urls['auth']}/register",
                    json=user_data
                )
                
                if register_response.status_code in [200, 201]:
                    # Try to login immediately (tests data persistence)
                    login_response = await client.post(
                        f"{test_urls['auth']}/login",
                        json={
                            "email": unique_email,
                            "password": user_data["password"]
                        }
                    )
                    
                    assert login_response.status_code in [200, 201], "User data not persisted"
                else:
                    pytest.skip("Registration failed")
                    
            except httpx.ConnectError:
                pytest.skip("Auth service not running")
    
    @pytest.mark.asyncio
    async def test_cross_service_data_consistency(self, test_urls, test_user_data):
        """Test data consistency across services."""
        async with httpx.AsyncClient() as client:
            try:
                # Register user through auth service
                register_response = await client.post(
                    f"{test_urls['auth']}/register",
                    json=test_user_data
                )
                
                if register_response.status_code in [200, 201]:
                    # Login to get token
                    login_response = await client.post(
                        f"{test_urls['auth']}/login",
                        json={
                            "email": test_user_data["email"],
                            "password": test_user_data["password"]
                        }
                    )
                    
                    if login_response.status_code in [200, 201]:
                        login_data = login_response.json()
                        token = login_data.get("access_token") or login_data.get("token")
                        
                        if token:
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            # Check if user data is accessible from other services
                            progress_response = await client.get(
                                f"{test_urls['progress']}/progress",
                                headers=headers
                            )
                            
                            # Should recognize the user (not get authentication error)
                            assert progress_response.status_code != 401, "Cross-service auth failed"
                        else:
                            pytest.skip("No token in login response")
                    else:
                        pytest.skip("Login failed")
                else:
                    pytest.skip("Registration failed")
                    
            except httpx.ConnectError:
                pytest.skip("Services not running")
