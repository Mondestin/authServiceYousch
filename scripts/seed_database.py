#!/usr/bin/env python3
"""
Script to seed database with initial data only
Assumes database tables already exist
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import seed_database
from app.core.logging import get_logger

logger = get_logger(__name__)

def main():
    """Main function to seed database only"""
    try:
        logger.info("Seeding database with initial data...")
        
        # Seed database with initial data
        seed_database()
        
        logger.info("Database seeded successfully!")
        logger.info("Initial data includes:")
        logger.info("- Default organization")
        logger.info("- Default service (auth-service)")
        logger.info("- Default roles (super_admin, org_admin, service_admin)")
        logger.info("- Super admin user (admin@default-org.com / admin123)")
        logger.info("\nYou can now start the application:")
        logger.info("uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 