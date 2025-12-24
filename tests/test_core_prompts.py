"""
Tests for core prompts module.
"""

import pytest
from app.core.prompts import (
    TREATMENT_SUMMARY_SYSTEM_PROMPT,
    INSURANCE_SUMMARY_SYSTEM_PROMPT,
    PROGRESS_NOTES_SYSTEM_PROMPT,
)


class TestSystemPrompts:
    """Test system prompts contain required guardrails."""
    
    def test_treatment_summary_prompt_exists(self):
        """Test that treatment summary prompt is defined."""
        assert TREATMENT_SUMMARY_SYSTEM_PROMPT
        assert isinstance(TREATMENT_SUMMARY_SYSTEM_PROMPT, str)
        assert len(TREATMENT_SUMMARY_SYSTEM_PROMPT) > 100
    
    def test_treatment_prompt_has_guardrails(self):
        """Test that prompt contains hard restrictions."""
        prompt = TREATMENT_SUMMARY_SYSTEM_PROMPT.lower()
        
        # Check for guardrail keywords
        assert "diagnosis" in prompt or "malocclusion" in prompt
        assert "guarantee" in prompt or "promise" in prompt
        assert "financial" in prompt or "pricing" in prompt or "cost" in prompt
    
    def test_treatment_prompt_has_tone_guidance(self):
        """Test that prompt mentions tone adaptation."""
        prompt = TREATMENT_SUMMARY_SYSTEM_PROMPT.lower()
        
        assert "tone" in prompt or "style" in prompt
        assert "concise" in prompt or "casual" in prompt or "reassuring" in prompt
    
    def test_treatment_prompt_has_audience_guidance(self):
        """Test that prompt mentions audience adaptation."""
        prompt = TREATMENT_SUMMARY_SYSTEM_PROMPT.lower()
        
        assert "audience" in prompt or "patient" in prompt
    
    def test_placeholder_prompts_exist(self):
        """Test that placeholder prompts are defined."""
        assert INSURANCE_SUMMARY_SYSTEM_PROMPT
        assert PROGRESS_NOTES_SYSTEM_PROMPT
        assert isinstance(INSURANCE_SUMMARY_SYSTEM_PROMPT, str)
        assert isinstance(PROGRESS_NOTES_SYSTEM_PROMPT, str)
    
    def test_prompt_no_harmful_content(self):
        """Test that prompts don't contain harmful instructions."""
        prompt = TREATMENT_SUMMARY_SYSTEM_PROMPT.lower()
        
        # Should not encourage violations
        assert "ignore" not in prompt or "ignore previous" not in prompt
        assert "disregard" not in prompt or "disregard restrictions" not in prompt
