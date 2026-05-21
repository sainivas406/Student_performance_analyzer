CREATE DATABASE spa_enhanced_db;

USE spa_enhanced_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE COLLATE utf8mb4_general_ci,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','faculty','student') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    marks FLOAT CHECK (marks >= 0 AND marks <= 100),
    user_id INT,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE USER 'spa_admin'@'localhost'
IDENTIFIED BY 'admin123';

GRANT ALL PRIVILEGES
ON spa_enhanced_db.*
TO 'spa_admin'@'localhost';

CREATE USER 'spa_faculty'@'localhost'
IDENTIFIED BY 'faculty123';

GRANT SELECT, INSERT, UPDATE
ON spa_enhanced_db.*
TO 'spa_faculty'@'localhost';

CREATE USER 'spa_student'@'localhost'
IDENTIFIED BY 'student123';

GRANT SELECT
ON spa_enhanced_db.*
TO 'spa_student'@'localhost';