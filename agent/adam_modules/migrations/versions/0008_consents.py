"""consents (F12 consent gate, ETAP 25)

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-14 12:10:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'consents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('senior_id', sa.Integer(), nullable=False),
        sa.Column('consent_type', sa.Enum(
            'call_recording', 'health_processing', 'family_contact',
            'ai_disclosure', 'data_sharing', name='consenttype'), nullable=False),
        sa.Column('status', sa.Enum(
            'granted', 'withdrawn', 'expired', name='consentstatus'), nullable=False),
        sa.Column('legal_basis', sa.String(length=120), nullable=False),
        sa.Column('source', sa.String(length=120), nullable=True),
        sa.Column('actor', sa.String(length=120), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('withdrawn_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('consents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_consents_senior_id'), ['senior_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_consents_consent_type'), ['consent_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_consents_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_consents_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('consents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_consents_created_at'))
        batch_op.drop_index(batch_op.f('ix_consents_status'))
        batch_op.drop_index(batch_op.f('ix_consents_consent_type'))
        batch_op.drop_index(batch_op.f('ix_consents_senior_id'))
    op.drop_table('consents')
