"""
Tests for API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

from app.schemas.treatment_summary import TreatmentSummaryOutput


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, test_client):
        """Test that health endpoint returns 200."""
        response = test_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "app_version" in data


class TestTreatmentSummaryEndpoint:
    """Test treatment summary generation endpoint."""
    
    @patch("app.api.routes.generate_treatment_summary")
    @patch("app.api.routes.log_generation")
    def test_generate_treatment_summary_success(
        self,
        mock_log_generation,
        mock_generate,
        test_client,
        sample_treatment_request,
        mock_openai_response,
    ):
        """Test successful treatment summary generation."""
        # Mock the service response
        mock_result = AsyncMock()
        mock_result.output = TreatmentSummaryOutput(**mock_openai_response)
        mock_result.tokens_used = 450
        mock_result.generation_time_ms = 1250
        mock_generate.return_value = mock_result
        
        # Mock audit logging
        mock_log_generation.return_value = AsyncMock()
        
        # Make request
        response = test_client.post(
            "/api/v1/generate-treatment-summary",
            json=sample_treatment_request,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "document" in data
        assert data["document"]["title"] == mock_openai_response["title"]
        assert "metadata" in data
        assert data["metadata"]["tokens_used"] == 450
        assert data["metadata"]["generation_time_ms"] == 1250
    
    @patch("app.api.routes.generate_treatment_summary")
    @patch("app.api.routes.log_generation")
    def test_generate_with_minimal_request(
        self,
        mock_log_generation,
        mock_generate,
        test_client,
        minimal_treatment_request,
        mock_openai_response,
    ):
        """Test generation with minimal request (all defaults)."""
        # Mock the service response
        mock_result = AsyncMock()
        mock_result.output = TreatmentSummaryOutput(**mock_openai_response)
        mock_result.tokens_used = 300
        mock_result.generation_time_ms = 1000
        mock_generate.return_value = mock_result
        
        mock_log_generation.return_value = AsyncMock()
        
        # Make request with empty body
        response = test_client.post(
            "/api/v1/generate-treatment-summary",
            json=minimal_treatment_request,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
    
    def test_generate_with_invalid_treatment_type(self, test_client):
        """Test that invalid treatment type returns 422."""
        invalid_request = {
            "treatment_type": "invalid_type",
        }
        
        response = test_client.post(
            "/api/v1/generate-treatment-summary",
            json=invalid_request,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_with_invalid_tone(self, test_client):
        """Test that invalid tone returns 422."""
        invalid_request = {
            "tone": "friendly",  # Not a valid tone
        }
        
        response = test_client.post(
            "/api/v1/generate-treatment-summary",
            json=invalid_request,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_with_invalid_patient_age(self, test_client):
        """Test that invalid patient age returns 422."""
        invalid_request = {
            "patient_age": 150,  # Over max age
        }
        
        response = test_client.post(
            "/api/v1/generate-treatment-summary",
            json=invalid_request,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch("app.api.routes.generate_treatment_summary")
    @patch("app.api.routes.log_generation")
    def test_generate_logs_error_on_failure(
        self,
        mock_log_generation,
        mock_generate,
        test_client,
        sample_treatment_request,
    ):
        """Test that errors are logged to audit database."""
        # Mock service to raise exception
        mock_generate.side_effect = Exception("OpenAI API timeout")
        mock_log_generation.return_value = AsyncMock()
        
        response = test_client.post(
            "/api/v1/generate-treatment-summary",
            json=sample_treatment_request,
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Verify error was logged
        assert mock_log_generation.called
        call_kwargs = mock_log_generation.call_args[1]
        assert call_kwargs["status"] == "error"
        assert "OpenAI API timeout" in call_kwargs["error_message"]


class TestPlaceholderEndpoints:
    """Test placeholder endpoints for future modules."""
    
    def test_insurance_summary_placeholder(self, test_client):
        """Test insurance summary placeholder endpoint."""
        response = test_client.post(
            "/api/v1/generate-insurance-summary",
            json={"patient_id": "test_patient"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Module coming soon"
        assert data["module"] == "insurance-summary"
    
    def test_progress_notes_placeholder(self, test_client):
        """Test progress notes placeholder endpoint."""
        response = test_client.post(
            "/api/v1/generate-progress-notes",
            json={"patient_id": "test_patient"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Module coming soon"
        assert data["module"] == "progress-notes"


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema_available(self, test_client):
        """Test that OpenAPI schema is available."""
        response = test_client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_swagger_ui_available(self, test_client):
        """Test that Swagger UI is available."""
        response = test_client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
    
    def test_redoc_available(self, test_client):
        """Test that ReDoc is available."""
        response = test_client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
