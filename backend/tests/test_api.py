import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from ai_brain_vault_service import app

# Test client for synchronous tests
client = TestClient(app)

@pytest.fixture
def mock_user():
    return {"user_id": "test_user_123", "email": "test@example.com"}

@pytest.fixture
def mock_idea_data():
    return {
        "content": "Test idea for AI-powered content generation",
        "source": "test"
    }

@pytest.fixture
def mock_idea_response():
    return {
        "id": 1,
        "content": "Test idea for AI-powered content generation",
        "source": "test",
        "timestamp": "2025-01-01T00:00:00",
        "project": None,
        "theme": None,
        "emotion": None,
        "transformed_output": None
    }

class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestIdeaEndpoints:
    @patch('ai_brain_vault_service.get_current_user')
    def test_capture_idea_success(self, mock_auth, mock_idea_data, mock_idea_response):
        """Test successful idea capture"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_conn.fetchval.return_value = 1
            
            with patch('ai_brain_vault_service.kafka_producer') as mock_kafka:
                response = client.post("/ideas/", json=mock_idea_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == 1
                assert data["content"] == mock_idea_data["content"]
                assert data["source"] == mock_idea_data["source"]
                
                # Verify database call
                mock_conn.fetchval.assert_called_once()
                
                # Verify Kafka message
                mock_kafka.send.assert_called_once()

    @patch('ai_brain_vault_service.get_current_user')
    def test_capture_idea_unauthorized(self, mock_auth):
        """Test idea capture without authentication"""
        mock_auth.side_effect = Exception("Unauthorized")
        
        response = client.post("/ideas/", json={"content": "test", "source": "test"})
        assert response.status_code == 401

    @patch('ai_brain_vault_service.get_current_user')
    def test_get_user_ideas(self, mock_auth):
        """Test getting user ideas"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            
            # Mock database response
            mock_idea = MagicMock()
            mock_idea.__getitem__.side_effect = lambda key: {
                "id": 1,
                "content": "Test idea",
                "source": "test",
                "timestamp": "2025-01-01T00:00:00",
                "project": "Test Project",
                "theme": "tech",
                "emotion": "excited",
                "transformed_output": None
            }[key]
            
            mock_conn.fetch.return_value = [mock_idea]
            
            response = client.get("/ideas/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["content"] == "Test idea"

    @patch('ai_brain_vault_service.get_current_user')
    def test_search_ideas(self, mock_auth):
        """Test idea search functionality"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_conn.fetch.return_value = []
            
            response = client.get("/ideas/search/?q=AI")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

class TestTransformEndpoints:
    @patch('ai_brain_vault_service.get_current_user')
    def test_transform_idea_success(self, mock_auth):
        """Test successful idea transformation"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        transform_request = {
            "idea_id": 1,
            "output_type": "content",
            "user_id": "test_user_123"
        }
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            
            # Mock idea exists
            mock_idea = MagicMock()
            mock_idea.__getitem__.side_effect = lambda key: {
                "id": 1,
                "content": "Test idea",
                "user_id": "test_user_123"
            }[key]
            mock_conn.fetchrow.return_value = mock_idea
            
            with patch('ai_brain_vault_service.generate_transformation') as mock_generate:
                mock_generate.return_value = "Generated blog post content"
                
                response = client.post("/transform/", json=transform_request)
                assert response.status_code == 200
                data = response.json()
                assert "transformed_content" in data

    @patch('ai_brain_vault_service.get_current_user')
    def test_transform_idea_not_found(self, mock_auth):
        """Test transformation of non-existent idea"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        transform_request = {
            "idea_id": 999,
            "output_type": "content",
            "user_id": "test_user_123"
        }
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_conn.fetchrow.return_value = None
            
            response = client.post("/transform/", json=transform_request)
            assert response.status_code == 404

class TestUserEndpoints:
    def test_create_user_success(self):
        """Test successful user creation"""
        user_data = {
            "auth0_id": "auth0|test123",
            "email": "test@example.com",
            "subscription": "free"
        }
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_conn.fetchval.return_value = 1
            
            response = client.post("/users/", json=user_data)
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["subscription"] == user_data["subscription"]

    @patch('ai_brain_vault_service.get_current_user')
    def test_get_current_user_info(self, mock_auth):
        """Test getting current user information"""
        mock_auth.return_value = {"user_id": "auth0|test123", "email": "test@example.com"}
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            
            mock_user = MagicMock()
            mock_user.__getitem__.side_effect = lambda key: {
                "id": 1,
                "email": "test@example.com",
                "subscription": "premium"
            }[key]
            mock_conn.fetchrow.return_value = mock_user
            
            response = client.get("/users/me")
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["subscription"] == "premium"

class TestVoiceEndpoints:
    @patch('ai_brain_vault_service.get_current_user')
    def test_voice_input_success(self, mock_auth):
        """Test successful voice input processing"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        with patch('ai_brain_vault_service.whisper_model') as mock_whisper:
            mock_whisper.transcribe.return_value = {"text": "Transcribed voice content"}
            
            with patch('ai_brain_vault_service.s3_client') as mock_s3:
                with patch('ai_brain_vault_service.capture_idea') as mock_capture:
                    mock_capture.return_value = {"id": 1, "content": "Transcribed voice content"}
                    
                    # Create a mock file
                    files = {"file": ("test.wav", b"fake audio data", "audio/wav")}
                    response = client.post("/ideas/voice/", files=files)
                    
                    assert response.status_code == 200

    @patch('ai_brain_vault_service.get_current_user')
    def test_voice_input_invalid_format(self, mock_auth):
        """Test voice input with invalid file format"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        files = {"file": ("test.txt", b"not audio data", "text/plain")}
        response = client.post("/ideas/voice/", files=files)
        assert response.status_code == 400

class TestNLPProcessing:
    @patch('ai_brain_vault_service.get_current_user')
    def test_idea_analysis(self, mock_auth):
        """Test NLP analysis endpoint"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_conn = MagicMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            
            mock_idea = MagicMock()
            mock_idea.__getitem__.side_effect = lambda key: {
                "id": 1,
                "content": "AI-powered content generation idea",
                "project": "AI Project",
                "theme": "technology",
                "emotion": "excited"
            }[key]
            mock_conn.fetchrow.return_value = mock_idea
            
            response = client.get("/ideas/1/analysis")
            assert response.status_code == 200
            data = response.json()
            assert data["project"] == "AI Project"
            assert data["theme"] == "technology"
            assert data["emotion"] == "excited"

class TestErrorHandling:
    def test_database_connection_error(self):
        """Test handling of database connection errors"""
        with patch('ai_brain_vault_service.app.state.pool') as mock_pool:
            mock_pool.acquire.side_effect = Exception("Database connection failed")
            
            response = client.get("/ideas/")
            assert response.status_code == 500

    def test_invalid_json_request(self):
        """Test handling of invalid JSON requests"""
        response = client.post("/ideas/", data="invalid json")
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/ideas/", json={"source": "test"})  # Missing content
        assert response.status_code == 422

class TestPerformance:
    @patch('ai_brain_vault_service.get_current_user')
    def test_concurrent_requests(self, mock_auth):
        """Test handling of concurrent requests"""
        mock_auth.return_value = {"user_id": "test_user_123", "email": "test@example.com"}
        
        async def make_request():
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.get("/health")
                return response.status_code
        
        # Test multiple concurrent requests
        async def test_concurrent():
            tasks = [make_request() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            return results
        
        results = asyncio.run(test_concurrent())
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 