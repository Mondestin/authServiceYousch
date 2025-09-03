-- MySQL Database Initialization Script for authGhost API
-- This script creates the database and user for the authGhost API

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS authghost_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user if it doesn't exist
CREATE USER IF NOT EXISTS 'authghost_user'@'%' IDENTIFIED BY 'authghost_password';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON authghost_db.* TO 'authghost_user'@'%';

-- Grant additional privileges for development
GRANT CREATE, DROP, ALTER, INDEX ON authghost_db.* TO 'authghost_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Use the database
USE authghost_db;

-- Show created database and user
SHOW DATABASES LIKE 'authghost_db';
SELECT User, Host FROM mysql.user WHERE User = 'authghost_user'; 