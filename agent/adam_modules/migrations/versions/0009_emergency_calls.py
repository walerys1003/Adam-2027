"""emergency_calls (F15 112, ETAP 26)

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-14 12:40:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'emergency_calls',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('senior_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=False),
        sa.Column('semaphore_level', sa.String(length=16), nullable=False),
        sa.Column('status', sa.Enum(
            'initiated', 'dispatched', 'connected', 'failed', 'simulated',
            name='emergencystatus'), nullable=False),
        sa.Column('channel_id', sa.String(length=120), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('audio_script', sa.Text(), nullable=True),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('emergency_calls', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_emergency_calls_senior_id'), ['senior_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_emergency_calls_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_emergency_calls_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('emergency_calls', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_emergency_calls_created_at'))
        batch_op.drop_index(batch_op.f('ix_emergency_calls_status'))
        batch_op.drop_index(batch_op.f('ix_emergency_calls_senior_id'))
    op.drop_table('emergency_calls')
