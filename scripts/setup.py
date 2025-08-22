#!/usr/bin/env python3
"""
Simple setup script for AuthService
Creates database tables and initial data
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database, seed_database
from app.core.logging import get_logger

logger = get_logger(__name__)

def main():
    """Main setup function"""
    try:
        logger.info("Starting AuthService setup...")
        
        # Step 1: Initialize database (create tables only)
        logger.info("Step 1: Creating database tables...")
        init_database()
        logger.info("✅ Database tables created successfully")
        
        # Step 2: Seed database with initial data
        logger.info("Step 2: Seeding database with initial data...")
        seed_database()
        logger.info("✅ Database seeded successfully")
        
        logger.info("🎉 Setup completed successfully!")
        logger.info("You can now start the application with:")
        logger.info("uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 