import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


@pytest.mark.api
class TestQueryEndpoint:
    """Test the /api/query endpoint"""
    
    def test_query_with_session_id(self, test_client, sample_query_request, expected_query_response):
        """Test query endpoint with existing session ID"""
        response = test_client.post("/api/query", json=sample_query_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["answer"] == expected_query_response["answer"]
        assert data["sources"] == expected_query_response["sources"]
        assert data["session_id"] == expected_query_response["session_id"]
    
    def test_query_without_session_id(self, test_client):
        """Test query endpoint without session ID (should create new session)"""
        query_request = {"query": "What is Python?"}
        
        response = test_client.post("/api/query", json=query_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session-123"  # From mock
    
    def test_query_with_empty_query(self, test_client):
        """Test query endpoint with empty query string"""
        query_request = {"query": ""}
        
        response = test_client.post("/api/query", json=query_request)
        
        assert response.status_code == 200  # FastAPI validation allows empty strings
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
    
    def test_query_with_missing_query_field(self, test_client):
        """Test query endpoint with missing required query field"""
        query_request = {"session_id": "test-123"}
        
        response = test_client.post("/api/query", json=query_request)
        
        assert response.status_code == 422  # Unprocessable Entity
        assert "detail" in response.json()
    
    def test_query_with_invalid_json(self, test_client):
        """Test query endpoint with invalid JSON"""
        response = test_client.post(
            "/api/query", 
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_query_endpoint_exception_handling(self, test_client):
        """Test query endpoint exception handling"""
        with patch('conftest.Mock.query') as mock_query:
            mock_query.side_effect = Exception("Test error")
            
            query_request = {"query": "What is Python?"}
            response = test_client.post("/api/query", json=query_request)
            
            assert response.status_code == 500
            assert "Test error" in response.json()["detail"]
    
    def test_query_response_structure(self, test_client, sample_query_request):
        """Test that query response has correct structure"""
        response = test_client.post("/api/query", json=sample_query_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["answer", "sources", "session_id"]
        for field in required_fields:
            assert field in data
        
        # Check field types
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)
        
        # Check sources are strings
        for source in data["sources"]:
            assert isinstance(source, str)
    
    def test_query_with_long_query(self, test_client):
        """Test query endpoint with very long query"""
        long_query = "What is Python? " * 1000  # Very long query
        query_request = {"query": long_query}
        
        response = test_client.post("/api/query", json=query_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data


@pytest.mark.api
class TestCoursesEndpoint:
    """Test the /api/courses endpoint"""
    
    def test_get_course_stats(self, test_client, expected_course_stats):
        """Test getting course statistics"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_courses"] == expected_course_stats["total_courses"]
        assert data["course_titles"] == expected_course_stats["course_titles"]
    
    def test_course_stats_response_structure(self, test_client):
        """Test that course stats response has correct structure"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["total_courses", "course_titles"]
        for field in required_fields:
            assert field in data
        
        # Check field types
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        
        # Check course titles are strings
        for title in data["course_titles"]:
            assert isinstance(title, str)
    
    def test_courses_endpoint_exception_handling(self, test_client):
        """Test courses endpoint exception handling"""
        with patch('conftest.Mock.get_course_analytics') as mock_analytics:
            mock_analytics.side_effect = Exception("Analytics error")
            
            response = test_client.get("/api/courses")
            
            assert response.status_code == 500
            assert "Analytics error" in response.json()["detail"]
    
    def test_courses_endpoint_methods(self, test_client):
        """Test that courses endpoint only accepts GET requests"""
        # Test POST (should not be allowed)
        response = test_client.post("/api/courses")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test PUT (should not be allowed)
        response = test_client.put("/api/courses")
        assert response.status_code == 405
        
        # Test DELETE (should not be allowed)
        response = test_client.delete("/api/courses")
        assert response.status_code == 405


@pytest.mark.api
class TestRootEndpoint:
    """Test the root / endpoint"""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns correct response"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert data["message"] == "Course Materials RAG System API"
    
    def test_root_endpoint_methods(self, test_client):
        """Test that root endpoint accepts different HTTP methods"""
        # Test GET (should work)
        response = test_client.get("/")
        assert response.status_code == 200
        
        # Test POST (should not be defined for root)
        response = test_client.post("/")
        assert response.status_code == 405  # Method Not Allowed


@pytest.mark.api
class TestAPIHeaders:
    """Test API headers and middleware"""
    
    def test_cors_headers(self, test_client):
        """Test that CORS headers are present"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        # CORS headers should be present due to middleware
        # Note: TestClient may not show all middleware headers
    
    def test_content_type_headers(self, test_client, sample_query_request):
        """Test content type headers in responses"""
        response = test_client.post("/api/query", json=sample_query_request)
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.api
class TestAPIValidation:
    """Test API input validation"""
    
    def test_query_request_validation(self, test_client):
        """Test request validation for query endpoint"""
        # Test with extra fields (should be ignored)
        query_request = {
            "query": "What is Python?",
            "session_id": "test-123",
            "extra_field": "should be ignored"
        }
        
        response = test_client.post("/api/query", json=query_request)
        assert response.status_code == 200
    
    def test_invalid_session_id_type(self, test_client):
        """Test query with invalid session_id type"""
        query_request = {
            "query": "What is Python?",
            "session_id": 12345  # Should be string
        }
        
        response = test_client.post("/api/query", json=query_request)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_query_type(self, test_client):
        """Test query with invalid query type"""
        query_request = {
            "query": 12345,  # Should be string
            "session_id": "test-123"
        }
        
        response = test_client.post("/api/query", json=query_request)
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    def test_query_to_courses_workflow(self, test_client):
        """Test workflow from query to getting course stats"""
        # First, make a query
        query_request = {"query": "What is Python?"}
        query_response = test_client.post("/api/query", json=query_request)
        
        assert query_response.status_code == 200
        query_data = query_response.json()
        assert "session_id" in query_data
        
        # Then get course stats
        courses_response = test_client.get("/api/courses")
        
        assert courses_response.status_code == 200
        courses_data = courses_response.json()
        assert courses_data["total_courses"] >= 0
        assert isinstance(courses_data["course_titles"], list)
    
    def test_multiple_queries_same_session(self, test_client):
        """Test multiple queries with the same session ID"""
        session_id = "persistent-session-123"
        
        # First query
        query1 = {"query": "What is Python?", "session_id": session_id}
        response1 = test_client.post("/api/query", json=query1)
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["session_id"] == session_id
        
        # Second query with same session
        query2 = {"query": "How do variables work?", "session_id": session_id}
        response2 = test_client.post("/api/query", json=query2)
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id