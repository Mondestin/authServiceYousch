#!/usr/bin/env python3
"""
Script to run database migrations for authGhost
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
        logger.info("Migration output:")
        logger.info(result.stdout)
        
        if result.stderr:
            logger.warning("Migration warnings:")
            logger.warning(result.stderr)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration: {e}")
        sys.exit(1)

def create_migration(message: str):
    """Create a new migration"""
    try:
        logger.info(f"Creating new migration: {message}")
        
        # Change to project root directory
        os.chdir(project_root)
        
        # Run alembic revision
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("✅ Migration created successfully!")
        logger.info("Migration output:")
        logger.info(result.stdout)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Migration creation failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration creation: {e}")
        sys.exit(1)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            if len(sys.argv) > 2:
                message = sys.argv[2]
                create_migration(message)
            else:
                logger.error("Please provide a migration message")
                sys.exit(1)
        elif command == "upgrade":
            run_migrations()
        else:
            logger.error("Unknown command. Use 'create <message>' or 'upgrade'")
            sys.exit(1)
    else:
        # Default to running migrations
        run_migrations()

if __name__ == "__main__":
    main()