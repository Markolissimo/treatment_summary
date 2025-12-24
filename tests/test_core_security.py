"""
Tests for core security module.
"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import get_current_user


class TestSecurity:
    """Test authentication and authorization."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test that no credentials returns dev user."""
        user_id = await get_current_user(credentials=None)
        assert user_id == "dev_user_001"
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_token(self):
        """Test that token is processed."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test_token_12345678"
        )
        
        user_id = await get_current_user(credentials=credentials)
        assert user_id.startswith("user_")
        assert "test_tok" in user_id
    
    @pytest.mark.asyncio
    async def test_get_current_user_returns_string(self):
        """Test that user_id is always a string."""
        user_id = await get_current_user(credentials=None)
        assert isinstance(user_id, str)
        assert len(user_id) > 0
