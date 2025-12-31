"""
Tests for schema validation.
"""

import pytest
from pydantic import ValidationError

from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentSummaryOutput,
    TreatmentSummaryResponse,
    TreatmentType,
    AreaTreated,
    CaseDifficulty,
    MonitoringApproach,
    Attachments,
    Audience,
    Tone,
)


class TestTreatmentSummaryRequest:
    """Test treatment summary request schema."""
    
    def test_minimal_request_with_defaults(self):
        """Test that empty request uses defaults."""
        request = TreatmentSummaryRequest()
        
        assert request.treatment_type == TreatmentType.CLEAR_ALIGNERS
        assert request.area_treated == AreaTreated.BOTH
        assert request.duration_range == "4-6 months"
        assert request.case_difficulty == CaseDifficulty.MODERATE
        assert request.monitoring_approach == MonitoringApproach.MIXED
        assert request.attachments == Attachments.SOME
        assert request.whitening_included == False
        assert request.audience == Audience.PATIENT
        assert request.tone == Tone.REASSURING
    
    def test_full_request_with_patient_details(self):
        """Test request with all fields populated."""
        request = TreatmentSummaryRequest(
            patient_name="John Smith",
            practice_name="BiteSoft Orthodontics",
            patient_age=25,
            treatment_type=TreatmentType.TRADITIONAL_BRACES,
            area_treated=AreaTreated.UPPER,
            duration_range="12-18 months",
            case_difficulty=CaseDifficulty.COMPLEX,
            monitoring_approach=MonitoringApproach.IN_CLINIC,
            attachments=Attachments.EXTENSIVE,
            whitening_included=True,
            dentist_note="Patient has previous orthodontic history",
            audience=Audience.INTERNAL,
            tone=Tone.CLINICAL,
        )
        
        assert request.patient_name == "John Smith"
        assert request.practice_name == "BiteSoft Orthodontics"
        assert request.patient_age == 25
        assert request.treatment_type == TreatmentType.TRADITIONAL_BRACES
        assert request.tone == Tone.CLINICAL
    
    def test_invalid_treatment_type(self):
        """Test that invalid treatment type raises error."""
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(treatment_type="invalid_type")
    
    def test_invalid_tone(self):
        """Test that invalid tone raises error."""
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(tone="friendly")
    
    def test_patient_age_validation(self):
        """Test patient age validation."""
        # Valid ages
        request = TreatmentSummaryRequest(patient_age=0)
        assert request.patient_age == 0
        
        request = TreatmentSummaryRequest(patient_age=120)
        assert request.patient_age == 120
        
        # Invalid ages
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(patient_age=-1)
        
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(patient_age=121)
    
    def test_dentist_note_max_length(self):
        """Test dentist note max length validation."""
        # Valid note
        request = TreatmentSummaryRequest(dentist_note="A" * 500)
        assert len(request.dentist_note) == 500
        
        # Too long
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(dentist_note="A" * 501)
    
    def test_patient_name_max_length(self):
        """Test patient name max length validation."""
        # Valid name
        request = TreatmentSummaryRequest(patient_name="A" * 200)
        assert len(request.patient_name) == 200
        
        # Too long
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(patient_name="A" * 201)
    
    def test_duration_range_validation(self):
        """Test duration range validation."""
        # Valid
        request = TreatmentSummaryRequest(duration_range="6-8 months")
        assert request.duration_range == "6-8 months"
        
        # Too short
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(duration_range="")
        
        # Too long
        with pytest.raises(ValidationError):
            TreatmentSummaryRequest(duration_range="A" * 51)


class TestTreatmentSummaryOutput:
    """Test treatment summary output schema."""
    
    def test_valid_output(self):
        """Test valid output creation."""
        output = TreatmentSummaryOutput(
            title="Your Treatment Plan",
            summary="This is a summary of your treatment.",
        )
        
        assert output.title == "Your Treatment Plan"
        assert output.summary == "This is a summary of your treatment."


class TestTreatmentSummaryResponse:
    """Test treatment summary response wrapper."""
    
    def test_valid_response(self):
        """Test valid response creation."""
        output = TreatmentSummaryOutput(
            title="Title",
            summary="Summary",
        )
        
        response = TreatmentSummaryResponse(
            success=True,
            document=output,
            metadata={"tokens_used": 450, "generation_time_ms": 1250},
        )
        
        assert response.success is True
        assert response.document == output
        assert response.metadata["tokens_used"] == 450
    
    def test_response_default_success(self):
        """Test that success defaults to True."""
        output = TreatmentSummaryOutput(
            title="Title",
            summary="Summary",
        )
        
        response = TreatmentSummaryResponse(document=output)
        assert response.success is True
    
    def test_response_default_metadata(self):
        """Test that metadata defaults to empty dict."""
        output = TreatmentSummaryOutput(
            title="Title",
            summary="Summary",
        )
        
        response = TreatmentSummaryResponse(document=output)
        assert response.metadata == {}


class TestEnums:
    """Test enum definitions."""
    
    def test_treatment_type_enum(self):
        """Test TreatmentType enum values."""
        assert TreatmentType.CLEAR_ALIGNERS.value == "clear aligners"
        assert TreatmentType.TRADITIONAL_BRACES.value == "traditional braces"
        assert TreatmentType.LINGUAL_BRACES.value == "lingual braces"
        assert TreatmentType.RETAINERS.value == "retainers"
    
    def test_area_treated_enum(self):
        """Test AreaTreated enum values."""
        assert AreaTreated.UPPER.value == "upper"
        assert AreaTreated.LOWER.value == "lower"
        assert AreaTreated.BOTH.value == "both"
    
    def test_tone_enum(self):
        """Test Tone enum values."""
        assert Tone.CONCISE.value == "concise"
        assert Tone.CASUAL.value == "casual"
        assert Tone.REASSURING.value == "reassuring"
        assert Tone.CLINICAL.value == "clinical"
    
    def test_audience_enum(self):
        """Test Audience enum values."""
        assert Audience.PATIENT.value == "patient"
        assert Audience.INTERNAL.value == "internal"
