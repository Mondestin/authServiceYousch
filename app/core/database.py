"""
Database configuration and utilities for the AuthService
Includes SQLAlchemy setup, connection pooling, and database utilities
"""

import time
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings
from app.core.logging import get_logger, log_database_operation

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Create declarative base for models
Base = declarative_base()


def create_database_engine() -> Engine:
    """
    Create and configure the database engine with connection pooling
    
    Returns:
        Engine: Configured SQLAlchemy engine
    """
    try:
        # Create engine with connection pooling
        # Add PyMySQL driver specification for MySQL URLs
        database_url = settings.database_url
        if database_url.startswith("mysql://") and "pymysql" not in database_url:
            database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
        
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
            echo=settings.debug,  # SQL logging in debug mode
        )
        
        # Add event listeners for connection monitoring
        @event.listens_for(engine, "connect")
        def set_mysql_settings(dbapi_connection, connection_record):
            """Set MySQL settings for better performance"""
            if "mysql" in settings.database_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("SET time_zone = '+00:00'")
                cursor.execute("SET character_set_connection = 'utf8mb4'")
                cursor.execute("SET character_set_client = 'utf8mb4'")
                cursor.execute("SET character_set_results = 'utf8mb4'")
                cursor.close()
        
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log database operations for performance monitoring"""
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log database operation completion and duration"""
            total = time.time() - conn.info['query_start_time'].pop(-1)
            
            # Extract table name from statement (basic parsing)
            table_name = "unknown"
            if "FROM" in statement.upper():
                parts = statement.upper().split("FROM")
                if len(parts) > 1:
                    table_part = parts[1].strip().split()[0]
                    table_name = table_part.strip("`\"'[]")
            
            # Determine operation type
            operation = "SELECT"
            if statement.upper().startswith("INSERT"):
                operation = "INSERT"
            elif statement.upper().startswith("UPDATE"):
                operation = "UPDATE"
            elif statement.upper().startswith("DELETE"):
                operation = "DELETE"
            elif statement.upper().startswith("CREATE"):
                operation = "CREATE"
            elif statement.upper().startswith("ALTER"):
                operation = "ALTER"
            elif statement.upper().startswith("DROP"):
                operation = "DROP"
            
            log_database_operation(
                operation=operation,
                table=table_name,
                duration=total,
                success=True
            )
        
        logger.info("Database engine created successfully", 
                   pool_size=settings.database_pool_size,
                   max_overflow=settings.database_max_overflow)
        
        return engine
        
    except Exception as e:
        logger.error("Failed to create database engine", error=str(e))
        raise


def create_database_session_factory(engine: Engine) -> sessionmaker:
    """
    Create a session factory for database sessions
    
    Args:
        engine: The database engine
        
    Returns:
        sessionmaker: Configured session factory
    """
    try:
        session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info("Database session factory created successfully")
        return session_factory
        
    except Exception as e:
        logger.error("Failed to create session factory", error=str(e))
        raise


def get_database_session() -> Generator[Session, None, None]:
    """
    Get a database session from the session factory
    
    Yields:
        Session: Database session
        
    Note:
        This function should be used as a dependency in FastAPI endpoints
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error("Database session error", error=str(e))
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    
    Yields:
        Session: Database session
        
    Example:
        with get_db_session() as session:
            result = session.execute(query)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error("Database session error", error=str(e))
        session.rollback()
        raise
    finally:
        session.close()


def test_database_connection(engine: Engine) -> bool:
    """
    Test database connectivity
    
    Args:
        engine: The database engine to test
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False


def close_database_connection(engine: Engine) -> None:
    """
    Close all database connections
    
    Args:
        engine: The database engine to close
    """
    try:
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error("Failed to close database connections", error=str(e))


def get_database_info(engine: Engine) -> dict:
    """
    Get database information and statistics
    
    Args:
        engine: The database engine
        
    Returns:
        dict: Database information
    """
    try:
        pool = engine.pool
        
        info = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
        
        logger.info("Database pool information retrieved", **info)
        return info
        
    except Exception as e:
        logger.error("Failed to get database info", error=str(e))
        return {}


