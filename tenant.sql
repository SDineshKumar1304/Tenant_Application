create database Tenant;
use tenant;

show tables;

CREATE TABLE tenant_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employment_history VARCHAR(255),
    income DECIMAL(10, 2),
    rental_history VARCHAR(255),
    credit_score INT,
    payment_history VARCHAR(255),
    outstanding_debts DECIMAL(10, 2),
    criminal_records VARCHAR(255),
    legal_issues VARCHAR(255),
    employment_verification VARCHAR(255),
    income_verification VARCHAR(255),
    personal_references VARCHAR(255),
    professional_references VARCHAR(255),
    result VARCHAR(50)
);

select * from tenant_applications;
DESCRIBE tenant_applications;
DELETE FROM tenant_applications
WHERE id NOT IN (1, 2, 3);


CREATE TABLE tenant_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employment_history VARCHAR(255),
    income DECIMAL(10, 2),
    rental_history VARCHAR(255),
    credit_score INT,
    payment_history VARCHAR(255),
    outstanding_debts DECIMAL(10, 2),
    criminal_records VARCHAR(255),
    legal_issues VARCHAR(255),
    employment_verification VARCHAR(255),
    income_verification VARCHAR(255),
    personal_references VARCHAR(255),
    professional_references VARCHAR(255),
    result VARCHAR(50)
);

select * from tenant_applications;
DESCRIBE tenant_applications;
DELETE FROM tenant_applications
WHERE id NOT IN (1, 2, 3);



CREATE TABLE tenant_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_details VARCHAR(20) NOT NULL,
    employment_history TEXT,
    income DECIMAL(10, 2),
    rental_history TEXT,
    credit_score INT,
    aadhar VARCHAR(255),  -- Path to uploaded Aadhaar document
    pan VARCHAR(255),     -- Path to uploaded PAN document
    income_certificate VARCHAR(255),  -- Path to uploaded income certificate
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

select * from tenant_registrations;

SHOW COLUMNS FROM tenant_registrations;

CREATE TABLE tenant_credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('tenant', 'admin') DEFAULT 'tenant',
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

