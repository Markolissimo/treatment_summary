"""
Tests for database operations and audit logging.
"""

import pytest
from datetime import datetime
from sqlalchemy import select

from app.db.models import AuditLog
from app.db.audit import log_generation


class TestAuditLog:
    """Test AuditLog model."""
    
    @pytest.mark.asyncio
    async def test_create_audit_log(self, test_session):
        """Test creating an audit log entry."""
        audit_entry = AuditLog(
            user_id="test_user_001",
            document_type="treatment_summary",
            document_version="1.0",
            input_data='{"treatment_type": "clear aligners"}',
            generated_text='{"title": "Test Summary"}',
            model_used="gpt-4o",
            tokens_used=450,
            generation_time_ms=1250,
            status="success",
        )
        
        test_session.add(audit_entry)
        await test_session.commit()
        await test_session.refresh(audit_entry)
        
        assert audit_entry.id is not None
        assert audit_entry.user_id == "test_user_001"
        assert audit_entry.document_type == "treatment_summary"
        assert audit_entry.tokens_used == 450
        assert audit_entry.status == "success"
        assert isinstance(audit_entry.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_audit_log_with_error(self, test_session):
        """Test audit log entry with error."""
        audit_entry = AuditLog(
            user_id="test_user_002",
            document_type="treatment_summary",
            document_version="1.0",
            input_data='{"treatment_type": "clear aligners"}',
            generated_text="{}",
            model_used="gpt-4o",
            status="error",
            error_message="OpenAI API timeout",
        )
        
        test_session.add(audit_entry)
        await test_session.commit()
        await test_session.refresh(audit_entry)
        
        assert audit_entry.status == "error"
        assert audit_entry.error_message == "OpenAI API timeout"
        assert audit_entry.tokens_used is None
    
    @pytest.mark.asyncio
    async def test_query_audit_logs_by_user(self, test_session):
        """Test querying audit logs by user_id."""
        # Create multiple entries
        for i in range(3):
            audit_entry = AuditLog(
                user_id="test_user_003",
                document_type="treatment_summary",
                document_version="1.0",
                input_data="{}",
                generated_text="{}",
                model_used="gpt-4o",
                status="success",
            )
            test_session.add(audit_entry)
        
        await test_session.commit()
        
        # Query by user_id
        statement = select(AuditLog).where(AuditLog.user_id == "test_user_003")
        result = await test_session.execute(statement)
        logs = result.scalars().all()
        
        assert len(logs) == 3
        assert all(log.user_id == "test_user_003" for log in logs)
    
    @pytest.mark.asyncio
    async def test_query_audit_logs_by_document_type(self, test_session):
        """Test querying audit logs by document_type."""
        # Create entries with different types
        audit_entry1 = AuditLog(
            user_id="test_user_004",
            document_type="treatment_summary",
            document_version="1.0",
            input_data="{}",
            generated_text="{}",
            model_used="gpt-4o",
            status="success",
        )
        
        audit_entry2 = AuditLog(
            user_id="test_user_004",
            document_type="insurance_summary",
            document_version="1.0",
            input_data="{}",
            generated_text="{}",
            model_used="gpt-4o",
            status="success",
        )
        
        test_session.add(audit_entry1)
        test_session.add(audit_entry2)
        await test_session.commit()
        
        # Query by document_type
        statement = select(AuditLog).where(
            AuditLog.document_type == "treatment_summary"
        )
        result = await test_session.execute(statement)
        logs = result.scalars().all()
        
        assert all(log.document_type == "treatment_summary" for log in logs)


class TestLogGeneration:
    """Test log_generation utility function."""
    
    @pytest.mark.asyncio
    async def test_log_successful_generation(self, test_session):
        """Test logging a successful generation."""
        audit_entry = await log_generation(
            session=test_session,
            user_id="test_user_005",
            document_type="treatment_summary",
            input_data={"treatment_type": "clear aligners"},
            generated_text={"title": "Test Summary", "summary": "Test content"},
            model_used="gpt-4o",
            tokens_used=500,
            generation_time_ms=1500,
            status="success",
        )
        
        assert audit_entry.id is not None
        assert audit_entry.user_id == "test_user_005"
        assert audit_entry.tokens_used == 500
        assert audit_entry.generation_time_ms == 1500
        assert audit_entry.status == "success"
        assert audit_entry.error_message is None
    
    @pytest.mark.asyncio
    async def test_log_failed_generation(self, test_session):
        """Test logging a failed generation."""
        audit_entry = await log_generation(
            session=test_session,
            user_id="test_user_006",
            document_type="treatment_summary",
            input_data={"treatment_type": "clear aligners"},
            generated_text={},
            model_used="gpt-4o",
            status="error",
            error_message="API rate limit exceeded",
        )
        
        assert audit_entry.status == "error"
        assert audit_entry.error_message == "API rate limit exceeded"
        assert audit_entry.tokens_used is None
        assert audit_entry.generation_time_ms is None
    
    @pytest.mark.asyncio
    async def test_log_generation_with_defaults(self, test_session):
        """Test log_generation with default parameters."""
        audit_entry = await log_generation(
            session=test_session,
            user_id="test_user_007",
            document_type="treatment_summary",
            input_data={},
            generated_text={},
        )
        
        assert audit_entry.model_used == "gpt-4o"
        assert audit_entry.status == "success"
        assert audit_entry.document_version == "1.0"
    
    @pytest.mark.asyncio
    async def test_log_generation_persists_to_database(self, test_session):
        """Test that log_generation persists data to database."""
        await log_generation(
            session=test_session,
            user_id="test_user_008",
            document_type="treatment_summary",
            input_data={"test": "data"},
            generated_text={"test": "output"},
        )
        
        # Query to verify persistence
        statement = select(AuditLog).where(AuditLog.user_id == "test_user_008")
        result = await test_session.execute(statement)
        log = result.scalar_one()
        
        assert log is not None
        assert log.user_id == "test_user_008"
        assert '"test": "data"' in log.input_data
        assert '"test": "output"' in log.generated_text
