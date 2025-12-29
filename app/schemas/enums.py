from enum import Enum

class TreatmentType(str, Enum):
    CLEAR_ALIGNERS = "clear aligners"
    TRADITIONAL_BRACES = "traditional braces"
    LINGUAL_BRACES = "lingual braces"
    RETAINERS = "retainers"

class AreaTreated(str, Enum):
    UPPER = "upper"
    LOWER = "lower"
    BOTH = "both"

class CaseDifficulty(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class MonitoringApproach(str, Enum):
    REMOTE = "remote"
    MIXED = "mixed"
    IN_CLINIC = "in-clinic"

class Attachments(str, Enum):
    NONE = "none"
    SOME = "some"
    EXTENSIVE = "extensive"

class Audience(str, Enum):
    PATIENT = "patient"
    INTERNAL = "internal"

class Tone(str, Enum):
    CONCISE = "concise"
    CASUAL = "casual"
    REASSURING = "reassuring"
    CLINICAL = "clinical"

class CaseTier(str, Enum):
    """Case tier for CDT code mapping."""
    EXPRESS = "express"
    MILD = "mild"
    MODERATE = "moderate"
    COMPLEX = "complex"

class AgeGroup(str, Enum):
    """Age group for CDT code mapping."""
    ADOLESCENT = "adolescent"
    ADULT = "adult"


class InsuranceTier(str, Enum):
    """Insurance tier for CDT code mapping.
    
    Note: Express and Mild are combined as 'express_mild' for insurance purposes
    since they both map to D8010 (limited orthodontic treatment).
    """
    EXPRESS_MILD = "express_mild"
    MODERATE = "moderate"
    COMPLEX = "complex"


class Arches(str, Enum):
    """Arches being treated."""
    UPPER = "upper"
    LOWER = "lower"
    BOTH = "both"