# Create global engine and session factory
engine = create_database_engine()
SessionLocal = create_database_session_factory(engine)


def seed_database() -> None:
    """Seed database with initial data"""
    try:
        from app.models.organization import Organization
        from app.models.service import Service
        from app.models.role import Role
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Check if data already exists
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM organizations"))
                org_count = result.scalar()
                
                if org_count > 0:
                    logger.info("Database already has data, skipping seeding")
                    return
        except Exception as e:
            logger.warning(f"Could not check existing data: {e}")
            # Continue with seeding if table doesn't exist yet
        
        logger.info("Seeding database with initial data...")
        
        # Create default organization
        default_organization = Organization(
            name="Default Organization"
        )
        
        # Create default service
        default_service = Service(
            name="auth-service",
            description="Authentication service",
            status="active"
        )
        
        # Create default roles
        super_admin_role = Role(
            name="super_admin",
            service_id=1,  # Will be set after service is created
            permissions={"all": True}
        )
        
        org_admin_role = Role(
            name="org_admin",
            service_id=1,  # Will be set after service is created
            permissions={"org": {"read": True, "update": True, "users": True}}
        )
        
        service_admin_role = Role(
            name="service_admin",
            service_id=1,  # Will be set after service is created
            permissions={"service": {"read": True, "update": True, "roles": True}}
        )
        
        # Create default super admin user
        super_admin_user = User(
            org_id=1,  # Will be set after organization is created
            email="admin@default-org.com",
            password_hash=get_password_hash("admin123")
        )
        
        # Add all objects to session
        with SessionLocal() as db:
            try:
                # Add organization
                db.add(default_organization)
                db.commit()
                db.refresh(default_organization)
                logger.info(f"Added default organization: {default_organization.name}")
                
                # Add service
                db.add(default_service)
                db.commit()
                db.refresh(default_service)
                logger.info(f"Added default service: {default_service.name}")
                
                # Update role service_id references
                super_admin_role.service_id = default_service.id
                org_admin_role.service_id = default_service.id
                service_admin_role.service_id = default_service.id
                
                # Add roles
                db.add(super_admin_role)
                db.add(org_admin_role)
                db.add(service_admin_role)
                db.commit()
                logger.info("Added default roles")
                
                # Update user references
                super_admin_user.org_id = default_organization.id
                
                # Add user
                db.add(super_admin_user)
                db.commit()
                logger.info("Added super admin user")
                
                logger.info("Database seeded successfully with initial data")
                
            except Exception as e:
                logger.error(f"Failed to seed database during transaction: {e}")
                db.rollback()
                raise
        
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        # Don't raise here as seeding is not critical for operation


def init_database() -> None:
    """Initialize database using Alembic migrations"""
    try:
        import subprocess
        import os
        from pathlib import Path
        
        logger.info("Initializing database with Alembic migrations...")
        
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent
        
        # Change to project root directory
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        try:
            # Run alembic upgrade head
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Database migrations completed successfully!")
            logger.debug(f"Migration output: {result.stdout}")
            
            if result.stderr:
                logger.warning(f"Migration warnings: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Migration failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            raise Exception(f"Database migration failed: {e.stderr}")
        except FileNotFoundError:
            logger.error("Alembic not found. Please ensure Alembic is installed and available in PATH")
            raise Exception("Alembic not found")
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
        
        # Verify tables were created successfully
        logger.info("Verifying table creation...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Check for our specific tables
        required_tables = {'users', 'organizations', 'services', 'roles', 'user_roles', 'subscription_tiers', 'organization_subscriptions', 'revoked_tokens'}
        missing_tables = required_tables - set(existing_tables)
        
        if missing_tables:
            logger.error(f"Missing tables after migration: {missing_tables}")
            raise Exception(f"Tables not created by migration: {missing_tables}")
        
        logger.info("All required tables created successfully!")
        
        # Verify the created tables have correct schema
        try:
            with engine.connect() as connection:
                # Verify users table schema
                result = connection.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'id'
                """))
                column_info = result.fetchone()
                logger.info(f"Verified users.id column type: {column_info[0] if column_info else 'unknown'}")
                
                # Verify organizations table schema
                result = connection.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'organizations' AND column_name = 'id'
                """))
                column_info = result.fetchone()
                logger.info(f"Verified organizations.id column type: {column_info[0] if column_info else 'unknown'}")
                
        except Exception as e:
            logger.warning(f"Could not verify created table schemas: {e}")
        
        # Tables are now created via migrations, seeding is handled by migration 002
        logger.info("Database tables created successfully via migrations!")
            
    except Exception as e:
        logger.error("Failed to initialize database tables", error=str(e))
        raise


