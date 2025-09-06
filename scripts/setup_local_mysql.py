#!/usr/bin/env python3
"""
Local MySQL setup script for AuthGhost API
Helps set up the database and user for local development
"""

import subprocess
import sys
import getpass
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed:")
        print(f"   Error: {e.stderr}")
        return None

def check_mysql_connection():
    """Check if MySQL is running and accessible"""
    print("[INFO] Checking MySQL connection...")
    
    # Try to connect to MySQL
    result = run_command("mysql --version", "Checking MySQL version")
    if not result:
        print("[ERROR] MySQL is not accessible. Please ensure MySQL is running.")
        return False
    
    print("[SUCCESS] MySQL is accessible")
    return True

def create_database_and_user():
    """Create database and user for AuthGhost API"""
    print("\n[INFO] Setting up database and user...")
    
    # Get MySQL root password
    root_password = getpass.getpass("Enter MySQL root password (or press Enter if none): ")
    
    if root_password:
        mysql_auth = f"-uroot -p{root_password}"
    else:
        mysql_auth = "-uroot"
    
    # Create database
    create_db_sql = """
    CREATE DATABASE IF NOT EXISTS authghost_db 
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """
    
    result = run_command(f'echo "{create_db_sql}" | mysql {mysql_auth}', "Creating database")
    if not result:
        return False
    
    # Create user
    create_user_sql = """
    CREATE USER IF NOT EXISTS 'authghost_user'@'localhost' IDENTIFIED BY 'authghost_password';
    GRANT ALL PRIVILEGES ON authghost_db.* TO 'authghost_user'@'localhost';
    FLUSH PRIVILEGES;
    """
    
    result = run_command(f'echo "{create_user_sql}" | mysql {mysql_auth}', "Creating user")
    if not result:
        return False
    
    print("[SUCCESS] Database and user created successfully")
    return True

def update_env_file():
    """Update .env file with local MySQL settings"""
    print("\n[INFO] Updating environment file...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("[ERROR] .env file not found. Please copy env.example to .env first.")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update DATABASE_URL for local MySQL
    if "DATABASE_URL=" in content:
        # Replace with local MySQL URL
        new_content = content.replace(
            "DATABASE_URL=mysql://root:your_mysql_root_password@localhost:3306/auth_db",
            "DATABASE_URL=mysql://auth_user:auth_password@localhost:3306/auth_db"
        )
        
        with open(env_file, 'w') as f:
            f.write(new_content)
        
        print("[SUCCESS] Updated .env file with local MySQL settings")
        return True
    else:
        print("[ERROR] DATABASE_URL not found in .env file")
        return False

def main():
    """Main setup function"""
    print("AuthService Local MySQL Setup")
    print("=" * 40)
    
    # Check if MySQL is accessible
    if not check_mysql_connection():
        print("\n[ERROR] Setup failed. Please ensure MySQL is running and accessible.")
        sys.exit(1)
    
    # Create database and user
    if not create_database_and_user():
        print("\n[ERROR] Setup failed. Could not create database or user.")
        sys.exit(1)
    
    # Update environment file
    if not update_env_file():
        print("\n[WARNING] Could not update .env file. Please update manually:")
        print("   DATABASE_URL=mysql://auth_user:auth_password@localhost:3306/auth_db")
    
    print("\n[SUCCESS] Setup completed successfully!")
    print("\nNext steps:")
    print("1. Install Python dependencies: pip install -r requirements.txt")
    print("2. Run database initialization: python scripts/setup.py")
    print("3. Start the application: uvicorn app.main:app --reload")
    print("\nDefault credentials:")
    print("   Database: auth_db")
    print("   Username: auth_user")
    print("   Password: auth_password")

if __name__ == "__main__":
    main() 