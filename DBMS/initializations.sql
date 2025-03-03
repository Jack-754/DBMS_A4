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

-- Add FOREIGN KEY Constraint for head_of_household after CITIZENS table creation
ALTER TABLE households 
ADD CONSTRAINT fk_head_of_household FOREIGN KEY (head_of_household) REFERENCES citizens(id) ON DELETE SET NULL;

-- USERS TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    pswd VARCHAR(255) NOT NULL, -- Increased length for hashed passwords
    user_type TEXT NOT NULL CHECK (user_type IN ('CITIZEN', 'GOVERNMENT_MONITOR', 'PANCHAYAT_EMPLOYEES', 'SYSTEM_ADMINISTRATOR')),
    citizen_id INT,
    CONSTRAINT citizen_id_required CHECK (
        (user_type IN ('CITIZEN', 'PANCHAYAT_EMPLOYEES', 'GOVERNMENT_MONITOR') AND citizen_id IS NOT NULL) OR
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
    financial_year VARCHAR(9),
    CONSTRAINT unique_tax_filing_per_year UNIQUE (citizen_id, financial_year),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- Create trigger to calculate financial_year automatically
CREATE OR REPLACE FUNCTION calculate_financial_year()
RETURNS TRIGGER AS $$
BEGIN
    IF EXTRACT(MONTH FROM NEW.filing_date) >= 4 THEN
        NEW.financial_year := CONCAT(EXTRACT(YEAR FROM NEW.filing_date), '-', EXTRACT(YEAR FROM NEW.filing_date) + 1);
    ELSE
        NEW.financial_year := CONCAT(EXTRACT(YEAR FROM NEW.filing_date) - 1, '-', EXTRACT(YEAR FROM NEW.filing_date));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tax_filing_financial_year
BEFORE INSERT OR UPDATE ON tax_filing
FOR EACH ROW EXECUTE FUNCTION calculate_financial_year();

-- INCOME DECLARATIONS TABLE (Depends on CITIZENS)
CREATE TABLE IF NOT EXISTS income_declarations (
    receipt_no SERIAL PRIMARY KEY,
    amount INT NOT NULL CHECK (amount > 0),
    citizen_id INT NOT NULL,
    filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
    source VARCHAR(50) NOT NULL,
    financial_year VARCHAR(9),
    CONSTRAINT unique_income_declaration_per_year UNIQUE (citizen_id, source, financial_year),
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
);

-- Create trigger to calculate financial_year automatically
CREATE TRIGGER update_income_declaration_financial_year
BEFORE INSERT OR UPDATE ON income_declarations
FOR EACH ROW EXECUTE FUNCTION calculate_financial_year();

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
    date_of_registration DATE NOT NULL DEFAULT CURRENT_DATE
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
CREATE UNIQUE INDEX unique_pradhan_per_village ON panchayat_employees (village_id) WHERE position = 'PRADHAN';


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
    enrollment_year INT,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE,
    CONSTRAINT unique_citizen_scheme_per_year UNIQUE (citizen_id, scheme_id, enrollment_year)
);

-- Create trigger to calculate enrollment_year automatically
CREATE OR REPLACE FUNCTION calculate_enrollment_year()
RETURNS TRIGGER AS $$
BEGIN
    NEW.enrollment_year := EXTRACT(YEAR FROM NEW.enrollment_date);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_enrollment_year
BEFORE INSERT OR UPDATE ON scheme_enrollment
FOR EACH ROW EXECUTE FUNCTION calculate_enrollment_year();

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
    ('john_doe', 'hashedpassword1', 'CITIZEN', 1),
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
INSERT INTO assets (asset_type)
VALUES 
    ('Land'),
    ('Vehicle');

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


