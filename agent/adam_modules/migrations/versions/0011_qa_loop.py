"""qa loop F16 (ETAP 30): qa_evaluations, manual_audits, improvement_items,
sentiment_readings, decision_telemetry

Revision ID: 0011
Revises: 0010
Create Date: 2026-07-14 13:10:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'qa_evaluations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('senior_id', sa.Integer(), nullable=True),
        sa.Column('conversation_ref', sa.String(length=120), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('flags', sa.Text(), nullable=True),
        sa.Column('metrics', sa.Text(), nullable=True),
        sa.Column('needs_review', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('qa_evaluations', schema=None) as b:
        b.create_index(b.f('ix_qa_evaluations_senior_id'), ['senior_id'], unique=False)
        b.create_index(b.f('ix_qa_evaluations_conversation_ref'), ['conversation_ref'], unique=False)
        b.create_index(b.f('ix_qa_evaluations_needs_review'), ['needs_review'], unique=False)
        b.create_index(b.f('ix_qa_evaluations_created_at'), ['created_at'], unique=False)

    op.create_table(
        'manual_audits',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('evaluation_id', sa.Integer(), nullable=True),
        sa.Column('senior_id', sa.Integer(), nullable=True),
        sa.Column('conversation_ref', sa.String(length=120), nullable=True),
        sa.Column('auditor', sa.String(length=120), nullable=False),
        sa.Column('verdict', sa.Enum('ok', 'minor_issues', 'major_issues', 'unsafe', name='auditverdict'), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['evaluation_id'], ['qa_evaluations.id'], ),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('manual_audits', schema=None) as b:
        b.create_index(b.f('ix_manual_audits_evaluation_id'), ['evaluation_id'], unique=False)
        b.create_index(b.f('ix_manual_audits_senior_id'), ['senior_id'], unique=False)
        b.create_index(b.f('ix_manual_audits_conversation_ref'), ['conversation_ref'], unique=False)
        b.create_index(b.f('ix_manual_audits_verdict'), ['verdict'], unique=False)
        b.create_index(b.f('ix_manual_audits_created_at'), ['created_at'], unique=False)

    op.create_table(
        'improvement_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_audit_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=240), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('open', 'in_progress', 'resolved', 'dismissed', name='improvementstatus'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default=sa.text('3')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_audit_id'], ['manual_audits.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('improvement_items', schema=None) as b:
        b.create_index(b.f('ix_improvement_items_source_audit_id'), ['source_audit_id'], unique=False)
        b.create_index(b.f('ix_improvement_items_category'), ['category'], unique=False)
        b.create_index(b.f('ix_improvement_items_status'), ['status'], unique=False)
        b.create_index(b.f('ix_improvement_items_created_at'), ['created_at'], unique=False)

    op.create_table(
        'sentiment_readings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('senior_id', sa.Integer(), nullable=False),
        sa.Column('conversation_ref', sa.String(length=120), nullable=True),
        sa.Column('label', sa.Enum('crisis', 'distressed', 'neutral', 'content', 'happy', name='moodlabel'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('source', sa.String(length=48), nullable=False, server_default='text'),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('sentiment_readings', schema=None) as b:
        b.create_index(b.f('ix_sentiment_readings_senior_id'), ['senior_id'], unique=False)
        b.create_index(b.f('ix_sentiment_readings_conversation_ref'), ['conversation_ref'], unique=False)
        b.create_index(b.f('ix_sentiment_readings_label'), ['label'], unique=False)
        b.create_index(b.f('ix_sentiment_readings_created_at'), ['created_at'], unique=False)

    op.create_table(
        'decision_telemetry',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('senior_id', sa.Integer(), nullable=True),
        sa.Column('conversation_ref', sa.String(length=120), nullable=True),
        sa.Column('decision', sa.Enum('EXECUTE', 'DEFER', 'ESCALATE', 'ABSTAIN', name='decisionkind'), nullable=False),
        sa.Column('level', sa.String(length=16), nullable=True),
        sa.Column('trigger', sa.String(length=64), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('voters', sa.Text(), nullable=True),
        sa.Column('escalated_112', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('emergency_call_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['senior_id'], ['seniors.id'], ),
        sa.ForeignKeyConstraint(['emergency_call_id'], ['emergency_calls.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('decision_telemetry', schema=None) as b:
        b.create_index(b.f('ix_decision_telemetry_senior_id'), ['senior_id'], unique=False)
        b.create_index(b.f('ix_decision_telemetry_conversation_ref'), ['conversation_ref'], unique=False)
        b.create_index(b.f('ix_decision_telemetry_decision'), ['decision'], unique=False)
        b.create_index(b.f('ix_decision_telemetry_escalated_112'), ['escalated_112'], unique=False)
        b.create_index(b.f('ix_decision_telemetry_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('decision_telemetry')
    op.drop_table('sentiment_readings')
    op.drop_table('improvement_items')
    op.drop_table('manual_audits')
    op.drop_table('qa_evaluations')
