"""
Tests for services module (OpenAI integration).
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.openai_service import (
    build_treatment_summary_user_prompt,
    generate_treatment_summary,
    GenerationResult,
)
from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentSummaryOutput,
)


class TestBuildUserPrompt:
    """Test user prompt construction."""
    
    def test_build_prompt_with_minimal_request(self):
        """Test prompt building with minimal request (defaults)."""
        request = TreatmentSummaryRequest()
        prompt = build_treatment_summary_user_prompt(request)
        
        assert "Generate a treatment summary" in prompt
        assert "clear aligners" in prompt
        assert "both" in prompt
        assert "4-6 months" in prompt
        assert "moderate" in prompt
        assert "patient" in prompt
        assert "reassuring" in prompt
    
    def test_build_prompt_with_patient_details(self):
        """Test prompt includes patient details when provided."""
        request = TreatmentSummaryRequest(
            patient_name="John Smith",
            practice_name="BiteSoft Orthodontics",
            patient_age=25,
        )
        prompt = build_treatment_summary_user_prompt(request)
        
        assert "John Smith" in prompt
        assert "BiteSoft Orthodontics" in prompt
        assert "25" in prompt
        assert "adult" in prompt  # Age category
    
    def test_build_prompt_with_adolescent_age(self):
        """Test prompt includes adolescent category for age < 18."""
        request = TreatmentSummaryRequest(patient_age=16)
        prompt = build_treatment_summary_user_prompt(request)
        
        assert "16" in prompt
        assert "adolescent" in prompt
    
    def test_build_prompt_with_dentist_note(self):
        """Test prompt includes dentist note when provided."""
        request = TreatmentSummaryRequest(
            dentist_note="Patient is highly motivated"
        )
        prompt = build_treatment_summary_user_prompt(request)
        
        assert "Patient is highly motivated" in prompt
        assert "Dentist Note" in prompt
    
    def test_build_prompt_without_optional_fields(self):
        """Test prompt without optional fields."""
        request = TreatmentSummaryRequest()
        prompt = build_treatment_summary_user_prompt(request)
        
        # Should not contain patient-specific fields
        assert "Patient Name" not in prompt
        assert "Practice Name" not in prompt
        assert "Patient Age" not in prompt
        assert "Dentist Note" not in prompt
    
    def test_build_prompt_format(self):
        """Test that prompt is properly formatted."""
        request = TreatmentSummaryRequest()
        prompt = build_treatment_summary_user_prompt(request)
        
        # Check for markdown-style formatting
        assert "**Treatment Type:**" in prompt
        assert "**Area Treated:**" in prompt
        assert "**Target Audience:**" in prompt
        assert "**Desired Tone:**" in prompt
        
        # Check for final instruction
        assert "following all guidelines and restrictions" in prompt


class TestGenerateTreatmentSummary:
    """Test treatment summary generation."""
    
    @pytest.mark.asyncio
    @patch("app.services.openai_service.AsyncOpenAI")
    async def test_generate_treatment_summary_success(self, mock_openai_class):
        """Test successful treatment summary generation."""
        # Mock OpenAI client and response
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_output = TreatmentSummaryOutput(
            title="Your Treatment Plan",
            summary="This is a test summary.",
            key_points=["Point 1", "Point 2"],
            next_steps=["Step 1", "Step 2"],
        )
        
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = mock_output
        mock_response.usage.total_tokens = 450
        
        # Add async delay to simulate API call time
        async def mock_parse(*args, **kwargs):
            await asyncio.sleep(0.01)  # 10ms delay
            return mock_response

        mock_client.beta.chat.completions.parse = mock_parse
        
        # Generate summary
        request = TreatmentSummaryRequest()
        result = await generate_treatment_summary(request)
        
        # Verify result
        assert isinstance(result, GenerationResult)
        assert result.output == mock_output
        assert result.tokens_used == 450
        assert result.generation_time_ms > 0
    
    @pytest.mark.asyncio
    @patch("app.services.openai_service.AsyncOpenAI")
    async def test_generate_with_custom_api_key(self, mock_openai_class):
        """Test generation with custom API key."""
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_output = TreatmentSummaryOutput(
            title="Test",
            summary="Test",
            key_points=["Test"],
            next_steps=["Test"],
        )
        
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = mock_output
        mock_response.usage.total_tokens = 100
        
        mock_client.beta.chat.completions.parse.return_value = mock_response
        
        # Generate with custom key
        request = TreatmentSummaryRequest()
        custom_key = "sk-custom-test-key"
        await generate_treatment_summary(request, api_key=custom_key)
        
        # Verify custom key was used
        mock_openai_class.assert_called_once_with(api_key=custom_key)
    
    @pytest.mark.asyncio
    @patch("app.services.openai_service.AsyncOpenAI")
    async def test_generate_calls_openai_with_correct_params(self, mock_openai_class):
        """Test that OpenAI is called with correct parameters."""
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_output = TreatmentSummaryOutput(
            title="Test",
            summary="Test",
            key_points=["Test"],
            next_steps=["Test"],
        )
        
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = mock_output
        mock_response.usage.total_tokens = 100
        
        mock_client.beta.chat.completions.parse.return_value = mock_response
        
        # Generate summary
        request = TreatmentSummaryRequest(tone="clinical")
        await generate_treatment_summary(request)
        
        # Verify OpenAI was called
        assert mock_client.beta.chat.completions.parse.called
        call_kwargs = mock_client.beta.chat.completions.parse.call_args[1]
        
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 2000
        assert call_kwargs["response_format"] == TreatmentSummaryOutput
        
        # Verify messages structure
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
    
    @pytest.mark.asyncio
    @patch("app.services.openai_service.AsyncOpenAI")
    async def test_generate_measures_time(self, mock_openai_class):
        """Test that generation time is measured."""
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_output = TreatmentSummaryOutput(
            title="Test",
            summary="Test",
            key_points=["Test"],
            next_steps=["Test"],
        )
        
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = mock_output
        mock_response.usage.total_tokens = 100
        
        async def mock_parse(*args, **kwargs):
            await asyncio.sleep(0.01)
            return mock_response
        mock_client.beta.chat.completions.parse = mock_parse
        
        # Generate summary
        request = TreatmentSummaryRequest()
        result = await generate_treatment_summary(request)
        
        # Verify time was measured
        assert result.generation_time_ms > 0
        assert isinstance(result.generation_time_ms, int)
    
    @pytest.mark.asyncio
    @patch("app.services.openai_service.AsyncOpenAI")
    async def test_generate_handles_missing_usage(self, mock_openai_class):
        """Test handling when usage data is missing."""
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_output = TreatmentSummaryOutput(
            title="Test",
            summary="Test",
            key_points=["Test"],
            next_steps=["Test"],
        )
        
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = mock_output
        mock_response.usage = None  # No usage data
        
        mock_client.beta.chat.completions.parse.return_value = mock_response
        
        # Generate summary
        request = TreatmentSummaryRequest()
        result = await generate_treatment_summary(request)
        
        # Should default to 0
        assert result.tokens_used == 0


class TestGenerationResult:
    """Test GenerationResult model."""
    
    def test_generation_result_creation(self):
        """Test creating a GenerationResult."""
        output = TreatmentSummaryOutput(
            title="Test",
            summary="Test summary",
            key_points=["Point 1"],
            next_steps=["Step 1"],
        )
        
        result = GenerationResult(
            output=output,
            tokens_used=450,
            generation_time_ms=1250,
        )
        
        assert result.output == output
        assert result.tokens_used == 450
        assert result.generation_time_ms == 1250
    
    def test_generation_result_types(self):
        """Test GenerationResult field types."""
        output = TreatmentSummaryOutput(
            title="Test",
            summary="Test",
            key_points=["Test"],
            next_steps=["Test"],
        )
        
        result = GenerationResult(
            output=output,
            tokens_used=100,
            generation_time_ms=500,
        )
        
        assert isinstance(result.output, TreatmentSummaryOutput)
        assert isinstance(result.tokens_used, int)
        assert isinstance(result.generation_time_ms, int)
