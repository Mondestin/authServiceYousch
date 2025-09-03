#!/usr/bin/env python3
"""
Script to run database migrations only (without seeding)
Useful for development when you want to create tables first, then seed later
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
    """Main function to create tables only"""
    try:
        logger.info("Creating database tables only (using migrations)...")
        
        # Run migrations to create tables
        if not run_migrations():
            logger.error("Migration failed, aborting")
            sys.exit(1)
        
        logger.info("✅ Database tables created successfully!")
        logger.info("Tables are ready. You can now:")
        logger.info("1. Run full setup with data: python scripts/setup.py")
        logger.info("2. Start the application: uvicorn app.main:app --reload")
        logger.info("3. Access API docs: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 