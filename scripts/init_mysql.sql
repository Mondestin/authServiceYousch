-- MySQL Database Initialization Script for AuthService
-- This script creates the database and user for the AuthService

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

-- Show created database and user
SHOW DATABASES LIKE 'auth_db';
SELECT User, Host FROM mysql.user WHERE User = 'auth_user'; 