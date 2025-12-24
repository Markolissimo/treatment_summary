from typing import Literal


def get_patient_category(age: int | None) -> Literal["adolescent", "adult", "unknown"]:
    """
    Determine patient category based on age threshold.
    
    CDT Logic:
    - Adolescent: under 18
    - Adult: 18 and over
    
    Args:
        age: Patient age in years
        
    Returns:
        "adolescent", "adult", or "unknown" if age not provided
    """
    if age is None:
        return "unknown"
    
    return "adolescent" if age < 18 else "adult"
