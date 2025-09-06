"""Seed initial AuthGhost data

Revision ID: 002_seed_initial_data
Revises: 001_initial_authghost_schema
Create Date: 2024-01-01 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import mysql
from datetime import datetime, date
import json

# revision identifiers, used by Alembic.
revision = '002_seed_initial_data'
down_revision = '001_initial_authghost_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed initial data for AuthGhost"""
    
    # Create table references for data insertion
    organizations_table = table('organizations',
        column('id', mysql.BIGINT()),
        column('name', sa.String(255)),
        column('created_at', sa.DateTime(timezone=True)),
        column('updated_at', sa.DateTime(timezone=True))
    )
    
    services_table = table('services',
        column('id', mysql.BIGINT()),
        column('name', sa.String(100)),
        column('description', sa.String(255)),
        column('status', sa.Enum('active', 'inactive', name='service_status')),
        column('created_at', sa.DateTime(timezone=True))
    )
    
    roles_table = table('roles',
        column('id', mysql.BIGINT()),
        column('name', sa.String(50)),
        column('service_id', mysql.BIGINT()),
        column('permissions', mysql.JSON()),
        column('created_at', sa.DateTime(timezone=True))
    )
    
    users_table = table('users',
        column('id', mysql.BIGINT()),
        column('org_id', mysql.BIGINT()),
        column('email', sa.String(255)),
        column('password_hash', sa.String(255)),
        column('is_active', sa.Boolean()),
        column('created_at', sa.DateTime(timezone=True)),
        column('updated_at', sa.DateTime(timezone=True)),
        column('last_login', sa.DateTime(timezone=True))
    )
    
    subscription_tiers_table = table('subscription_tiers',
        column('id', mysql.BIGINT()),
        column('service_id', mysql.BIGINT()),
        column('tier_name', sa.String(50)),
        column('features', mysql.JSON()),
        column('created_at', sa.DateTime(timezone=True))
    )
    
    organization_subscriptions_table = table('organization_subscriptions',
        column('id', mysql.BIGINT()),
        column('org_id', mysql.BIGINT()),
        column('service_id', mysql.BIGINT()),
        column('tier_id', mysql.BIGINT()),
        column('start_date', sa.Date()),
        column('end_date', sa.Date()),
        column('is_active', sa.Boolean()),
        column('created_at', sa.DateTime(timezone=True))
    )
    
    # Insert default organization
    op.bulk_insert(organizations_table, [
        {
            'id': 1,
            'name': 'Default Organization',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ])
    
    # Insert default service
    op.bulk_insert(services_table, [
        {
            'id': 1,
            'name': 'auth-service',
            'description': 'Authentication service',
            'status': 'active',
            'created_at': datetime.now()
        }
    ])
    
    # Insert default roles
    op.bulk_insert(roles_table, [
        {
            'id': 1,
            'name': 'super_admin',
            'service_id': 1,
            'permissions': {"all": True},
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'name': 'org_admin',
            'service_id': 1,
            'permissions': {"org": {"read": True, "update": True, "users": True}},
            'created_at': datetime.now()
        },
        {
            'id': 3,
            'name': 'service_admin',
            'service_id': 1,
            'permissions': {"service": {"read": True, "update": True, "roles": True}},
            'created_at': datetime.now()
        }
    ])
    
    # Insert default subscription tiers
    op.bulk_insert(subscription_tiers_table, [
        {
            'id': 1,
            'service_id': 1,
            'tier_name': 'basic',
            'features': {
                "max_users": 10,
                "api_calls_per_month": 1000,
                "features": ["authentication", "basic_rbac"]
            },
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'service_id': 1,
            'tier_name': 'premium',
            'features': {
                "max_users": 100,
                "api_calls_per_month": 10000,
                "features": ["authentication", "advanced_rbac", "subscription_management"]
            },
            'created_at': datetime.now()
        },
        {
            'id': 3,
            'service_id': 1,
            'tier_name': 'enterprise',
            'features': {
                "max_users": -1,  # unlimited
                "api_calls_per_month": -1,  # unlimited
                "features": ["authentication", "advanced_rbac", "subscription_management", "custom_roles", "audit_logs"]
            },
            'created_at': datetime.now()
        }
    ])
    
    # Insert default super admin user (password: admin123)
    # Note: This is a bcrypt hash for 'admin123'
    admin_password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2'
    
    op.bulk_insert(users_table, [
        {
            'id': 1,
            'org_id': 1,
            'email': 'admin@default-org.com',
            'password_hash': admin_password_hash,
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'last_login': None
        }
    ])
    
    # Insert default organization subscription
    op.bulk_insert(organization_subscriptions_table, [
        {
            'id': 1,
            'org_id': 1,
            'service_id': 1,
            'tier_id': 3,  # enterprise tier
            'start_date': date.today(),
            'end_date': date(2025, 12, 31),
            'is_active': True,
            'created_at': datetime.now()
        }
    ])


def downgrade() -> None:
    """Remove seeded data"""
    
    # Delete in reverse order to handle foreign key constraints
    op.execute("DELETE FROM organization_subscriptions WHERE id = 1")
    op.execute("DELETE FROM users WHERE id = 1")
    op.execute("DELETE FROM subscription_tiers WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM roles WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM services WHERE id = 1")
    op.execute("DELETE FROM organizations WHERE id = 1")