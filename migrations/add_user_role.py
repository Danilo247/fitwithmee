"""Add role field to User model

Revision ID: add_user_role
Create Date: 2024-03-19 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add role column with default value
    op.add_column('user', sa.Column('role', sa.String(20), nullable=False, server_default='customer'))

def downgrade():
    # Remove role column
    op.drop_column('user', 'role') 