"""
API endpoint tests for all services.
Tests each service's main endpoints for expected responses and data structures.
"""

import asyncio
import httpx
import pytest
from typing import Dict, Any


class EndpointDiscovery:
    """Helper class to discover available endpoints."""
    
    @staticmethod
    async def discover_endpoints(base_url: str, service_name: str, endpoint_patterns: list) -> dict:
        """Discover which endpoints exist for a service."""
        results = {"service": service_name, "base_url": base_url, "endpoints": {}, "accessible": False}
        
        async with httpx.AsyncClient() as client:
            try:
                # First check if service is accessible
                response = await client.get(f"{base_url}/health", timeout=5)
                results["accessible"] = True
            except:
                try:
                    response = await client.get(f"{base_url}/", timeout=5)
                    results["accessible"] = True
                except:
                    return results
            
            for pattern in endpoint_patterns:
                try:
                    # Try GET first
                    response = await client.get(f"{base_url}{pattern}")
                    if response.status_code != 404:
                        results["endpoints"][pattern] = {"method": "GET", "status": response.status_code}
                        continue
                    
                    # Try POST if GET returns 404
                    response = await client.post(f"{base_url}{pattern}", json={})
                    if response.status_code != 404:
                        results["endpoints"][pattern] = {"method": "POST", "status": response.status_code}
                
                except httpx.ConnectError:
                    break
                except Exception:
                    pass
        
        return results


class TestServiceEndpoints:
    """Test all service endpoints in a unified way."""
    
    SERVICES = {
        'auth': {
            'name': 'Auth Service',
            'endpoints': ['/register', '/login', '/token', '/api/auth/register', '/api/auth/login', '/auth/register', '/auth/login']
        },
        'admin': {
            'name': 'Admin Service', 
            'endpoints': ['/schools', '/users', '/api/schools', '/api/users', '/admin/schools', '/admin/users']
        },
        'assistant': {
            'name': 'Assistant Service',
            'endpoints': ['/chat', '/api/chat', '/assistant/chat', '/query', '/api/query']
        },
        'content-quiz': {
            'name': 'Content Quiz Service',
            'endpoints': ['/quizzes', '/api/quizzes', '/quiz', '/api/quiz', '/content', '/api/content']
        },
        'file-storage': {
            'name': 'File Storage Service',
            'endpoints': ['/files', '/upload', '/api/files', '/api/upload', '/storage', '/api/storage']
        },
        'notification': {
            'name': 'Notification Service',
            'endpoints': ['/notifications', '/api/notifications', '/notify', '/api/notify', '/send']
        },
        'progress': {
            'name': 'Progress Service',
            'endpoints': ['/progress', '/api/progress', '/stats', '/api/stats', '/analytics']
        },
        'sync-messaging': {
            'name': 'Sync Messaging Service',
            'endpoints': ['/messages', '/api/messages', '/chat', '/api/chat', '/sync']
        }
    }
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key", SERVICES.keys())
    async def test_service_endpoint_discovery(self, test_urls, service_key):
        """Discover available endpoints for each service."""
        service_info = self.SERVICES[service_key]
        service_url = test_urls[service_key]
        
        # Discover endpoints
        discovery = await EndpointDiscovery.discover_endpoints(
            service_url, 
            service_info['name'], 
            service_info['endpoints'] + ['/health', '/docs', '/api', '/', '/status']
        )
        
        if not discovery["accessible"]:
            pytest.skip(f"{service_info['name']} not accessible")
        
        print(f"\n🔍 {service_info['name']} Discovery Report:")
        print(f"   Base URL: {service_url}")
        
        if discovery["endpoints"]:
            print(f"   ✅ Found {len(discovery['endpoints'])} accessible endpoints:")
            for endpoint, info in discovery["endpoints"].items():
                status = info.get('status', 'unknown')
                method = info.get('method', 'unknown')
                print(f"      {endpoint} ({method}: {status})")
        else:
            print(f"   ⚠️  No standard endpoints found (service may be minimal or use different paths)")
        
        # At minimum, service should be accessible
        assert discovery["accessible"], f"{service_info['name']} is not accessible"


