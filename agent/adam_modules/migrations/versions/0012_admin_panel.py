"""admin panel (ETAP 35): fleet_units, admin_models, admin_providers, admin_logs

Revision ID: 0012
Revises: 0011
Create Date: 2026-07-14 15:40:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'fleet_units',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('region', sa.String(length=64), nullable=False, server_default='eu-central'),
        sa.Column('status', sa.Enum('online', 'degraded', 'offline', 'maintenance', name='fleetstatus'), nullable=False, server_default='offline'),
        sa.Column('active_calls', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default=sa.text('50')),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fleet_units_code', 'fleet_units', ['code'], unique=True)
    op.create_index('ix_fleet_units_status', 'fleet_units', ['status'], unique=False)

    op.create_table(
        'admin_models',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kind', sa.Enum('asr', 'llm', 'tts', name='modelkind'), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('status', sa.Enum('active', 'standby', 'disabled', name='modelstatus'), nullable=False, server_default='standby'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('params_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_admin_models_kind', 'admin_models', ['kind'], unique=False)
    op.create_index('ix_admin_models_status', 'admin_models', ['status'], unique=False)

    op.create_table(
        'admin_providers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('kind', sa.Enum('sms', 'email', 'push', 'asr', 'llm', 'tts', 'telephony', name='providerkind'), nullable=False),
        sa.Column('display_name', sa.String(length=120), nullable=False),
        sa.Column('state', sa.Enum('configured', 'missing_secrets', 'disabled', name='providerstate'), nullable=False, server_default='missing_secrets'),
        sa.Column('required_env', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_admin_providers_key', 'admin_providers', ['key'], unique=True)
    op.create_index('ix_admin_providers_kind', 'admin_providers', ['kind'], unique=False)

    op.create_table(
        'admin_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('level', sa.Enum('debug', 'info', 'warning', 'error', 'critical', name='loglevel'), nullable=False, server_default='info'),
        sa.Column('source', sa.String(length=64), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('actor', sa.String(length=120), nullable=True),
        sa.Column('meta_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_admin_logs_level', 'admin_logs', ['level'], unique=False)
    op.create_index('ix_admin_logs_source', 'admin_logs', ['source'], unique=False)
    op.create_index('ix_admin_logs_created_at', 'admin_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_admin_logs_created_at', table_name='admin_logs')
    op.drop_index('ix_admin_logs_source', table_name='admin_logs')
    op.drop_index('ix_admin_logs_level', table_name='admin_logs')
    op.drop_table('admin_logs')
    op.drop_index('ix_admin_providers_kind', table_name='admin_providers')
    op.drop_index('ix_admin_providers_key', table_name='admin_providers')
    op.drop_table('admin_providers')
    op.drop_index('ix_admin_models_status', table_name='admin_models')
    op.drop_index('ix_admin_models_kind', table_name='admin_models')
    op.drop_table('admin_models')
    op.drop_index('ix_fleet_units_status', table_name='fleet_units')
    op.drop_index('ix_fleet_units_code', table_name='fleet_units')
    op.drop_table('fleet_units')
