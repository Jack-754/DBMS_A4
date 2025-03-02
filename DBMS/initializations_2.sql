-- VILLAGE TABLE (Independent)
CREATE TABLE IF NOT EXISTS village (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- HOUSEHOLD TABLE (Independent)
CREATE TABLE IF NOT EXISTS households (
    id SERIAL PRIMARY KEY,
    primary_residence VARCHAR(100) NOT NULL,
    head_of_household INT UNIQUE -- Ensures only one head per household
);

-- CITIZENS TABLE (Depends on VILLAGE and HOUSEHOLDS)
CREATE TABLE IF NOT EXISTS citizens (
    id SERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
    phone VARCHAR(10) NOT NULL CHECK (phone ~ '^[0-9]{10}$'),
    household_id INT,
    educational_qualification TEXT NOT NULL CHECK (
        educational_qualification IN ('Illiterate', 'Primary', 'Secondary', '10th', '12th', 'Graduate', 'Post-Graduate')
    ),
    mother_id INT,
    father_id INT,
    village_id INT NOT NULL,
    FOREIGN KEY (mother_id) REFERENCES citizens(id) ON DELETE SET NULL,
    FOREIGN KEY (father_id) REFERENCES citizens(id) ON DELETE SET NULL,
    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE SET NULL,
    FOREIGN KEY (village_id) REFERENCES village(id) ON DELETE CASCADE
);


-- USERS TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    pswd VARCHAR(255) NOT NULL, -- Increased length for hashed passwords
    user_type TEXT NOT NULL CHECK (user_type IN ('CITIZEN', 'GOVERNMENT_MONITOR', 'PANCHAYAT_EMPLOYEES', 'SYSTEM_ADMINISTRATOR')),
    citizen_id INT,
    CONSTRAINT citizen_id_required CHECK (
        (user_type IN ('USER', 'PANCHAYAT_EMPLOYEES') AND citizen_id IS NOT NULL) OR
        (user_type IN ('SYSTEM_ADMINISTRATOR') AND citizen_id IS NULL)
    ),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- TAX FILING TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS tax_filing (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT unique_tax_filing_per_year UNIQUE (citizen_id, filing_date),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);


-- INCOME DECLARATIONS TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS income_declarations (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    source VARCHAR(50) NOT NULL,
    CONSTRAINT unique_income_declaration_per_year UNIQUE (citizen_id, source, filing_date),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- CERTIFICATES TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS certificates (
    certificate_no SERIAL PRIMARY KEY,
    cert_type VARCHAR(50) NOT NULL,
    citizen_issued INT NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (citizen_issued) REFERENCES citizens(id) ON DELETE CASCADE
);

-- ASSETS TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS assets (
    asset_id SERIAL PRIMARY KEY,
    asset_type VARCHAR(50) NOT NULL,
    date_of_registration DATE NOT NULL DEFAULT CURRENT_DATE,
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES citizens(id) ON DELETE CASCADE
);


-- PANCHAYAT EMPLOYEES TABLE (Depends on CITIZENS and VILLAGE)
CREATE TABLE IF NOT EXISTS panchayat_employees (
    citizen_id INT PRIMARY KEY NOT NULL UNIQUE,
    position VARCHAR(50) NOT NULL CHECK (position IN ('PRADHAN', 'MEMBER')),
    salary INT CHECK (salary > 0),
    village_id INT NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE,
    FOREIGN KEY (village_id) REFERENCES village(id) ON DELETE CASCADE
);

-- Enforce that only one 'PRADHAN' exists per village
CREATE UNIQUE INDEX IF NOT EXISTS unique_pradhan_per_village ON panchayat_employees (village_id) WHERE position = 'PRADHAN';


-- SCHEMES TABLE (Independent)
CREATE TABLE IF NOT EXISTS schemes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

-- SCHEME ENROLLMENT TABLE (Depends on CITIZENS and SCHEMES)
CREATE TABLE IF NOT EXISTS scheme_enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    citizen_id INT NOT NULL,
    scheme_id INT NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    enrollment_year INT GENERATED ALWAYS AS (EXTRACT (year FROM enrollment_date)) STORED,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE,
    CONSTRAINT unique_citizen_scheme_per_year UNIQUE (citizen_id, scheme_id, enrollment_year)
);

CREATE TABLE IF NOT EXISTS expenditure (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    amount INT NOT NULL CHECK (amount > 0),
    date_spent DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS vaccination (
	vaccination_id SERIAL PRIMARY KEY,
	citizen_id INT,
	vaccine_type VARCHAR(50) NOT NULL,
	date_administered DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- Insert into village
INSERT INTO village (name) VALUES ('Greenwood'), ('Sunnyvale'), ('Riverside');

-- Insert into households
INSERT INTO households (primary_residence) VALUES ('123 Main St'), ('456 Elm St'), ('789 Oak St');

-- Insert into citizens
INSERT INTO citizens (name, dob, gender, phone, household_id, educational_qualification, village_id) 
VALUES 
    ('John Doe', '1985-06-15', 'M', '9876543210', 1, 'Graduate', 1),
    ('Jane Doe', '1990-09-25', 'F', '8765432109', 1, 'Post-Graduate', 1),
    ('Alice Smith', '2000-04-12', 'F', '7654321098', 2, '12th', 2),
    ('Bob Brown', '1975-12-05', 'M', '6543210987', 3, '10th', 3);

-- Set head_of_household
UPDATE households SET head_of_household = 1 WHERE id = 1;
UPDATE households SET head_of_household = 3 WHERE id = 2;

-- Insert into users
INSERT INTO users (username, pswd, user_type, citizen_id)
VALUES 
    ('john_doe', 'hashedpassword1', 'USER', 1),
    ('jane_doe', 'hashedpassword2', 'PANCHAYAT_EMPLOYEES', 2),
    ('admin_user', 'hashedpassword3', 'SYSTEM_ADMINISTRATOR', NULL);

-- Insert into tax_filing
INSERT INTO tax_filing (amount, citizen_id, filing_date)
VALUES 
    (5000, 1, '2024-05-10'),
    (3000, 3, '2024-07-15');

-- Insert into income_declarations
INSERT INTO income_declarations (amount, citizen_id, source, filing_date)
VALUES 
    (40000, 1, 'Salary', '2024-06-01'),
    (25000, 2, 'Freelance', '2024-06-05');

-- Insert into certificates
INSERT INTO certificates (cert_type, citizen_issued)
VALUES 
    ('Birth Certificate', 3),
    ('Income Certificate', 1);

-- Insert into assets
INSERT INTO assets (asset_type, owner_id)
VALUES 
    ('Land', 1),
    ('Vehicle', 2);

-- Insert into panchayat_employees
INSERT INTO panchayat_employees (citizen_id, position, salary, village_id)
VALUES 
    (2, 'PRADHAN', 50000, 1),
    (4, 'MEMBER', 30000, 3);

-- Insert into schemes
INSERT INTO schemes (name, description)
VALUES 
    ('Housing Assistance', 'Provides financial aid for home construction'),
    ('Education Scholarship', 'Supports students with tuition fees');

-- Insert into scheme_enrollment
INSERT INTO scheme_enrollment (citizen_id, scheme_id, enrollment_date)
VALUES 
    (1, 1, '2024-04-10'),
    (3, 2, '2024-05-20');

-- Insert into expenditure
INSERT INTO expenditure (category, amount, date_spent)
VALUES 
    ('Road Repair', 100000, '2024-03-15'),
    ('Water Supply', 50000, '2024-02-28');

-- Insert into vaccination
INSERT INTO vaccination (citizen_id, vaccine_type, date_administered)
VALUES 
    (1, 'COVID-19', '2024-01-10'),
    (3, 'Polio', '2024-02-05');

