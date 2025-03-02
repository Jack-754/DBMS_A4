-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
   id SERIAL PRIMARY KEY NOT NULL,
   username VARCHAR(255) NOT NULL UNIQUE,
   password VARCHAR(255) NOT NULL, -- Increased length for hashed passwords
   type TEXT NOT NULL CHECK (type IN ('USER', 'GOVERNMENT_MONITOR', 'PANCHAYAT_EMPLOYEES', 'SYSTEM_ADMINISTRATOR')),
   citizen_id INT,
   CONSTRAINT citizen_id_required CHECK (
       (type IN ('USER', 'PANCHAYAT_EMPLOYEES') AND citizen_id IS NOT NULL) OR
       (type IN ('GOVERNMENT_MONITOR', 'SYSTEM_ADMINISTRATOR') AND citizen_id IS NULL)
   ),
   FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE SET NULL
);

-- LOGIN LOGS TABLE
CREATE TABLE IF NOT EXISTS login_logs (  
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- CITIZENS TABLE
CREATE TABLE IF NOT EXISTS citizens (
   id SERIAL PRIMARY KEY NOT NULL,
   name VARCHAR(255) NOT NULL,
   dob DATE NOT NULL,
   gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
   phone VARCHAR(10) NOT NULL CHECK (phone ~ '^[0-9]{10}$'), -- Ensures valid 10-digit phone number
   household_id INT NOT NULL,
   educational_qualification TEXT NOT NULL CHECK (
       educational_qualification IN ('Illiterate', 'Primary', 'Secondary', '10th', '12th', 'Graduate', 'Post-Graduate')
   ),
   mother_id INT,
   father_id INT,
   FOREIGN KEY (mother_id) REFERENCES citizens(id) ON DELETE SET NULL,
   FOREIGN KEY (father_id) REFERENCES citizens(id) ON DELETE SET NULL,
   FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

-- TAX FILING TABLE
CREATE TABLE IF NOT EXISTS tax_filing (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- INCOME DECLARATIONS TABLE
CREATE TABLE IF NOT EXISTS income_declarations (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    source VARCHAR(50) NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- HOUSEHOLD TABLE
CREATE TABLE IF NOT EXISTS households (
    id SERIAL PRIMARY KEY,
    household_member_count INT NOT NULL CHECK (household_member_count > 0),
    primary_residence VARCHAR(100) NOT NULL,
    head_of_household INT,
    FOREIGN KEY (head_of_household) REFERENCES citizens(id) ON DELETE SET NULL
);

-- CERTIFICATES TABLE
CREATE TABLE IF NOT EXISTS certificates (
    certificate_no SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    citizen_issued INT NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (citizen_issued) REFERENCES citizens(id) ON DELETE CASCADE
);

-- ASSETS TABLE
CREATE TABLE IF NOT EXISTS assets (
    asset_id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    date_of_registration DATE NOT NULL DEFAULT CURRENT_DATE,
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- PANCHAYAT EMPLOYEES TABLE
CREATE TABLE IF NOT EXISTS panchayat_employees (
    id SERIAL PRIMARY KEY,
    citizen_id INT NOT NULL UNIQUE,
    position VARCHAR(50) NOT NULL,
    salary INT CHECK (salary > 0),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- GOVERNMENT MONITOR TABLE
CREATE TABLE IF NOT EXISTS government_monitor (
    id SERIAL PRIMARY KEY,
    citizen_id INT NOT NULL UNIQUE,
    department VARCHAR(50) NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- RECORDS TABLE
CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    citizen_id INT NOT NULL,
    record_type VARCHAR(50) NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- CENSUS DATA TABLE
CREATE TABLE IF NOT EXISTS census_data (
    id SERIAL PRIMARY KEY,
    year INT NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    total_population INT NOT NULL CHECK (total_population > 0),
    number_of_households INT NOT NULL CHECK (number_of_households > 0)
);

-- ENVIRONMENT DATA TABLE
CREATE TABLE IF NOT EXISTS environment_data (
    id SERIAL PRIMARY KEY,
    year INT NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    air_quality_index INT CHECK (air_quality_index BETWEEN 0 AND 500),
    water_quality_index INT CHECK (water_quality_index BETWEEN 0 AND 100),
    forest_cover_percentage DECIMAL(5,2) CHECK (forest_cover_percentage BETWEEN 0 AND 100)
);

-- AGRICULTURAL DATA TABLE
CREATE TABLE IF NOT EXISTS agricultural_data (
    id SERIAL PRIMARY KEY,
    year INT NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    total_crop_production INT NOT NULL CHECK (total_crop_production > 0),
    irrigated_land_percentage DECIMAL(5,2) CHECK (irrigated_land_percentage BETWEEN 0 AND 100)
);

-- EXPENDITURE TABLE
CREATE TABLE IF NOT EXISTS expenditure (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    amount INT NOT NULL CHECK (amount > 0),
    date_spent DATE NOT NULL DEFAULT CURRENT_DATE
);

-- VILLAGE TABLE
CREATE TABLE IF NOT EXISTS village (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
-- TAX FILING TABLE (One filing per citizen per financial year)
CREATE TABLE IF NOT EXISTS tax_filing (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    financial_year VARCHAR(9) GENERATED ALWAYS AS (
        CASE 
            WHEN EXTRACT(MONTH FROM filing_date) >= 4 
            THEN CONCAT(EXTRACT(YEAR FROM filing_date), '-', EXTRACT(YEAR FROM filing_date) + 1)
            ELSE CONCAT(EXTRACT(YEAR FROM filing_date) - 1, '-', EXTRACT(YEAR FROM filing_date))
        END
    ) STORED,
    CONSTRAINT unique_tax_filing_per_year UNIQUE (citizen_id, financial_year),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- INCOME DECLARATIONS TABLE (One declaration per citizen per financial year)
CREATE TABLE IF NOT EXISTS income_declarations (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    source VARCHAR(50) NOT NULL,
    financial_year VARCHAR(9) GENERATED ALWAYS AS (
        CASE 
            WHEN EXTRACT(MONTH FROM filing_date) >= 4 
            THEN CONCAT(EXTRACT(YEAR FROM filing_date), '-', EXTRACT(YEAR FROM filing_date) + 1)
            ELSE CONCAT(EXTRACT(YEAR FROM filing_date) - 1, '-', EXTRACT(YEAR FROM filing_date))
        END
    ) STORED,
    CONSTRAINT unique_income_declaration_per_year UNIQUE (citizen_id, financial_year),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS citizens (
   id SERIAL PRIMARY KEY NOT NULL,
   name VARCHAR(255) NOT NULL,
   dob DATE NOT NULL,
   age INT GENERATED ALWAYS AS (DATE_PART('year', AGE(dob))) STORED,
   gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
   phone VARCHAR(10) NOT NULL CHECK (phone ~ '^[0-9]{10}$'), -- Ensures valid 10-digit phone number
   caste VARCHAR(20) NOT NULL,
   household_id INT NOT NULL,
   educational_qualification TEXT NOT NULL CHECK (
       educational_qualification IN ('Illiterate', 'Primary', 'Secondary', '10th', '12th', 'Graduate', 'Post-Graduate')
   ),
   mother_id INT,
   father_id INT,
   FOREIGN KEY (mother_id) REFERENCES citizens(id) ON DELETE SET NULL,
   FOREIGN KEY (father_id) REFERENCES citizens(id) ON DELETE SET NULL,
   FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS citizen_edit_logs (
    log_id SERIAL PRIMARY KEY,
    edited_by INT NOT NULL,
    citizen_id INT NOT NULL,
    edit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB,
    FOREIGN KEY (edited_by) REFERENCES users(id),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id)
);

