"""Initial authGhost schema

Revision ID: 001_initial_authghost_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_initial_authghost_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial authGhost schema tables"""
    
    # ==========================
    # 1. Organizations Table
    # ==========================
    op.create_table('organizations',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False, comment='Organization ID'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now() ON UPDATE now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        comment='Organizations table for multi-tenant support'
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)

    # ==========================
    # 2. Users Table
    # ==========================
    op.create_table('users',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False, comment='User ID'),
        sa.Column('org_id', mysql.BIGINT(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now() ON UPDATE now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        comment='Users table for authentication'
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_org_id'), 'users', ['org_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # ==========================
    # 3. Services Table
    # ==========================
    op.create_table('services',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False, comment='Service ID'),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', name='service_status'), nullable=False, server_default=sa.text("'active'")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        comment='Services table for microservices'
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)

    # ==========================
    # 4. Roles Table (Service-Specific)
    # ==========================
    op.create_table('roles',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('service_id', mysql.BIGINT(), nullable=False),
        sa.Column('permissions', mysql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_id', 'name', name='unique_service_role'),
        comment='Service-specific roles with JSON permissions'
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_service_id'), 'roles', ['service_id'], unique=False)

    # ==========================
    # 5. User Roles Table
    # ==========================
    op.create_table('user_roles',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('user_id', mysql.BIGINT(), nullable=False),
        sa.Column('role_id', mysql.BIGINT(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
        comment='Many-to-many relationship between users and roles'
    )
    op.create_index(op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=False)
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_roles_role_id'), 'user_roles', ['role_id'], unique=False)

    # ==========================
    # 6. Subscription Tiers Table (Service-Specific)
    # ==========================
    op.create_table('subscription_tiers',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('service_id', mysql.BIGINT(), nullable=False),
        sa.Column('tier_name', sa.String(length=50), nullable=False),
        sa.Column('features', mysql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_id', 'tier_name', name='unique_service_tier'),
        comment='Service-specific subscription tiers'
    )
    op.create_index(op.f('ix_subscription_tiers_id'), 'subscription_tiers', ['id'], unique=False)
    op.create_index(op.f('ix_subscription_tiers_service_id'), 'subscription_tiers', ['service_id'], unique=False)

    # ==========================
    # 7. Organization Subscriptions Table
    # ==========================
    op.create_table('organization_subscriptions',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('org_id', mysql.BIGINT(), nullable=False),
        sa.Column('service_id', mysql.BIGINT(), nullable=False),
        sa.Column('tier_id', mysql.BIGINT(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tier_id'], ['subscription_tiers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_id', 'service_id', name='unique_org_service'),
        comment='Organization subscriptions to services'
    )
    op.create_index(op.f('ix_organization_subscriptions_id'), 'organization_subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_organization_subscriptions_org_id'), 'organization_subscriptions', ['org_id'], unique=False)
    op.create_index(op.f('ix_organization_subscriptions_service_id'), 'organization_subscriptions', ['service_id'], unique=False)

    # ==========================
    # 8. Revoked Tokens Table (Optional)
    # ==========================
    op.create_table('revoked_tokens',
        sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('token_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', mysql.BIGINT(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Revoked JWT tokens for security'
    )
    op.create_index(op.f('ix_revoked_tokens_id'), 'revoked_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_revoked_tokens_token_id'), 'revoked_tokens', ['token_id'], unique=False)
    op.create_index(op.f('ix_revoked_tokens_user_id'), 'revoked_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop all authGhost schema tables"""
    
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('revoked_tokens')
    op.drop_table('organization_subscriptions')
    op.drop_table('subscription_tiers')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('services')
    op.drop_table('users')
    op.drop_table('organizations')
    
    # Drop the enum type
    op.execute('DROP TYPE IF EXISTS service_status')