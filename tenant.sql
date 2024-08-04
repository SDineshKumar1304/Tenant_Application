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
