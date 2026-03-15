"""initial_schema

Revision ID: 49700027aa7c
Revises:
Create Date: 2026-03-15 13:17:59.045335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '49700027aa7c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建班组表
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=True)

    # 创建班次类型表
    op.create_table(
        'shift_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('start_time', sa.String(10), nullable=False),
        sa.Column('end_time', sa.String(10), nullable=False),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('required_count', sa.Integer(), nullable=True, default=1),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shift_types_id'), 'shift_types', ['id'], unique=False)

    # 创建员工表
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('position', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('available_days', sqlite.JSON(), nullable=True),
        sa.Column('preferred_shifts', sqlite.JSON(), nullable=True),
        sa.Column('available_start_time', sa.String(10), nullable=True),
        sa.Column('available_end_time', sa.String(10), nullable=True),
        sa.Column('preference_note', sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)

    # 创建排班表
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('shift_type_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['shift_type_id'], ['shift_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schedules_id'), 'schedules', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_schedules_id'), table_name='schedules')
    op.drop_table('schedules')

    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_table('employees')

    op.drop_index(op.f('ix_shift_types_id'), table_name='shift_types')
    op.drop_table('shift_types')

    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
