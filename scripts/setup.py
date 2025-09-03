#!/usr/bin/env python3
"""
Setup script for authGhost API
Runs database migrations and seeds initial data
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.logging import get_logger

logger = get_logger(__name__)

def run_migrations():
    """Run database migrations"""
    try:
        logger.info("Running database migrations...")
        
        # Change to project root directory
        os.chdir(project_root)
        
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("✅ Migrations completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration: {e}")
        return False

def main():
    """Main setup function"""
    try:
        logger.info("Starting authGhost API setup...")
        
        # Step 1: Run database migrations
        logger.info("Step 1: Running database migrations...")
        if not run_migrations():
            logger.error("Migration failed, aborting setup")
            sys.exit(1)
        
        logger.info("🎉 Setup completed successfully!")
        logger.info("Initial data includes:")
        logger.info("- Default organization")
        logger.info("- Default service (auth-service)")
        logger.info("- Default roles (super_admin, org_admin, service_admin)")
        logger.info("- Default subscription tiers (basic, premium, enterprise)")
        logger.info("- Super admin user (admin@default-org.com / admin123)")
        logger.info("- Default organization subscription (enterprise tier)")
        logger.info("\nYou can now start the application with:")
        logger.info("uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 