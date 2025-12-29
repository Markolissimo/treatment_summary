"""Admin panel for managing CDT codes and rules using sqladmin."""

from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog, CDTCode, CDTRule, DocumentConfirmation
from app.services.cdt_validation import validate_cdt_rule


class AuditLogAdmin(ModelView, model=AuditLog):
    """Admin view for audit logs."""

    name = "Audit Log"
    name_plural = "Audit Logs"
    icon = "fa-solid fa-clipboard-list"

    # Columns to display in list view
    column_list = [
        AuditLog.id,
        AuditLog.user_id,
        AuditLog.document_type,
        AuditLog.status,
        AuditLog.created_at,
        AuditLog.seed,
        AuditLog.is_regenerated,
    ]

    # Columns searchable
    column_searchable_list = [AuditLog.user_id, AuditLog.document_type]

    # Columns sortable
    column_sortable_list = [
        AuditLog.created_at,
        AuditLog.user_id,
        AuditLog.document_type,
        AuditLog.status,
    ]

    # Default sort
    column_default_sort = [(AuditLog.created_at, True)]

    # Read-only (audit logs should not be edited)
    can_create = False
    can_edit = False
    can_delete = False


class CDTCodeAdmin(ModelView, model=CDTCode):
    """Admin view for CDT codes."""

    name = "CDT Code"
    name_plural = "CDT Codes"
    icon = "fa-solid fa-code"

    # Columns to display in list view
    column_list = [
        CDTCode.code,
        CDTCode.description,
        CDTCode.category,
        CDTCode.is_primary,
        CDTCode.is_active,
    ]

    # Columns searchable
    column_searchable_list = [CDTCode.code, CDTCode.description]

    # Columns sortable
    column_sortable_list = [
        CDTCode.code,
        CDTCode.category,
        CDTCode.is_primary,
        CDTCode.is_active,
    ]

    # Default sort
    column_default_sort = [(CDTCode.code, False)]

    # Form configuration
    form_columns = [
        CDTCode.code,
        CDTCode.description,
        CDTCode.category,
        CDTCode.is_primary,
        CDTCode.is_active,
        CDTCode.notes,
    ]


class CDTRuleAdmin(ModelView, model=CDTRule):
    """Admin view for CDT mapping rules with validation."""

    name = "CDT Rule"
    name_plural = "CDT Rules"
    icon = "fa-solid fa-gears"

    # Columns to display in list view
    column_list = [
        CDTRule.tier,
        CDTRule.age_group,
        CDTRule.cdt_code,
        CDTRule.priority,
        CDTRule.is_active,
    ]

    # Columns searchable
    column_searchable_list = [CDTRule.tier, CDTRule.age_group, CDTRule.cdt_code]

    # Columns sortable
    column_sortable_list = [
        CDTRule.tier,
        CDTRule.age_group,
        CDTRule.cdt_code,
        CDTRule.priority,
        CDTRule.is_active,
    ]

    # Default sort (by priority descending)
    column_default_sort = [(CDTRule.priority, True)]

    # Form configuration
    form_columns = [
        CDTRule.tier,
        CDTRule.age_group,
        CDTRule.cdt_code,
        CDTRule.priority,
        CDTRule.is_active,
        CDTRule.notes,
    ]
    
    async def on_model_change(self, data: dict, model: CDTRule, is_created: bool, session: AsyncSession) -> None:
        """Validate CDT rule before saving."""
        # Validate tier, age_group, and cdt_code
        await validate_cdt_rule(
            session=session,
            tier=data.get("tier", model.tier),
            age_group=data.get("age_group", model.age_group),
            cdt_code=data.get("cdt_code", model.cdt_code),
        )


class DocumentConfirmationAdmin(ModelView, model=DocumentConfirmation):
    """Admin view for document confirmations."""

    name = "Document Confirmation"
    name_plural = "Document Confirmations"
    icon = "fa-solid fa-check-circle"

    # Columns to display in list view
    column_list = [
        DocumentConfirmation.id,
        DocumentConfirmation.generation_id,
        DocumentConfirmation.user_id,
        DocumentConfirmation.document_type,
        DocumentConfirmation.confirmed_at,
    ]

    # Columns searchable
    column_searchable_list = [
        DocumentConfirmation.generation_id,
        DocumentConfirmation.user_id,
        DocumentConfirmation.document_type,
    ]

    # Columns sortable
    column_sortable_list = [
        DocumentConfirmation.confirmed_at,
        DocumentConfirmation.user_id,
        DocumentConfirmation.document_type,
    ]

    # Default sort
    column_default_sort = [(DocumentConfirmation.confirmed_at, True)]

    # Read-only (confirmations should not be edited after creation)
    can_create = False
    can_edit = False
    can_delete = False


def setup_admin(app, engine):
    """
    Set up the admin panel.

    Args:
        app: FastAPI application instance
        engine: SQLAlchemy engine

    Returns:
        Admin instance
    """
    admin = Admin(app, engine, title="BiteSoft AI Admin")

    # Register admin views
    admin.add_view(AuditLogAdmin)
    admin.add_view(CDTCodeAdmin)
    admin.add_view(CDTRuleAdmin)
    admin.add_view(DocumentConfirmationAdmin)

    return admin
