"""Add first_name and last_name to users table

Revision ID: 003_add_user_names
Revises: 002_seed_initial_data
Create Date: 2024-01-01 00:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003_add_user_names'
down_revision = '002_seed_initial_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add first_name and last_name columns to users table"""
    
    # Add first_name column
    op.add_column('users', 
        sa.Column('first_name', sa.String(length=100), nullable=True, comment="User's first name")
    )
    
    # Add last_name column
    op.add_column('users', 
        sa.Column('last_name', sa.String(length=100), nullable=True, comment="User's last name")
    )


def downgrade() -> None:
    """Remove first_name and last_name columns from users table"""
    
    # Remove last_name column
    op.drop_column('users', 'last_name')
    
    # Remove first_name column
    op.drop_column('users', 'first_name')