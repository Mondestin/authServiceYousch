#!/usr/bin/env python3
"""
Script to create database tables only (without seeding)
Useful for development when you want to create tables first, then seed later
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database
from app.core.logging import get_logger

logger = get_logger(__name__)

def main():
    """Main function to create tables only"""
    try:
        logger.info("Creating database tables only...")
        
        # Initialize database (create tables only)
        init_database()
        
        logger.info("✅ Database tables created successfully!")
        logger.info("Tables are ready. You can now:")
        logger.info("1. Run seeding: python scripts/seed_database.py")
        logger.info("2. Or run full setup: python scripts/setup.py")
        logger.info("3. Start the application: uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 