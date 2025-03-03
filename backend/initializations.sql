--VILLAGE TABLE (Independent)
CREATE TABLE IF NOT EXISTS village (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- HOUSEHOLD TABLE (Independent)
CREATE TABLE IF NOT EXISTS households (
    id SERIAL PRIMARY KEY,
    primary_residence VARCHAR(100) NOT NULL,
    head_of_household INT UNIQUE 
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
    location INT,
    date_of_registration DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (location) REFERENCES village(id) ON DELETE CASCADE
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

-- Create a partial unique index for PRADHAN position
CREATE UNIQUE INDEX unique_pradhan_per_village 
ON panchayat_employees (village_id)
WHERE position = 'PRADHAN';

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
CREATE TABLE census_data (
    citizen_id INT NOT NULL,
    event_type TEXT NOT NULL,
    event_date DATE NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES citizens (id),
    CHECK (event_type IN ('Birth', 'Death', 'Marriage', 'Divorce'))
);

CREATE TABLE land_records (
    land_id SERIAL PRIMARY KEY,
    citizen_id INT NOT NULL,
    area_acres DECIMAL(10, 2) NOT NULL,
    crop_type TEXT NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES citizens (id),
    CHECK (crop_type IN ('Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize'))
);

-- Create trigger function to handle panchayat employee changes
CREATE OR REPLACE FUNCTION manage_panchayat_employees()
RETURNS TRIGGER AS $$
DECLARE
    user_village_id INT;
BEGIN
    -- If user changed from non-panchayat to panchayat employee
    IF OLD.user_type != 'PANCHAYAT_EMPLOYEES' AND NEW.user_type = 'PANCHAYAT_EMPLOYEES' THEN
        -- Get the village_id from citizens table
        SELECT village_id INTO user_village_id 
        FROM citizens 
        WHERE id = NEW.citizen_id;
        
        -- Insert new record into panchayat_employees
        INSERT INTO panchayat_employees (citizen_id, position, salary, village_id)
        VALUES (NEW.citizen_id, 'MEMBER', 30000, user_village_id);
        
    -- If user changed from panchayat to non-panchayat employee
    ELSIF OLD.user_type = 'PANCHAYAT_EMPLOYEES' AND NEW.user_type != 'PANCHAYAT_EMPLOYEES' THEN
        -- Delete the record from panchayat_employees
        DELETE FROM panchayat_employees 
        WHERE citizen_id = NEW.citizen_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger on users table
CREATE TRIGGER user_panchayat_employee_changes
AFTER UPDATE OF user_type ON users
FOR EACH ROW
WHEN (OLD.user_type IS DISTINCT FROM NEW.user_type)
EXECUTE FUNCTION manage_panchayat_employees();

-- Insert villages first (Independent table)
INSERT INTO village (name) VALUES 
    ('Greenwood'),
    ('Sunnyvale'),
    ('Riverside'),
    ('Meadowbrook'),
    ('Highland');

-- Insert households (Independent table)
INSERT INTO households (primary_residence) VALUES 
    ('123 Main St, Greenwood'),
    ('456 Elm St, Greenwood'),
    ('789 Oak St, Sunnyvale'),
    ('321 Pine St, Riverside'),
    ('654 Maple St, Meadowbrook'),
    ('987 Cedar St, Highland'),
    ('741 Birch St, Sunnyvale'),
    ('852 Willow St, Riverside');

-- Insert citizens
INSERT INTO citizens (name, dob, gender, phone, household_id, educational_qualification, village_id) VALUES 
    ('John Doe', '1980-06-15', 'M', '9876543210', 1, 'Graduate', 1),
    ('Jane Doe', '1982-09-25', 'F', '8765432109', 1, 'Post-Graduate', 1),
    ('Alice Smith', '1975-04-12', 'F', '7654321098', 2, '12th', 1),
    ('Bob Brown', '1978-12-05', 'M', '6543210987', 2, '10th', 1),
    ('Charlie Wilson', '1990-03-20', 'M', '5432109876', 3, 'Graduate', 2),
    ('Diana Miller', '1988-07-30', 'F', '4321098765', 3, 'Post-Graduate', 2),
    ('Edward Davis', '1995-11-08', 'M', '3210987654', 4, 'Graduate', 3),
    ('Fiona Taylor', '1992-01-15', 'F', '2109876543', 4, '12th', 3),
    ('George White', '1985-08-22', 'M', '1098765432', 5, 'Secondary', 4),
    ('Helen Green', '1987-04-17', 'F', '9987654321', 5, 'Graduate', 4),
    ('Ian Black', '1983-12-30', 'M', '8876543210', 6, '10th', 5),
    ('Julia Grey', '1986-06-05', 'F', '7765432109', 6, 'Graduate', 5),
    ('Kevin Lee', '1993-09-12', 'M', '6654321098', 7, 'Post-Graduate', 2),
    ('Laura Chen', '1991-02-28', 'F', '5543210987', 7, 'Graduate', 2),
    ('Michael Wong', '1989-07-14', 'M', '4432109876', 8, '12th', 3),
    ('Nancy Park', '1994-11-19', 'F', '3321098765', 8, 'Graduate', 3),
    ('Oliver Singh', '1981-03-25', 'M', '2210987654', 1, 'Post-Graduate', 1),
    ('Patricia Kumar', '1984-08-09', 'F', '1109876543', 2, 'Graduate', 1),
    ('Quinn Martinez', '1996-01-31', 'O', '9988776655', 3, '12th', 2),
    ('Rachel Rodriguez', '1997-05-16', 'F', '8877665544', 4, 'Graduate', 3);

-- Update households with head_of_household
UPDATE households SET head_of_household = 1 WHERE id = 1;  -- John Doe
UPDATE households SET head_of_household = 3 WHERE id = 2;  -- Alice Smith
UPDATE households SET head_of_household = 5 WHERE id = 3;  -- Charlie Wilson
UPDATE households SET head_of_household = 7 WHERE id = 4;  -- Edward Davis
UPDATE households SET head_of_household = 9 WHERE id = 5;  -- George White
UPDATE households SET head_of_household = 11 WHERE id = 6; -- Ian Black
UPDATE households SET head_of_household = 13 WHERE id = 7; -- Kevin Lee
UPDATE households SET head_of_household = 15 WHERE id = 8; -- Michael Wong

-- Insert users (10 users with different roles)
INSERT INTO users (username, pswd, user_type, citizen_id) VALUES 
    ('john_doe', 'hashed_password_1', 'CITIZEN', 1),
    ('jane_doe', 'hashed_password_2', 'PANCHAYAT_EMPLOYEES', 2),
    ('alice_smith', 'hashed_password_3', 'GOVERNMENT_MONITOR', 3),
    ('charlie_wilson', 'hashed_password_4', 'CITIZEN', 5),
    ('diana_miller', 'hashed_password_5', 'PANCHAYAT_EMPLOYEES', 6),
    ('edward_davis', 'hashed_password_6', 'CITIZEN', 7),
    ('helen_green', 'hashed_password_7', 'GOVERNMENT_MONITOR', 10),
    ('kevin_lee', 'hashed_password_8', 'CITIZEN', 13),
    ('laura_chen', 'hashed_password_9', 'PANCHAYAT_EMPLOYEES', 14),
    ('admin_user', 'hashed_password_10', 'SYSTEM_ADMINISTRATOR', NULL);

-- Insert some panchayat employees (one PRADHAN per village)
INSERT INTO panchayat_employees (citizen_id, position, salary, village_id) VALUES 
    (2, 'PRADHAN', 50000, 1),    -- Jane Doe for Greenwood
    (6, 'PRADHAN', 50000, 2),    -- Diana Miller for Sunnyvale
    (14, 'PRADHAN', 50000, 3),   -- Laura Chen for Riverside
    (10, 'MEMBER', 30000, 1),    -- Helen Green as member
    (18, 'MEMBER', 30000, 2);    -- Patricia Kumar as member

-- Insert vaccinations (multiple vaccines per citizen)
INSERT INTO vaccination (citizen_id, vaccine_type, date_administered) VALUES 
    (1, 'COVID-19', '2023-01-10'),
    (1, 'Flu', '2023-09-15'),
    (2, 'COVID-19', '2023-01-12'),
    (3, 'COVID-19', '2023-01-15'),
    (3, 'Tetanus', '2023-06-20'),
    (4, 'COVID-19', '2023-02-01'),
    (5, 'COVID-19', '2023-02-05'),
    (5, 'Hepatitis B', '2023-07-10'),
    (6, 'COVID-19', '2023-02-10'),
    (7, 'COVID-19', '2023-02-15'),
    (8, 'COVID-19', '2023-03-01'),
    (8, 'Flu', '2023-09-20'),
    (9, 'COVID-19', '2023-03-05'),
    (10, 'COVID-19', '2023-03-10'),
    (11, 'COVID-19', '2023-03-15'),
    (12, 'COVID-19', '2023-04-01'),
    (13, 'COVID-19', '2023-04-05'),
    (14, 'COVID-19', '2023-04-10'),
    (15, 'COVID-19', '2023-04-15'),
    (16, 'COVID-19', '2023-05-01'),
    (17, 'COVID-19', '2023-05-05'),
    (18, 'COVID-19', '2023-05-10'),
    (19, 'COVID-19', '2023-05-15'),
    (20, 'COVID-19', '2023-06-01');

-- Insert tax filings
INSERT INTO tax_filing (amount, citizen_id, filing_date) VALUES 
    (25000, 1, '2023-06-15'),
    (30000, 2, '2023-07-10'),
    (20000, 3, '2023-06-20'),
    (15000, 5, '2023-08-05'),
    (35000, 6, '2023-07-15'),
    (28000, 7, '2023-06-25'),
    (22000, 10, '2023-07-20'),
    (40000, 13, '2023-08-10'),
    (32000, 14, '2023-07-25'),
    (18000, 17, '2023-08-15');

-- Insert income declarations
INSERT INTO income_declarations (amount, citizen_id, source, filing_date) VALUES 
    (300000, 1, 'Salary', '2023-04-10'),
    (450000, 2, 'Business', '2023-04-15'),
    (250000, 3, 'Rental', '2023-04-20'),
    (200000, 5, 'Salary', '2023-05-01'),
    (550000, 6, 'Business', '2023-05-05'),
    (350000, 7, 'Salary', '2023-05-10'),
    (400000, 10, 'Rental', '2023-05-15'),
    (600000, 13, 'Business', '2023-06-01'),
    (480000, 14, 'Salary', '2023-06-05'),
    (280000, 17, 'Rental', '2023-06-10');

-- Insert certificates
INSERT INTO certificates (cert_type, citizen_issued) VALUES 
    ('Birth Certificate', 1),
    ('Income Certificate', 1),
    ('Residence Certificate', 2),
    ('Birth Certificate', 3),
    ('Income Certificate', 5),
    ('Caste Certificate', 6),
    ('Birth Certificate', 7),
    ('Marriage Certificate', 8),
    ('Income Certificate', 10),
    ('Residence Certificate', 13),
    ('Birth Certificate', 14),
    ('Income Certificate', 17),
    ('Marriage Certificate', 18),
    ('Residence Certificate', 19),
    ('Birth Certificate', 20);

-- Insert assets

-- Update assets entries with community infrastructure types
INSERT INTO assets (asset_type, location, date_of_registration) VALUES 
    ('STREET_LIGHT', 1, '2022-01-15'),          -- Greenwood
    ('COMMUNITY_PARK', 1, '2022-03-20'),        -- Greenwood
    ('WATER_TANK', 1, '2022-05-10'),            -- Greenwood
    ('PRIMARY_SCHOOL', 2, '2022-02-25'),        -- Sunnyvale
    ('COMMUNITY_HALL', 2, '2022-04-15'),        -- Sunnyvale
    ('HEALTH_CENTER', 2, '2022-06-20'),         -- Sunnyvale
    ('PUBLIC_LIBRARY', 3, '2022-07-10'),        -- Riverside
    ('PLAYGROUND', 3, '2022-08-05'),            -- Riverside
    ('WASTE_FACILITY', 3, '2022-09-15'),        -- Riverside
    ('COMMUNITY_CENTER', 4, '2022-10-20'),      -- Meadowbrook
    ('SPORTS_GROUND', 4, '2022-11-25'),         -- Meadowbrook
    ('DRAINAGE_SYSTEM', 5, '2022-12-30'),       -- Highland
    ('BUS_SHELTER', 5, '2023-01-15'),           -- Highland
    ('TEMPLE', 1, '2023-02-20'),                -- Greenwood
    ('MARKET_COMPLEX', 2, '2023-03-25');

-- Insert schemes
INSERT INTO schemes (name, description) VALUES 
    ('PM Awas Yojana', 'Housing scheme for rural areas'),
    ('Skill Development Program', 'Vocational training for youth'),
    ('Agricultural Subsidy Scheme', 'Support for farmers'),
    ('Education Scholarship', 'Financial aid for students'),
    ('Healthcare Support', 'Medical assistance for elderly'),
    ('Women Empowerment Initiative', 'Support for women entrepreneurs');

-- Insert scheme enrollments
INSERT INTO scheme_enrollment (citizen_id, scheme_id, enrollment_date) VALUES 
    (1, 1, '2023-04-10'),
    (2, 2, '2023-04-15'),
    (3, 3, '2023-05-20'),
    (5, 4, '2023-06-25'),
    (6, 5, '2023-07-30'),
    (7, 6, '2023-08-05'),
    (10, 1, '2023-09-10'),
    (13, 2, '2023-10-15'),
    (14, 3, '2023-11-20'),
    (17, 4, '2023-12-25'),
    (18, 5, '2024-01-30'),
    (19, 6, '2024-02-05'),
    (20, 1, '2024-03-10');

-- Insert expenditure records
INSERT INTO expenditure (category, amount, date_spent) VALUES 
    ('Road Construction', 500000, '2023-04-15'),
    ('Street Lighting', 150000, '2023-05-20'),
    ('Water Supply', 300000, '2023-06-25'),
    ('Sanitation', 200000, '2023-07-30'),
    ('Public Park Maintenance', 100000, '2023-08-05'),
    ('School Infrastructure', 400000, '2023-09-10'),
    ('Healthcare Center', 350000, '2023-10-15'),
    ('Waste Management', 250000, '2023-11-20'),
    ('Community Hall Renovation', 450000, '2023-12-25'),
    ('Emergency Services', 180000, '2024-01-30');

-- Insert census_data entries
INSERT INTO census_data (citizen_id, event_type, event_date) VALUES 
    (1, 'Marriage', '2005-06-15'),
    (2, 'Marriage', '2005-06-15'),
    (3, 'Marriage', '2000-03-22'),
    (4, 'Marriage', '2000-03-22'),
    (5, 'Marriage', '2015-08-10'),
    (6, 'Marriage', '2015-08-10'),
    (7, 'Marriage', '2018-12-25'),
    (8, 'Marriage', '2018-12-25'),
    (9, 'Birth', '1985-08-22'),
    (10, 'Birth', '1987-04-17'),
    (11, 'Divorce', '2022-11-30'),
    (12, 'Divorce', '2022-11-30'),
    (13, 'Marriage', '2019-02-14'),
    (14, 'Marriage', '2019-02-14'),
    (15, 'Death', '2023-09-01');

-- Insert land_records entries
INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES 
    (1, 5.50, 'Rice'),
    (1, 3.25, 'Wheat'),
    (3, 4.75, 'Cotton'),
    (5, 6.00, 'Sugarcane'),
    (6, 2.50, 'Maize'),
    (7, 8.25, 'Rice'),
    (9, 3.75, 'Wheat'),
    (11, 5.00, 'Cotton'),
    (13, 7.50, 'Sugarcane'),
    (14, 4.25, 'Maize'),
    (15, 6.75, 'Rice'),
    (17, 3.50, 'Wheat'),
    (18, 5.25, 'Cotton'),
    (19, 4.00, 'Sugarcane'),
    (20, 2.75, 'Maize');