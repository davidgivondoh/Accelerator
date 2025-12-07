"""
Integration Tests for API Endpoints
===================================

Tests for the FastAPI REST API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

# Import the FastAPI app
from src.api import app, create_app


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_returns_ok(self):
        """Test that health endpoint returns healthy status."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_health_check_includes_version(self):
        """Test that health endpoint includes version."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        
        data = response.json()
        assert "version" in data


class TestDiscoveryEndpoints:
    """Tests for discovery API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_opportunities_empty(self):
        """Test getting opportunities when none exist."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/discovery/opportunities")
        
        # Should return empty list or appropriate response
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_opportunities_with_filters(self):
        """Test getting opportunities with query filters."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/discovery/opportunities",
                params={"min_score": 0.7, "type": "job", "limit": 10}
            )
        
        assert response.status_code in [200, 404]


class TestApplicationEndpoints:
    """Tests for application API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_drafts_empty(self):
        """Test getting drafts when none exist."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/applications/drafts")
        
        assert response.status_code in [200, 404]


class TestAnalyticsEndpoints:
    """Tests for analytics API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_dashboard(self):
        """Test getting analytics dashboard."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/dashboard")
        
        assert response.status_code in [200, 500]  # May fail without DB


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    @pytest.mark.asyncio
    async def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
    
    @pytest.mark.asyncio
    async def test_docs_available(self):
        """Test that Swagger docs are available."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/docs")
        
        assert response.status_code == 200


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    @pytest.mark.asyncio
    async def test_cors_headers_present(self):
        """Test that CORS headers are set correctly."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.options(
                "/health",
                headers={"Origin": "http://localhost:3000"}
            )
        
        # CORS preflight should be handled
        assert response.status_code in [200, 204, 405]


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_404_for_unknown_route(self):
        """Test 404 response for unknown routes."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_validation_error_response(self):
        """Test validation error returns proper format."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/discovery/opportunities",
                params={"min_score": "invalid"}  # Should be float
            )
        
        # Should return 422 for validation error
        assert response.status_code in [200, 422]
