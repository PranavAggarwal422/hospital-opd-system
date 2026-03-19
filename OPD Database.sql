-- DROP DATABASE IF EXISTS hospital_opd_system;
-- CREATE DATABASE hospital_opd_system;
-- USE hospital_opd_system;
CREATE TABLE IF NOT EXISTS UserAccount (
	user_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(15) UNIQUE ,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(250) NOT NULL,
    user_role ENUM('Doctor', 'Patient', 'LabStaff', 'Admin', 'SuperAdmin') NOT NULL,
    user_status ENUM('Active', 'Inactive', 'Locked') NOT NULL DEFAULT 'Active', 
   
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
	updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
    CHECK(phone IS NOT NULL  OR email IS NOT NULL)
) ;

CREATE TABLE IF NOT EXISTS Hospital (
	hospital_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	hospital_name VARCHAR(150) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(6) NOT NULL CHECK (pincode REGEXP '^[0-9]{6}$'),
    is_active BOOLEAN DEFAULT TRUE NOT NULL, 
    
	UNIQUE(state, city, hospital_name)
) ;

CREATE INDEX idx_hospital_location
ON Hospital(state, city, pincode) ; 

CREATE INDEX idx_hospital_name
ON Hospital(hospital_name) ; 


CREATE TABLE IF NOT EXISTS Admin(
	admin_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED UNIQUE NOT NULL,
    hospital_id INT UNSIGNED NOT NULL,
    admin_name VARCHAR(100) NOT NULL,
    
    FOREIGN KEY(user_id) REFERENCES UserAccount(user_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

	FOREIGN KEY(hospital_id) REFERENCES Hospital(hospital_id)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Patient (
	patient_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL UNIQUE,
    patient_name VARCHAR(100) NOT NULL,
	gender ENUM('Male' , 'Female', 'Other') NOT NULL,
    dob DATE,
    address VARCHAR(500),
    
    FOREIGN KEY(user_id) REFERENCES UserAccount(user_id)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE
) ;

CREATE TABLE IF NOT EXISTS Department(
	department_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
	hospital_id INT UNSIGNED NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    UNIQUE KEY uniq_dept_per_hospital (hospital_id, department_name),
    
    -- This unique key is required to allow composite FK from OPD(hospital_id, department_id)
    UNIQUE KEY uniq_dept_hospital_composite(hospital_id, department_id),
    
    FOREIGN KEY(hospital_id) REFERENCES Hospital(hospital_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- list departments of a hospital
CREATE INDEX idx_department_hospital
ON Department(hospital_id);

CREATE TABLE IF NOT EXISTS Doctor(
	doctor_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED UNIQUE NOT NULL,
    department_id INT UNSIGNED NOT NULL,
    doctor_name VARCHAR(100) NOT NULL,
	gender ENUM('Male' , 'Female', 'Other') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    FOREIGN KEY(user_id) REFERENCES UserAccount(user_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    
    FOREIGN KEY(department_id) REFERENCES Department(department_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ;
-- fetch doctors by department 
CREATE INDEX idx_doctor_department
ON Doctor(department_id);

CREATE TABLE IF NOT EXISTS OPD(
	opd_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	department_id INT UNSIGNED NOT NULL,
    hospital_id INT UNSIGNED NOT NULL,
    room_no VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    UNIQUE KEY uniq_room_per_hospital(hospital_id, room_no),
    
    --  OPD cannot have mismatched hospital+department
    --  ensuring using foreign key for now ; can be replaced by trigger later 
    FOREIGN KEY(hospital_id, department_id) REFERENCES Department(hospital_id, department_id) 
    ON DELETE RESTRICT 
    ON UPDATE CASCADE 
);
-- fetch OPDs by department
CREATE INDEX idx_opd_department
ON OPD(department_id);

CREATE TABLE IF NOT EXISTS OPDSession (
	session_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	doctor_id INT UNSIGNED NOT NULL,
    opd_id INT UNSIGNED NOT NULL,
    -- doctor and opd must be of same departments ensured by trigger
    week_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    max_tokens_per_session INT UNSIGNED NOT NULL DEFAULT 50, -- no overbooking beyond max_tokens_per_session to be ensure later 
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    
    FOREIGN KEY (opd_id) REFERENCES OPD(opd_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    
    -- Overlapping will be handle later either through application layer or trigger 
    CHECK(start_time < end_time)
);

-- Doctors + patients will view schedule by day.
CREATE INDEX idx_session_doctor_weekday
ON OPDSession(doctor_id, week_day);

CREATE INDEX idx_session_opd_weekday
ON OPDSession(opd_id, week_day);


CREATE TABLE IF NOT EXISTS Appointment ( 
	appointment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id INT UNSIGNED NOT NULL,
    patient_id INT UNSIGNED NOT NULL,
    department_id INT UNSIGNED NOT NULL, -- to ensure one_person_one_appointment_per_department
    
    token_no INT UNSIGNED NOT NULL, 
    -- token auto generation (appointments already booked for same session_id and appointment_date + 1) to be ensure later 
    
    appointment_date DATE NOT NULL, -- date must match weekday of OPDSession to be ensure later 
    -- expected_time = OPDSession.start_time + (token_no-1)5 minutes
    
    appointment_status ENUM('Booked','Expired','Cancelled') NOT NULL DEFAULT 'Booked', 
    -- status will be update to expire automatically by system after opdsession end ; expired means completed 
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
    
    UNIQUE KEY one_patient_dept_date(patient_id, department_id, appointment_date),
    UNIQUE KEY uniq_session_date_token(session_id, appointment_date, token_no), -- also idx_session_appt_date for Show today’s queue for a session
    
    FOREIGN KEY(session_id) REFERENCES OPDSession(session_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    
    FOREIGN KEY(patient_id) REFERENCES Patient(patient_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
    
    FOREIGN KEY(department_id) REFERENCES Department(department_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- Show appointment history of a patient ORDER BY appointment_date
CREATE INDEX idx_appt_patient_date
ON Appointment(patient_id, appointment_date);

-- Department-wise load today
CREATE INDEX idx_appt_department_date
ON Appointment(department_id, appointment_date);

CREATE INDEX idx_session_date_token
ON Appointment(session_id, appointment_date, token_no, appointment_status);

CREATE TABLE IF NOT EXISTS DiagnosticLab (
	lab_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT UNSIGNED NOT NULL,
    lab_name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    is_active BOOLEAN NOT NULL DEFAULT TRUE ,
    
    UNIQUE KEY uniq_lab_per_hospital(hospital_id, lab_name),
    FOREIGN KEY(hospital_id) REFERENCES Hospital(hospital_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
); 

CREATE TABLE IF NOT EXISTS LabStaff (
	staff_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
    lab_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL UNIQUE ,
    staff_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE ,
    staff_role ENUM('Technician','Receptionist','Manager') NOT NULL,
    
    FOREIGN KEY(lab_id) REFERENCES DiagnosticLab(lab_id)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE,
    
    FOREIGN KEY(user_id) REFERENCES UserAccount(user_id)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE
);
CREATE INDEX idx_labstaff_lab
ON LabStaff(lab_id);


CREATE TABLE IF NOT EXISTS HospitalTest (
    test_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT UNSIGNED NOT NULL,

    test_type ENUM('XRay','MRI','CT','Ultrasound','Blood','Urine','Other') NOT NULL,
    test_name VARCHAR(120) NOT NULL,
    test_description VARCHAR(250),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE KEY uniq_test_per_hospital (hospital_id, test_name),

    FOREIGN KEY (hospital_id) REFERENCES Hospital(hospital_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE
);
-- find all tests of a hospital
CREATE INDEX idx_hospitaltest_hospital
ON HospitalTest(hospital_id);

CREATE TABLE IF NOT EXISTS LabSupportTest (
    lab_id INT UNSIGNED NOT NULL,
    test_id INT UNSIGNED NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE, -- will be used for soft delete 

    PRIMARY KEY (lab_id, test_id),

    FOREIGN KEY (lab_id) REFERENCES DiagnosticLab(lab_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE,

    FOREIGN KEY (test_id) REFERENCES HospitalTest(test_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE
);
CREATE INDEX idx_lab_support_test_lab
ON LabSupportTest(lab_id);
CREATE INDEX idx_lab_support_test_test
ON LabSupportTest(test_id);


CREATE TABLE IF NOT EXISTS TestRequest(
	request_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    lab_id INT UNSIGNED NOT NULL,
    appointment_id INT UNSIGNED NOT NULL,
    test_id INT UNSIGNED NOT NULL,
    
    test_status ENUM('Requested', 'SampleCollected', 'Completed') NOT NULL DEFAULT 'Requested',
    requested_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sample_collected_time TIMESTAMP NULL,
    completed_time TIMESTAMP NULL,
    
    FOREIGN KEY(appointment_id) REFERENCES Appointment(appointment_id)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE,
    
    FOREIGN KEY (test_id) REFERENCES HospitalTest(test_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE,
    
    UNIQUE(appointment_id, test_id),
    
    CHECK(
	  (test_status = 'Requested' AND sample_collected_time IS NULL AND completed_time IS NULL)
	  OR
	  (test_status = 'SampleCollected' AND sample_collected_time IS NOT NULL AND completed_time IS NULL)
	  OR
	  (test_status = 'Completed' AND sample_collected_time IS NOT NULL AND completed_time IS NOT NULL)
	) ,
    
    -- Enforce lab supports this test
    FOREIGN KEY (lab_id, test_id) REFERENCES LabSupportTest(lab_id, test_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE
);

-- Show pending tests for a lab sorted by test_id
CREATE INDEX idx_test_lab_status
ON TestRequest(lab_id, test_status, test_id);

-- Show all tests for an appointment 
CREATE INDEX idx_test_appointment
ON TestRequest(appointment_id);


CREATE TABLE IF NOT EXISTS Report ( -- Only for completed request
    request_id INT UNSIGNED PRIMARY KEY,
    report_url VARCHAR(255) NOT NULL,
    remarks VARCHAR(255),
    upload_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (request_id) REFERENCES TestRequest(request_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS Feedback (
    feedback_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NOT NULL UNIQUE, -- one feedback per appointment

    rating TINYINT UNSIGNED NOT NULL,
    comment VARCHAR(500),
    submitted_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE,
    
    CHECK (rating BETWEEN 1 AND 5)
);

-- Doctor and OPD must belong to same department
DELIMITER $$
CREATE TRIGGER check_doctor_opd_department
BEFORE INSERT ON OPDSession
FOR EACH ROW
BEGIN

    DECLARE doctor_dept INT;
    DECLARE opd_dept INT;

    SELECT department_id
    INTO doctor_dept
    FROM Doctor
    WHERE doctor_id = NEW.doctor_id;

    SELECT department_id
    INTO opd_dept
    FROM OPD
    WHERE opd_id = NEW.opd_id;

    IF doctor_dept != opd_dept THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor and OPD must belong to same department';
    END IF;

END$$
DELIMITER ;

--  Triggers for no overbooking (Appointments cannot exceed session capacity) and token generation
DELIMITER $$
CREATE TRIGGER appointment_insert_control
BEFORE INSERT ON Appointment
FOR EACH ROW
BEGIN
    DECLARE next_token INT;
    DECLARE token_count INT;
    DECLARE max_tokens INT;

    SELECT IFNULL(MAX(token_no),0)+1
    INTO next_token
    FROM Appointment
    WHERE session_id = NEW.session_id
    AND appointment_date = NEW.appointment_date;

    SELECT COUNT(*)
    INTO token_count
    FROM Appointment
    WHERE session_id = NEW.session_id
    AND appointment_date = NEW.appointment_date
    AND appointment_status='Booked';

    SELECT max_tokens_per_session
    INTO max_tokens
    FROM OPDSession
    WHERE session_id = NEW.session_id;

    IF token_count >= max_tokens THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT='Session token limit reached';
    END IF;

    SET NEW.token_no = next_token;

END$$
DELIMITER ;


DELIMITER $$
CREATE TRIGGER check_token_limit_update
BEFORE UPDATE ON Appointment
FOR EACH ROW
BEGIN
    DECLARE token_count INT;
    DECLARE max_tokens INT;

    SELECT COUNT(*)
    INTO token_count
    FROM Appointment
    WHERE session_id = NEW.session_id
      AND appointment_date = NEW.appointment_date
      AND appointment_status = 'Booked'
      AND appointment_id != OLD.appointment_id;

    SELECT max_tokens_per_session
    INTO max_tokens
    FROM OPDSession
    WHERE session_id = NEW.session_id;

    IF token_count >= max_tokens THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Session token limit reached';
    END IF;

END$$
DELIMITER ;


-- Triggers to prevent overlapping sessions (Doctor cannot have overlapping schedule)
DELIMITER $$
CREATE TRIGGER prevent_session_overlap_insert
BEFORE INSERT ON OPDSession
FOR EACH ROW
BEGIN
    DECLARE overlap_count INT;

    SELECT COUNT(*)
    INTO overlap_count
    FROM OPDSession
    WHERE doctor_id = NEW.doctor_id
      AND week_day = NEW.week_day
      AND is_active = TRUE
      AND (
            NEW.start_time < end_time
            AND NEW.end_time > start_time
          );

    IF overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor already has overlapping session';
    END IF;

END$$
DELIMITER ;


DELIMITER $$
CREATE TRIGGER prevent_session_overlap_update
BEFORE UPDATE ON OPDSession
FOR EACH ROW
BEGIN
    DECLARE overlap_count INT;

    SELECT COUNT(*)
    INTO overlap_count
    FROM OPDSession
    WHERE doctor_id = NEW.doctor_id
      AND week_day = NEW.week_day
      AND is_active = TRUE
      AND session_id != OLD.session_id
      AND (
            NEW.start_time < end_time
            AND NEW.end_time > start_time
          );

    IF overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor already has overlapping session';
    END IF;

END$$
DELIMITER ;

-- Appointment data must match weekday of OPD Session
DELIMITER $$
CREATE TRIGGER check_session_weekday
BEFORE INSERT ON Appointment
FOR EACH ROW
BEGIN
    DECLARE session_day VARCHAR(10);
    DECLARE booking_day VARCHAR(10);

    SELECT week_day
    INTO session_day
    FROM OPDSession
    WHERE session_id = NEW.session_id;

    SET booking_day = DAYNAME(NEW.appointment_date);

    IF session_day != booking_day THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Appointment date must match session weekday';
    END IF;

END$$
DELIMITER ;

-- Enable MySQL event scheduler
-- SET GLOBAL event_scheduler = ON; -- require admin priviliges 
-- Remove existing event if it exists
DROP EVENT IF EXISTS expire_completed_sessions;

DELIMITER $$
CREATE EVENT expire_completed_sessions
ON SCHEDULE EVERY 5 MINUTE
DO
BEGIN
    UPDATE Appointment a
    JOIN OPDSession s 
        ON a.session_id = s.session_id

    SET a.appointment_status = 'Expired'

    WHERE a.appointment_status = 'Booked'
    AND (
        a.appointment_date < CURDATE()
        OR
        (
            a.appointment_date = CURDATE()
            AND s.end_time < CURTIME()
        )
    );

END$$
DELIMITER ;
