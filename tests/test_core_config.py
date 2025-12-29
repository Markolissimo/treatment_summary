"""
Tests for core configuration module.
"""

import pytest
from app.core.config import get_settings, Settings


class TestSettings:
    """Test configuration settings."""
    
    def test_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    def test_settings_has_required_fields(self):
        """Test that settings has all required fields."""
        settings = get_settings()
        
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "app_version")
        assert hasattr(settings, "debug")
        assert hasattr(settings, "openai_api_key")
        assert hasattr(settings, "openai_model")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "secret_key")
        assert hasattr(settings, "algorithm")
        assert hasattr(settings, "access_token_expire_minutes")
    
    def test_default_values(self):
        """Test default configuration values."""
        settings = get_settings()
        
        assert settings.app_name == "BiteSoft AI Document Generation System"
        assert settings.app_version == "0.2.0"
        assert settings.openai_model == "gpt-4o"
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
    
    def test_settings_types(self):
        """Test that settings have correct types."""
        settings = get_settings()
        
        assert isinstance(settings.app_name, str)
        assert isinstance(settings.app_version, str)
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.openai_api_key, str)
        assert isinstance(settings.openai_model, str)
        assert isinstance(settings.database_url, str)
        assert isinstance(settings.secret_key, str)
        assert isinstance(settings.algorithm, str)
        assert isinstance(settings.access_token_expire_minutes, int)
