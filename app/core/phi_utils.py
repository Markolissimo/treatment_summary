"""Utilities for handling PHI (Protected Health Information) redaction."""

import json
import hashlib
from typing import Any, Dict
from app.core.config import get_settings

settings = get_settings()


def redact_phi_from_dict(data: Dict[str, Any], fields_to_redact: list[str]) -> Dict[str, Any]:
    """
    Redact specified PHI fields from a dictionary.
    
    Args:
        data: Dictionary containing potentially sensitive data
        fields_to_redact: List of field names to redact
        
    Returns:
        Dictionary with PHI fields redacted
    """
    if not fields_to_redact:
        return data
    
    redacted = data.copy()
    
    for field in fields_to_redact:
        if field in redacted and redacted[field] is not None:
            # Replace with hash for audit trail purposes
            original_value = str(redacted[field])
            redacted[field] = f"[REDACTED:{hashlib.sha256(original_value.encode()).hexdigest()[:8]}]"
    
    return redacted


def prepare_audit_data(data: Dict[str, Any]) -> str:
    """
    Prepare data for audit logging based on PHI redaction settings.
    
    Args:
        data: Dictionary to be stored in audit log
        
    Returns:
        JSON string of the data (redacted if configured)
    """
    if settings.redact_phi_fields:
        redacted_data = redact_phi_from_dict(data, settings.phi_fields_list)
        return json.dumps(redacted_data)
    
    if settings.store_full_audit_data:
        return json.dumps(data)
    
    # If neither full storage nor redaction is enabled, store minimal data
    return json.dumps({
        "stored": False,
        "reason": "Full audit data storage disabled",
        "timestamp": data.get("timestamp", "unknown")
    })


def should_store_full_data() -> bool:
    """
    Check if full audit data should be stored.
    
    Returns:
        bool: True if full data storage is enabled
    """
    return settings.store_full_audit_data
