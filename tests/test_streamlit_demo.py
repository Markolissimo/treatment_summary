"""
Tests for Streamlit demo application.

Note: These are basic import and structure tests.
Full UI testing would require Streamlit testing framework.
"""

import pytest
import sys
from pathlib import Path


class TestStreamlitDemo:
    """Test Streamlit demo application."""
    
    def test_streamlit_demo_file_exists(self):
        """Test that streamlit_demo.py exists."""
        demo_file = Path("streamlit_demo.py")
        assert demo_file.exists(), "streamlit_demo.py should exist"
    
    def test_streamlit_demo_imports(self):
        """Test that demo file has required imports."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        # Check for required imports
        assert "import streamlit" in content
        assert "import requests" in content
        assert "import json" in content
    
    def test_streamlit_demo_has_api_base_url(self):
        """Test that demo has API base URL configured."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        assert "API_BASE_URL" in content
        assert "localhost:8000" in content or "127.0.0.1:8000" in content
    
    def test_streamlit_demo_has_page_config(self):
        """Test that demo has page configuration."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        assert "st.set_page_config" in content
        assert "page_title" in content
    
    def test_streamlit_demo_has_input_fields(self):
        """Test that demo has input fields for case data."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        # Check for key input fields
        assert "treatment_type" in content
        assert "patient_age" in content
        assert "tone" in content
        assert "audience" in content
    
    def test_streamlit_demo_has_generate_button(self):
        """Test that demo has generate button."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        assert "st.button" in content
        assert "Generate" in content or "generate" in content
    
    def test_streamlit_demo_makes_api_calls(self):
        """Test that demo makes API calls."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        assert "requests.post" in content
        assert "/api/v1/generate-treatment-summary" in content
    
    def test_streamlit_demo_has_error_handling(self):
        """Test that demo has error handling."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        assert "try:" in content or "except" in content
        assert "st.error" in content
    
    def test_streamlit_demo_has_documentation(self):
        """Test that demo has documentation/about section."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        # Should have docstring or about section
        assert '"""' in content or "About" in content or "ℹ️" in content
    
    def test_streamlit_demo_is_optional(self):
        """Test that demo is documented as optional."""
        demo_file = Path("streamlit_demo.py")
        content = demo_file.read_text(encoding="utf-8")
        
        # Should mention it's optional/demo
        content_lower = content.lower()
        assert "optional" in content_lower or "demo" in content_lower


class TestStreamlitDemoRequirements:
    """Test Streamlit demo requirements file."""
    
    def test_demo_requirements_file_exists(self):
        """Test that requirements-demo.txt exists."""
        req_file = Path("requirements-demo.txt")
        assert req_file.exists(), "requirements-demo.txt should exist"
    
    def test_demo_requirements_has_streamlit(self):
        """Test that demo requirements includes streamlit."""
        req_file = Path("requirements-demo.txt")
        content = req_file.read_text(encoding="utf-8")
        
        assert "streamlit" in content.lower()
    
    def test_demo_requirements_has_requests(self):
        """Test that demo requirements includes requests."""
        req_file = Path("requirements-demo.txt")
        content = req_file.read_text(encoding="utf-8")
        
        assert "requests" in content.lower()
    
    def test_demo_requirements_is_separate(self):
        """Test that demo requirements is separate from main requirements."""
        main_req = Path("requirements.txt")
        demo_req = Path("requirements-demo.txt")
        
        main_content = main_req.read_text(encoding="utf-8")
        
        # Main requirements should NOT have streamlit
        assert "streamlit" not in main_content.lower()
