"""
Tests for core utility functions.
"""

import pytest
from app.core.utils import get_patient_category


class TestPatientCategory:
    """Test age threshold logic for CDT."""
    
    def test_adolescent_category(self):
        """Test adolescent category (under 18)."""
        assert get_patient_category(0) == "adolescent"
        assert get_patient_category(5) == "adolescent"
        assert get_patient_category(12) == "adolescent"
        assert get_patient_category(17) == "adolescent"
    
    def test_adult_category(self):
        """Test adult category (18 and over)."""
        assert get_patient_category(18) == "adult"
        assert get_patient_category(25) == "adult"
        assert get_patient_category(45) == "adult"
        assert get_patient_category(100) == "adult"
    
    def test_unknown_category(self):
        """Test unknown category (None age)."""
        assert get_patient_category(None) == "unknown"
    
    def test_boundary_values(self):
        """Test boundary values around age 18."""
        assert get_patient_category(17) == "adolescent"
        assert get_patient_category(18) == "adult"
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert get_patient_category(0) == "adolescent"  # Newborn
        assert get_patient_category(120) == "adult"     # Very old
