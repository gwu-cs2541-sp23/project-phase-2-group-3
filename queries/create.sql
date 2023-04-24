-- Active: 1681927449683@@group3phase2-taylor23.c71jatiazsww.us-east-1.rds.amazonaws.com@3306@university
use university;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    uid CHAR(8),
    username varchar(64) NOT NULL UNIQUE, --only used for login, uid for everything else
    password VARCHAR(64) NOT NULL,
    first_name varchar(32) NOT NULL,
    last_name varchar(32) NOT NULL,
    ssn varchar(16) NOT NULL UNIQUE,
    address varchar(64) NOT NULL,
    user_type varchar(16) NOT NULL, --possible choices: sysadmin, gradsec, employee, student, applicant
    PRIMARY KEY(uid)
);

DROP TABLE IF EXISTS students;
CREATE TABLE students (
    uid CHAR(8),
    degree_type varchar(4) NOT NULL, --possible choices: PHD or MS (hardcode those options into form, don't make a query)
    is_suspended BOOLEAN,
    thesis_approved BOOLEAN,
    PRIMARY KEY(uid),
    FOREIGN KEY(uid)
        REFERENCES users(uid)
);

DROP TABLE IF EXISTS employee;
CREATE TABLE employee (
    uid CHAR(8),
    is_professor BOOLEAN,
    is_advisor BOOLEAN,
    is_review_chair BOOLEAN,
    is_reviewer BOOLEAN,
    PRIMARY KEY(uid),
    FOREIGN KEY(uid)
        REFERENCES users(uid)
);

DROP TABLE IF EXISTS reviewers;
CREATE TABLE reviewer_assignments (
    reviewer_uid CHAR(8),
    applicant_uid CHAR(8),
    PRIMARY KEY(reviewer_uid, applicant_uid),
    FOREIGN KEY(reviewer_uid)
        REFERENCES employee(uid),
    FOREIGN KEY(applicant_uid)
        REFERENCES users(uid)
);

DROP TABLE IF EXISTS advisors;
CREATE TABLE advisor_assignments (
    advisor_uid CHAR(8),
    student_uid CHAR(8),
    PRIMARY KEY(advisor_uid, student_uid),
    FOREIGN KEY(advisor_uid)
        REFERENCES employee(uid),
    FOREIGN KEY(student_uid)
        REFERENCES users(uid)
);

DROP TABLE IF EXISTS applicant;
CREATE TABLE applicant (   
   uid CHAR(8) NOT NULL,
   appStatus VARCHAR(32) NOT NULL, --Application Incomplete, Application Awaiting Materials, Application Under Review, Decision Pending, Decision Delivered
   decision VARCHAR(32) NOT NULL, -- Pending, Admit, Admit With Aid, Reject
   PRIMARY KEY (uid),
   FOREIGN KEY (uid) REFERENCES users(uid) 
);

DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni ( --student is deleted from students when they become an alum
	uid CHAR(8),
	grad_year int(4) NOT NULL,
    PRIMARY KEY(uid),
	FOREIGN KEY (uid)
        REFERENCES users(uid)
);

DROP TABLE IF EXISTS classes;
CREATE TABLE classes (
    cid INTEGER,
    dept varchar(8),
    class_number INTEGER,
    title varchar(32),
    credit_hours INTEGER,
    PRIMARY KEY(cid)
);

DROP TABLE IF EXISTS current_sections;
CREATE TABLE current_sections (
    cid INTEGER,
    section_id varchar(8),
    professor_uid CHAR(8),
    year INTEGER,
    semester INTEGER,
    day char(1),
    timeslot INTEGER,
    PRIMARY KEY(cid, section_id),
    FOREIGN KEY(cid) 
        REFERENCES classes(cid),
    FOREIGN KEY(professor_uid)
        REFERENCES employee(uid)
);

DROP TABLE IF EXISTS prerequisites;
CREATE TABLE prerequisites (
    class_cid INTEGER,
    prereq_cid INTEGER,
    PRIMARY KEY(class_cid, prereq_cid),
    FOREIGN KEY(class_cid) 
        REFERENCES classes(cid),
    FOREIGN KEY(prereq_cid) 
        REFERENCES classes(cid)
);

DROP TABLE IF EXISTS student_classes;
CREATE TABLE student_classes (
    student_uid CHAR(8),
    cid INTEGER,
    section_id varchar(8),
    grade char(4),
    finalized BOOL,
    PRIMARY KEY(student_uid, cid, section_id),
    FOREIGN KEY(student_uid) 
        REFERENCES students(uid),
    FOREIGN KEY(cid, section_id) 
        REFERENCES current_sections(cid, section_id)
);

DROP TABLE IF EXISTS applicationForm;
CREATE TABLE applicationForm (
   uid CHAR(8) NOT NULL,
   degreeSeeking VARCHAR(32) NOT NULL,
   MScheck VARCHAR(32),
   MSmajor VARCHAR(32),
   MSyear INT(4),
   MSuniversity VARCHAR(32),
   MSgpa decimal(3,2),
   BAcheck VARCHAR(32) NOT NULL,
   BAmajor VARCHAR(32) NOT NULL,
   BAyear INT(4) NOT NULL,
   BAuniversity VARCHAR(32) NOT NULL,
   BAgpa decimal(3,2) NOT NULL,
   GREverbal INT(4),
   GREquantitative INT(4),
   GREyear INT(4),
   GREadvancedScore INT(4),
   GREadvancedSubject VARCHAR(32),
   TOEFLscore INT(4),
   TOEFLdate VARCHAR(32),
   priorWork VARCHAR(300) NOT NULL,
   startDate VARCHAR(32) NOT NULL,
   transcriptStatus VARCHAR(32),
   r1status VARCHAR(32),
   r1writer VARCHAR(32) NOT NULL,
   r1email VARCHAR(32) NOT NULL,
   r1title VARCHAR(32) NOT NULL,
   r1affiliation VARCHAR(32) NOT NULL,
   r1letter VARCHAR(500) NOT NULL,
   r2status VARCHAR(32),
   r2writer VARCHAR(32),
   r2email VARCHAR(32),
   r2title VARCHAR(32),
   r2affiliation VARCHAR(32),
   r2letter VARCHAR(500),
   r3status VARCHAR(32),
   r3writer VARCHAR(32),
   r3email VARCHAR(32),
   r3title VARCHAR(32),
   r3affiliation VARCHAR(32),
   r3letter VARCHAR(500),
   PRIMARY KEY (startDate, uid)
);

DROP TABLE IF EXISTS review_form;
CREATE TABLE review_form (
   student_uid CHAR(8) NOT NULL,
   reviewer_uid CHAR(8) NOT NULL,
   r1rating INT(1) NOT NULL,
   r1generic VARCHAR(32) NOT NULL,
   r1credible VARCHAR(32) NOT NULL,
   r1from VARCHAR(32) NOT NULL,
   r2rating INT(1),
   r2generic VARCHAR(32),
   r2credible VARCHAR(32),
   r2from VARCHAR(32),
   r3rating INT(1),
   r3generic VARCHAR(32),
   r3credible VARCHAR(32),
   r3from VARCHAR(32),
   GASrating INT(1) NOT NULL,
   deficiencies VARCHAR(40),
   rejectReason VARCHAR(1),
   thoughts VARCHAR(40),
   semesterApplied VARCHAR(32) NOT NULL,
   decision VARCHAR(32) NOT NULL,
   PRIMARY KEY(student_uid, reviewer_uid),
   FOREIGN KEY (student_uid)
        REFERENCES applicant(uid) ON DELETE CASCADE,
   FOREIGN KEY (reviewer_uid) 
        REFERENCES employee(uid) ON DELETE CASCADE
);


SET FOREIGN_KEY_CHECKS = 1;