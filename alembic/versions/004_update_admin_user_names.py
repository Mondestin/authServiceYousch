"""Update admin user with first_name and last_name

Revision ID: 004_update_admin_user_names
Revises: 003_add_user_names
Create Date: 2024-01-01 00:04:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_update_admin_user_names'
down_revision = '003_add_user_names'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update admin user with first_name and last_name"""
    
    # Update the admin user with first_name and last_name
    op.execute("""
        UPDATE users 
        SET first_name = 'Super', last_name = 'Admin'
        WHERE email = 'admin@default-org.com'
    """)


def downgrade() -> None:
    """Remove first_name and last_name from admin user"""
    
    # Clear the first_name and last_name for admin user
    op.execute("""
        UPDATE users 
        SET first_name = NULL, last_name = NULL
        WHERE email = 'admin@default-org.com'
    """)