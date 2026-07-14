"""conversation_summaries (F7 pamięć długoterminowa, ETAP 28)

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-14 13:10:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversation_summaries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('senior_id', sa.Integer(), nullable=False),
        sa.Column('conversation_ref', sa.String(length=120), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('mood', sa.String(length=32), nullable=True),
        sa.Column('max_level', sa.String(length=16), nullable=True),
        sa.Column('topics', sa.Text(), nullable=True),
        sa.Column('turn_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('conversation_summaries', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_conversation_summaries_senior_id'), ['senior_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_conversation_summaries_conversation_ref'), ['conversation_ref'], unique=False)
        batch_op.create_index(batch_op.f('ix_conversation_summaries_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('conversation_summaries', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conversation_summaries_created_at'))
        batch_op.drop_index(batch_op.f('ix_conversation_summaries_conversation_ref'))
        batch_op.drop_index(batch_op.f('ix_conversation_summaries_senior_id'))
    op.drop_table('conversation_summaries')