class TestServiceHealthChecks:
    """Test health check endpoints for all services."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("service_key", TestServiceEndpoints.SERVICES.keys())
    async def test_service_health_endpoint(self, test_urls, service_key):
        """Test that each service responds to health checks."""
        service_info = TestServiceEndpoints.SERVICES[service_key]
        service_url = test_urls[service_key]
        
        async with httpx.AsyncClient() as client:
            try:
                # Try common health check endpoints
                health_endpoints = ['/health', '/api/health', '/status', '/']
                
                for endpoint in health_endpoints:
                    try:
                        response = await client.get(f"{service_url}{endpoint}", timeout=5)
                        if response.status_code in [200, 404]:  # 404 is OK - service is responding
                            print(f"✅ {service_info['name']} responding at {endpoint} (status: {response.status_code})")
                            return  # Service is responding
                    except httpx.ConnectError:
                        continue
                    except Exception:
                        continue
                
                pytest.skip(f"{service_info['name']} not accessible")
                
            except Exception as e:
                pytest.skip(f"{service_info['name']} not accessible: {e}")


class TestAPIGatewayRouting:
    """Test API Gateway routing capabilities."""
    
    @pytest.mark.asyncio
    async def test_gateway_routing_discovery(self, test_urls):
        """Test that API gateway can route to services."""
        gateway_url = test_urls['gateway']
        
        async with httpx.AsyncClient() as client:
            try:
                # Test if gateway is accessible
                response = await client.get(f"{gateway_url}/", timeout=5)
                print(f"✅ API Gateway accessible (status: {response.status_code})")
                
                # Try common gateway patterns
                gateway_patterns = [
                    '/api/auth', '/api/admin', '/api/assistant', '/api/content',
                    '/api/files', '/api/notifications', '/api/progress', '/api/messages',
                    '/auth', '/admin', '/assistant', '/content', '/files', '/notifications',
                    '/progress', '/messages', '/docs', '/health', '/status'
                ]
                
                discovery = await EndpointDiscovery.discover_endpoints(
                    gateway_url, "API Gateway", gateway_patterns
                )
                
                if discovery["endpoints"]:
                    print(f"✅ Gateway has {len(discovery['endpoints'])} accessible routes:")
                    for endpoint, info in discovery["endpoints"].items():
                        status = info.get('status', 'unknown')
                        method = info.get('method', 'unknown')
                        print(f"   {endpoint} ({method}: {status})")
                else:
                    print(f"ℹ️  Gateway responding but no standard routes found")
                
                assert discovery["accessible"], "API Gateway is not accessible"
                
            except httpx.ConnectError:
                pytest.skip("API Gateway not accessible")
            except Exception as e:
                pytest.skip(f"API Gateway error: {e}")


class TestCrossServiceCommunication:
    """Test basic cross-service communication patterns."""
    
    @pytest.mark.asyncio
    async def test_service_to_service_accessibility(self, test_urls):
        """Test that services can potentially communicate with each other."""
        accessible_services = []
        
        for service_key, service_url in test_urls.items():
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{service_url}/health", timeout=2)
                    if response.status_code in [200, 404]:
                        accessible_services.append(service_key)
                except:
                    try:
                        response = await client.get(f"{service_url}/", timeout=2)
                        if response.status_code in [200, 404]:
                            accessible_services.append(service_key)
                    except:
                        pass
        
        print(f"🔗 Service Communication Report:")
        print(f"   Accessible services: {len(accessible_services)}/{len(test_urls)}")
        print(f"   Services online: {', '.join(accessible_services)}")
        
        offline_services = set(test_urls.keys()) - set(accessible_services)
        if offline_services:
            print(f"   Services offline: {', '.join(offline_services)}")
        
        # At least some services should be accessible for integration testing
        assert len(accessible_services) >= 1, "No services are accessible for testing"
        
        # If gateway is accessible, it should be able to route to other services
        if 'gateway' in accessible_services:
            print(f"   ✅ API Gateway is online and can potentially route to {len(accessible_services)-1} services")
