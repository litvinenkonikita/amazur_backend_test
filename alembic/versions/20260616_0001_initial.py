"""initial schema

Revision ID: 20260616_0001
Revises: None
Create Date: 2026-06-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260616_0001"
down_revision = None
branch_labels = None
depends_on = None


campaign_status = sa.Enum("active", "paused", name="campaign_status")


def upgrade() -> None:
    campaign_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "campaigns",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("current_status", campaign_status, nullable=False, server_default="active"),
        sa.Column("target_status", campaign_status, nullable=False, server_default="active"),
        sa.Column("is_managed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("budget_limit", sa.Numeric(12, 2), nullable=True),
        sa.Column("spend_today", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("stock_days_left", sa.Integer(), nullable=True),
        sa.Column("stock_days_min", sa.Integer(), nullable=True),
        sa.Column("schedule_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=False), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "campaign_schedules",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_campaign_schedules_day_of_week"),
        sa.CheckConstraint("end_time > start_time", name="ck_campaign_schedules_time_range"),
    )
    op.create_index("ix_campaign_schedules_campaign_id", "campaign_schedules", ["campaign_id"], unique=False)

    op.create_table(
        "rule_evaluation_logs",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("triggered_rule", sa.String(length=64), nullable=True),
        sa.Column("previous_target", campaign_status, nullable=False),
        sa.Column("new_target", campaign_status, nullable=False),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=False), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rule_evaluation_logs_campaign_id", "rule_evaluation_logs", ["campaign_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rule_evaluation_logs_campaign_id", table_name="rule_evaluation_logs")
    op.drop_table("rule_evaluation_logs")
    op.drop_index("ix_campaign_schedules_campaign_id", table_name="campaign_schedules")
    op.drop_table("campaign_schedules")
    op.drop_table("campaigns")
    campaign_status.drop(op.get_bind(), checkfirst=True)
