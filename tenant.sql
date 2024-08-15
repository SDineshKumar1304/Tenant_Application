USE Tenant;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS tenant_applications;
DROP TABLE IF EXISTS tenant_registrations;


-- Create the tenant_applications table
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

-- Create the tenant_registrations table
CREATE TABLE tenant_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_details VARCHAR(20) NOT NULL,
    employment_history TEXT,
    income DECIMAL(10, 2),
    rental_history TEXT,
    credit_score INT,
    aadhar VARCHAR(255),
    pan VARCHAR(255),
    income_certificate VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

