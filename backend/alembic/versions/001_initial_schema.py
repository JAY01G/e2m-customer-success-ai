"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-24 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'CUSTOMER_SUCCESS_MANAGER', 'VIEWER', name='user_role'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'AT_RISK', 'CHURNED', 'PROSPECT', name='customer_status'), nullable=False),
        sa.Column('health_score', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Uuid(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('health_score >= 0 AND health_score <= 100', name='check_health_score_range'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_company_name'), 'customers', ['company_name'], unique=False)
    op.create_index(op.f('ix_customers_health_score'), 'customers', ['health_score'], unique=False)
    op.create_index(op.f('ix_customers_name'), 'customers', ['name'], unique=False)
    op.create_index(op.f('ix_customers_owner_id'), 'customers', ['owner_id'], unique=False)
    op.create_index(op.f('ix_customers_status'), 'customers', ['status'], unique=False)

    # Interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('customer_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('type', sa.Enum('MEETING', 'CALL', 'EMAIL', 'DEMO', 'OTHER', name='interaction_type'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('meeting_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interactions_customer_id'), 'interactions', ['customer_id'], unique=False)
    op.create_index(op.f('ix_interactions_meeting_date'), 'interactions', ['meeting_date'], unique=False)
    op.create_index(op.f('ix_interactions_type'), 'interactions', ['type'], unique=False)
    op.create_index(op.f('ix_interactions_user_id'), 'interactions', ['user_id'], unique=False)

    # AI Insights table
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('interaction_id', sa.Uuid(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('sentiment', sa.Enum('Positive', 'Neutral', 'Negative', name='sentiment_type'), nullable=False),
        sa.Column('action_items', sa.JSON(), nullable=False),
        sa.Column('risks', sa.JSON(), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('generation_status', sa.Enum('SUCCESS', 'FAILED', 'FALLBACK', name='generation_status'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interaction_id'], ['interactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_insights_interaction_id'), 'ai_insights', ['interaction_id'], unique=True)


def downgrade() -> None:
    op.drop_table('ai_insights')
    op.drop_table('interactions')
    op.drop_table('customers')
    op.drop_table('users')