-- -- USERS TABLE
-- CREATE TABLE IF NOT EXISTS users (
--    id SERIAL PRIMARY KEY NOT NULL,
--    username VARCHAR(255) NOT NULL UNIQUE,
--    password VARCHAR(255) NOT NULL, -- Increased length for hashed passwords
--    type TEXT NOT NULL CHECK (type IN ('USER', 'GOVERNMENT_MONITOR', 'PANCHAYAT_EMPLOYEES', 'SYSTEM_ADMINISTRATOR')),
--    citizen_id INT,
--    CONSTRAINT citizen_id_required CHECK (
--        (type IN ('USER', 'PANCHAYAT_EMPLOYEES') AND citizen_id IS NOT NULL) OR
--        (type IN ('GOVERNMENT_MONITOR', 'SYSTEM_ADMINISTRATOR') AND citizen_id IS NULL)
--    ),
--    FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );

-- -- CITIZENS TABLE
-- CREATE TABLE IF NOT EXISTS citizens (
--    id SERIAL PRIMARY KEY NOT NULL,
--    name VARCHAR(255) NOT NULL,
--    dob DATE NOT NULL,
--    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
--    phone VARCHAR(10) NOT NULL CHECK (phone ~ '^[0-9]{10}$'), -- Ensures valid 10-digit phone number
--    household_id INT NOT NULL,
--    educational_qualification TEXT NOT NULL CHECK (
--        educational_qualification IN ('Illiterate', 'Primary', 'Secondary', '10th', '12th', 'Graduate', 'Post-Graduate')
--    ),
--    mother_id INT,
--    father_id INT,
--    village_id INT,
--    FOREIGN KEY (mother_id) REFERENCES citizens(id) ON DELETE SET NULL,
--    FOREIGN KEY (father_id) REFERENCES citizens(id) ON DELETE SET NULL,
--    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
--    FOREIGN KEY (village_id) REFERENCES village(id) ON DELETE CASCADE
-- );

-- -- TAX FILING TABLE
-- CREATE TABLE IF NOT EXISTS tax_filing (
--     receipt_no SERIAL PRIMARY KEY,
--     amount INT NOT NULL CHECK (amount > 0),
--     citizen_id INT NOT NULL,
--     filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
--     FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );

-- -- INCOME DECLARATIONS TABLE
-- CREATE TABLE IF NOT EXISTS income_declarations (
--     receipt_no SERIAL PRIMARY KEY,
--     amount INT NOT NULL CHECK (amount > 0),
--     citizen_id INT NOT NULL,
--     filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
--     source VARCHAR(50) NOT NULL,
--     FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );

-- -- HOUSEHOLD TABLE
-- CREATE TABLE IF NOT EXISTS households (
--     id SERIAL PRIMARY KEY,
--     household_member_count INT NOT NULL CHECK (household_member_count > 0),
--     primary_residence VARCHAR(100) NOT NULL,
--     head_of_household INT,
--     FOREIGN KEY (head_of_household) REFERENCES citizens(id) ON DELETE SET NULL
-- );





-- -- GOVERNMENT MONITOR TABLE
-- CREATE TABLE IF NOT EXISTS government_monitor (
--     id SERIAL PRIMARY KEY,
--     department VARCHAR(50) NOT NULL,
--     FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );

-- -- RECORDS TABLE
-- CREATE TABLE IF NOT EXISTS records (
--     id SERIAL PRIMARY KEY,
--     citizen_id INT NOT NULL,
--     record_type VARCHAR(50) NOT NULL,
--     details TEXT NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );

-- -- CENSUS DATA TABLE
-- CREATE TABLE IF NOT EXISTS census_data (
--     id SERIAL PRIMARY KEY,
--     year INT NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
--     total_population INT NOT NULL CHECK (total_population > 0),
--     number_of_households INT NOT NULL CHECK (number_of_households > 0)
-- );

-- -- ENVIRONMENT DATA TABLE
-- CREATE TABLE IF NOT EXISTS environment_data (
--     id SERIAL PRIMARY KEY,
--     year INT NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
--     air_quality_index INT CHECK (air_quality_index BETWEEN 0 AND 500),
--     water_quality_index INT CHECK (water_quality_index BETWEEN 0 AND 100),
--     forest_cover_percentage DECIMAL(5,2) CHECK (forest_cover_percentage BETWEEN 0 AND 100)
-- );

