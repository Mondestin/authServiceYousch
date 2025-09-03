-- MySQL Database Initialization Script for AuthService
-- This script creates the database and tables for the new AuthService schema

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if it doesn't exist
CREATE USER IF NOT EXISTS 'auth_user'@'%' IDENTIFIED BY 'auth_password';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON auth_db.* TO 'auth_user'@'%';

-- Grant additional privileges for development
GRANT CREATE, DROP, ALTER, INDEX ON auth_db.* TO 'auth_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Use the database
USE auth_db;

-- ==========================
-- 1. Organizations Table
-- ==========================
CREATE TABLE organizations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==========================
-- 2. Users Table
-- ==========================
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- ==========================
-- 3. Services Table
-- ==========================
CREATE TABLE services (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    status ENUM('active','inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================
-- 4. Roles Table (Service-Specific)
-- ==========================
CREATE TABLE roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    service_id BIGINT NOT NULL,
    permissions JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, name),
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- ==========================
-- 5. User Roles Table
-- ==========================
CREATE TABLE user_roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- ==========================
-- 6. Subscription Tiers Table (Service-Specific)
-- ==========================
CREATE TABLE subscription_tiers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service_id BIGINT NOT NULL,
    tier_name VARCHAR(50) NOT NULL,
    features JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_id, tier_name),
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- ==========================
-- 7. Organization Subscriptions Table
-- ==========================
CREATE TABLE organization_subscriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    org_id BIGINT NOT NULL,
    service_id BIGINT NOT NULL,
    tier_id BIGINT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, service_id),
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES subscription_tiers(id) ON DELETE CASCADE
);

-- ==========================
-- 8. Revoked Tokens Table (Optional)
-- ==========================
CREATE TABLE revoked_tokens (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    token_id VARCHAR(255) NOT NULL,
    user_id BIGINT NOT NULL,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_users_org_id ON users(org_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_roles_service_id ON roles(service_id);
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_subscription_tiers_service_id ON subscription_tiers(service_id);
CREATE INDEX idx_organization_subscriptions_org_id ON organization_subscriptions(org_id);
CREATE INDEX idx_organization_subscriptions_service_id ON organization_subscriptions(service_id);
CREATE INDEX idx_revoked_tokens_token_id ON revoked_tokens(token_id);
CREATE INDEX idx_revoked_tokens_user_id ON revoked_tokens(user_id);

-- Show created tables
SHOW TABLES;