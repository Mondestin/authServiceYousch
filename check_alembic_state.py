#!/usr/bin/env python3
"""
Script to check and fix Alembic state
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from sqlalchemy import text

def check_alembic_state():
    """Check and fix Alembic state"""
    try:
        with engine.connect() as connection:
            # Check current version in alembic_version table
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                print(f"📋 Current version in alembic_version: {version[0]}")
            else:
                print("❌ No version found in alembic_version table")
                return
            
            # Check if all tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name IN ('organizations', 'users', 'services', 'roles', 'user_roles', 
                                  'subscription_tiers', 'organization_subscriptions', 'revoked_tokens')
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            required_tables = {'organizations', 'users', 'services', 'roles', 'user_roles', 
                             'subscription_tiers', 'organization_subscriptions', 'revoked_tokens'}
            
            print(f"📋 Existing tables: {existing_tables}")
            
            if required_tables.issubset(set(existing_tables)):
                print("✅ All required tables exist")
                
                # Check if we have data
                result = connection.execute(text("SELECT COUNT(*) FROM organizations"))
                org_count = result.fetchone()[0]
                
                if org_count > 0:
                    print("✅ Data exists, database is complete")
                    print("🔧 The issue is that Alembic is not recognizing the current state")
                    print("💡 Solution: Use 'alembic stamp head' to mark the database as up-to-date")
                else:
                    print("⚠️  Tables exist but no data found")
            else:
                missing_tables = required_tables - set(existing_tables)
                print(f"❌ Missing tables: {missing_tables}")
                
    except Exception as e:
        print(f"❌ Error checking Alembic state: {e}")

if __name__ == "__main__":
    check_alembic_state()