# Note: create_tables_individually() function removed - now using Alembic migrations
def _obsolete_create_tables_individually() -> None:
    """OBSOLETE: Create tables individually using raw SQL for MySQL compatibility"""
    try:
        logger.info("Creating tables individually with MySQL-compatible SQL...")
        
        # Create schools table
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS schools (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    domain VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_schools_code (code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created schools table")
            
            # Create campuses table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS campuses (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    school_id BIGINT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    address_street VARCHAR(255),
                    address_city VARCHAR(100),
                    address_postal VARCHAR(20),
                    address_country VARCHAR(100),
                    contact_email VARCHAR(255),
                    contact_phone VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    INDEX idx_campuses_school_id (school_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created campuses table")
            
            # Create permissions table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_permissions_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created permissions table")
            
            # Create roles table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS roles (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    school_id BIGINT,
                    campus_id BIGINT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    FOREIGN KEY (campus_id) REFERENCES campuses(id) ON DELETE CASCADE,
                    INDEX idx_roles_school_id (school_id),
                    INDEX idx_roles_campus_id (campus_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created roles table")
            
            # Create role_permissions table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role_id BIGINT NOT NULL,
                    permission_id BIGINT NOT NULL,
                    PRIMARY KEY (role_id, permission_id),
                    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created role_permissions table")
            
            # Create users table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    school_id BIGINT NOT NULL,
                    campus_id BIGINT,
                    role_id BIGINT NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    username VARCHAR(50),
                    phone VARCHAR(20),
                    hashed_password VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    date_of_birth DATETIME,
                    gender ENUM('male', 'female', 'other'),
                    profile_picture VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    failed_login_attempts INT DEFAULT 0,
                    locked_until DATETIME,
                    email_verification_token VARCHAR(255),
                    password_reset_token VARCHAR(255),
                    password_reset_expires DATETIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
                    FOREIGN KEY (campus_id) REFERENCES campuses(id) ON DELETE CASCADE,
                    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                    INDEX idx_users_school_id (school_id),
                    INDEX idx_users_campus_id (campus_id),
                    INDEX idx_users_role_id (role_id),
                    INDEX idx_users_email (email),
                    INDEX idx_users_username (username),
                    INDEX idx_users_phone (phone)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created users table")
            
            # Create sessions table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    session_token VARCHAR(255) NOT NULL UNIQUE,
                    refresh_token VARCHAR(255) NOT NULL UNIQUE,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    expires_at DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_sessions_user_id (user_id),
                    INDEX idx_sessions_session_token (session_token),
                    INDEX idx_sessions_refresh_token (refresh_token)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created sessions table")
            
            # Create login_history table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS login_history (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    ip_address VARCHAR(100),
                    device_info TEXT,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('success', 'failed') NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_login_history_user_id (user_id),
                    INDEX idx_login_history_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            logger.info("Created login_history table")
            
        logger.info("All tables created successfully using individual SQL statements")
        
    except Exception as e:
        logger.error(f"Failed to create tables individually: {e}")
        raise


def drop_database() -> None:
    """Drop all database tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error("Failed to drop database tables", error=str(e))
        raise 