-- -- AGRICULTURAL DATA TABLE
-- CREATE TABLE IF NOT EXISTS agricultural_data (
--     id SERIAL PRIMARY KEY,
--     year INT NOT NULL CHECK (year >= 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
--     total_crop_production INT NOT NULL CHECK (total_crop_production > 0),
--     irrigated_land_percentage DECIMAL(5,2) CHECK (irrigated_land_percentage BETWEEN 0 AND 100)
-- );

-- -- EXPENDITURE TABLE
-- CREATE TABLE IF NOT EXISTS expenditure (
--     id SERIAL PRIMARY KEY,
--     category VARCHAR(50) NOT NULL,
--     amount INT NOT NULL CHECK (amount > 0),
--     date_spent DATE NOT NULL DEFAULT CURRENT_DATE
-- );

-- -- VILLAGE TABLE
-- CREATE TABLE IF NOT EXISTS village (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(50) NOT NULL UNIQUE
-- );

-- -- TAX FILING TABLE (One filing per citizen per financial year)
-- CREATE TABLE IF NOT EXISTS tax_filing (
--     receipt_no SERIAL PRIMARY KEY,
--     amount INT NOT NULL CHECK (amount > 0),
--     citizen_id INT NOT NULL,
--     filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
--     financial_year VARCHAR(9) GENERATED ALWAYS AS (
--         CASE 
--             WHEN EXTRACT(MONTH FROM filing_date) >= 4 
--             THEN CONCAT(EXTRACT(YEAR FROM filing_date), '-', EXTRACT(YEAR FROM filing_date) + 1)
--             ELSE CONCAT(EXTRACT(YEAR FROM filing_date) - 1, '-', EXTRACT(YEAR FROM filing_date))
--         END
--     ) STORED,
--     CONSTRAINT unique_tax_filing_per_year UNIQUE (citizen_id, financial_year),
--     FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );

-- -- INCOME DECLARATIONS TABLE (One declaration per citizen per financial year)
-- CREATE TABLE IF NOT EXISTS income_declarations (
--     receipt_no SERIAL PRIMARY KEY,
--     amount INT NOT NULL CHECK (amount > 0),
--     citizen_id INT NOT NULL,
--     filing_date DATE NOT NULL DEFAULT CURRENT_DATE,
--     source VARCHAR(50) NOT NULL,
--     financial_year VARCHAR(9) GENERATED ALWAYS AS (
--         CASE 
--             WHEN EXTRACT(MONTH FROM filing_date) >= 4 
--             THEN CONCAT(EXTRACT(YEAR FROM filing_date), '-', EXTRACT(YEAR FROM filing_date) + 1)
--             ELSE CONCAT(EXTRACT(YEAR FROM filing_date) - 1, '-', EXTRACT(YEAR FROM filing_date))
--         END
--     ) STORED,
--     CONSTRAINT unique_income_declaration_per_year UNIQUE (citizen_id, financial_year),
--     FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
-- );
-- -- CREATE TABLE IF NOT EXISTS citizens (
-- --    id SERIAL PRIMARY KEY NOT NULL,
-- --    name VARCHAR(255) NOT NULL,
-- --    dob DATE NOT NULL,
-- --    age INT GENERATED ALWAYS AS (DATE_PART('year', AGE(dob))) STORED,
-- --    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
-- --    phone VARCHAR(10) NOT NULL CHECK (phone ~ '^[0-9]{10}$'), -- Ensures valid 10-digit phone number
-- --    household_id INT NOT NULL,
-- --    educational_qualification TEXT NOT NULL CHECK (
-- --        educational_qualification IN ('Illiterate', 'Primary', 'Secondary', '10th', '12th', 'Graduate', 'Post-Graduate')
-- --    ),
-- --    mother_id INT,
-- --    father_id INT,
-- --    FOREIGN KEY (mother_id) REFERENCES citizens(id) ON DELETE SET NULL,
-- --    FOREIGN KEY (father_id) REFERENCES citizens(id) ON DELETE SET NULL,
-- --    FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE
-- -- );

