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
    user_type varchar(16) NOT NULL, --possible choices: sysadmin, gradsec, employee, student, applicant, recommender
    PRIMARY KEY(uid)
);

DROP TABLE IF EXISTS students;
CREATE TABLE students (
    uid CHAR(8),
    degree_type varchar(4) NOT NULL, --possible choices: PHD or MS (hardcode those options into form, don't make a query)
    is_suspended BOOLEAN,
    thesis_approved BOOLEAN,
    applied_grad BOOLEAN,
    start_date varchar(16),
    PRIMARY KEY(uid),
    FOREIGN KEY(uid)
        REFERENCES users(uid) ON DELETE CASCADE
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
        REFERENCES users(uid) ON DELETE CASCADE
);

DROP TABLE IF EXISTS advisor_assignments;
CREATE TABLE advisor_assignments (
    advisor_uid CHAR(8),
    student_uid CHAR(8),
    PRIMARY KEY(advisor_uid, student_uid),
    FOREIGN KEY(advisor_uid)
        REFERENCES employee(uid) ON DELETE CASCADE,
    FOREIGN KEY(student_uid)
        REFERENCES users(uid) ON DELETE CASCADE
);

DROP TABLE IF EXISTS applicant;
CREATE TABLE applicant (   
   uid CHAR(8) NOT NULL,
   appStatus VARCHAR(32) NOT NULL, --Application Incomplete, Application Awaiting Materials, Application Under Review, Decision Pending, Decision Delivered
   decision VARCHAR(32) NOT NULL, -- Pending, Admit, Admit With Aid, Reject
   has_accepted BOOLEAN,
   has_paid BOOLEAN,
   PRIMARY KEY (uid),
   FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
);

DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni ( --student is deleted from students when they become an alum
	uid CHAR(8),
	grad_year int(4) NOT NULL,
    degree_type varchar(4) NOT NULL,
    email varchar(64) NOT NULL,
    PRIMARY KEY(uid),
	FOREIGN KEY (uid)
        REFERENCES users(uid) ON DELETE CASCADE
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
        REFERENCES classes(cid) ON DELETE CASCADE,
    FOREIGN KEY(professor_uid)
        REFERENCES employee(uid) ON DELETE CASCADE
);

DROP TABLE IF EXISTS prerequisites;
CREATE TABLE prerequisites (
    class_cid INTEGER,
    prereq_cid INTEGER,
    PRIMARY KEY(class_cid, prereq_cid),
    FOREIGN KEY(class_cid) 
        REFERENCES classes(cid) ON DELETE CASCADE,
    FOREIGN KEY(prereq_cid) 
        REFERENCES classes(cid) ON DELETE CASCADE
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
        REFERENCES students(uid) ON DELETE CASCADE,
    FOREIGN KEY(cid, section_id) 
        REFERENCES current_sections(cid, section_id) ON DELETE CASCADE
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
   transcriptstatus VARCHAR(32),
   transcriptpdf BLOB,
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

DROP TABLE IF EXISTS form1_answer;
CREATE TABLE form1_answer (
  student_uid int(8) NOT NULL,
  cid INTEGER NOT NULL
);

SET FOREIGN_KEY_CHECKS = 1;

--classes
INSERT INTO classes VALUES (1,'CSCI',6221,'SW Paradigms',3);
INSERT INTO classes VALUES (2,'CSCI',6461,'Computer Architecture',3);
INSERT INTO classes VALUES (3,'CSCI',6212,'Algorithms',3);
INSERT INTO classes VALUES (4,'CSCI',6220,'Machine Learning',3);
INSERT INTO classes VALUES (5,'CSCI',6232,'Networks 1',3);
INSERT INTO classes VALUES (6,'CSCI',6233,'Networks 2',3);
INSERT INTO classes VALUES (7,'CSCI',6241,'Database 1',3);
INSERT INTO classes VALUES (8,'CSCI',6242,'Database 2',3);
INSERT INTO classes VALUES (9,'CSCI',6246,'Compilers',3);
INSERT INTO classes VALUES (10,'CSCI',6260,'Multimedia',3);
INSERT INTO classes VALUES (11,'CSCI',6251,'Cloud Computing',3);
INSERT INTO classes VALUES (12,'CSCI',6254,'SW Engineering',3);
INSERT INTO classes VALUES (13,'CSCI',6262,'Graphics 1',3);
INSERT INTO classes VALUES (14,'CSCI',6283,'Security 1',3);
INSERT INTO classes VALUES (15,'CSCI',6284,'Cryptography',3);
INSERT INTO classes VALUES (16,'CSCI',6286,'Network Security',3);
INSERT INTO classes VALUES (17,'CSCI',6325,'Algorithms 2',3);
INSERT INTO classes VALUES (18,'CSCI',6339,'Embedded Systems',3);
INSERT INTO classes VALUES (19,'CSCI',6384,'Cryptography 2',3);
INSERT INTO classes VALUES (20,'ECE',6241,'Communication Theory',3);
INSERT INTO classes VALUES (21,'ECE',6242,'Information Theory',2);
INSERT INTO classes VALUES (22,'MATH',6210,'Logic',2);

--prerequisites
INSERT INTO prerequisites VALUES (6,5);
INSERT INTO prerequisites VALUES (8,7);
INSERT INTO prerequisites VALUES (9,2);
INSERT INTO prerequisites VALUES (9,3);
INSERT INTO prerequisites VALUES (11,2);
INSERT INTO prerequisites VALUES (12,1);
INSERT INTO prerequisites VALUES (14,3);
INSERT INTO prerequisites VALUES (15,3);
INSERT INTO prerequisites VALUES (16,14);
INSERT INTO prerequisites VALUES (16,5);
INSERT INTO prerequisites VALUES (17,3);
INSERT INTO prerequisites VALUES (18,2);
INSERT INTO prerequisites VALUES (18,3);
INSERT INTO prerequisites VALUES (19,15);

--users
INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000000', 'sysadmin', 'password', 'SYS', 'ADMIN', '000-00-0000', 'James Taylor University', 'sysadmin' );

INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '88888888', 'bholiday', 'password', 'Billie', 'Holiday', '001-02-0003', 'The Jazz Bar', 'student' );
INSERT INTO students ( uid, degree_type, is_suspended, thesis_approved, applied_grad, start_date ) VALUES ('88888888', 'MS', FALSE, FALSE, FALSE, 'Fall 2021' );
--add into her classes

INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '99999999', 'dkrall', 'password', 'Diana', 'Krall', '002-03-0004', 'The Piano Bench', 'student' );
INSERT INTO students ( uid, degree_type, is_suspended, thesis_approved, applied_grad, start_date ) VALUES ('99999999', 'MS', FALSE, FALSE, FALSE, 'Fall 2021' );


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000001', 'bnarahari', 'password', 'Bhaginarath', 'Narahari', '003-04-0005', 'The SEAS CS Department', 'employee' );
INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES ('00000001', TRUE, TRUE, FALSE, TRUE);


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000002', 'hchoi', 'password', 'Hyeong-Ah', 'Choi', '004-05-0006', 'The SEAS CS Department', 'employee' );
INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES ('00000002', TRUE, FALSE, FALSE, FALSE);


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '12312312', 'jlennon', 'password', 'John', 'Lennon', '111-11-1111', 'A Yellow Submarine', 'applicant' );
INSERT INTO applicant (uid, `appStatus`, decision, has_accepted, has_paid) VALUES ('12312312', 'Application Under Review', 'Pending', FALSE, TRUE);
INSERT INTO applicationForm VALUES ('12312312','PHD','Yes','Comp Sci','2023','Duke','4.00','Yes','Comp Sci','2021','Georgetown','4.00','140','140','2023','140','Physics','120','2023','None','Fall 2023','Recieved','transcript.pdf','Recieved','Professor Taylor','taylor@gwu.edu','Professor of Computer Science','professor','what a great kid','','','','','','','','','','','','');


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '66666666', 'rstarr', 'password', 'Ringo', 'Starr', '222-11-1111', 'In the Sky with Diamonds', 'applicant' );
INSERT INTO applicant (uid, `appStatus`, decision, has_accepted, has_paid) VALUES ('66666666', 'Application Incomplete', 'Pending', FALSE, FALSE);


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000003', 'mparrish', 'password', 'Mark', 'Parrish', '005-06-0007', 'JBKO Hall', 'gradsec' );


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000004', 'sgarrity', 'password', 'Sheila', 'Garrity', '006-07-0008', 'The Townhouses', 'employee' );
INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES ('00000004', FALSE, FALSE, TRUE, FALSE);


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000005', 'twood', 'password', 'Tim', 'Wood', '008-09-0010', 'The SEAS CS Department', 'employee' );
INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES ('00000005', FALSE, FALSE, FALSE, TRUE);

INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000006', 'rheller', 'password', 'Rachelle', 'Heller', '009-10-0011', 'The SEAS CS Department', 'employee' );
INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES ('00000006', FALSE, FALSE, FALSE, TRUE);


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '55555555', 'pmccartney', 'password', 'Paul', 'McCartney', '010-11-0012', 'Sgt. Pepper\'s Lonely Hearts Club', 'student' );
INSERT INTO students ( uid, degree_type, is_suspended, thesis_approved, applied_grad, start_date ) VALUES ('55555555', 'MS', FALSE, FALSE, FALSE, 'Spring 2021' );
-- add classes and grades


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '66666667', 'gharrison', 'password', 'George', 'Harrison', '011-12-0013', 'The Sun', 'student' );
INSERT INTO students ( uid, degree_type, is_suspended, thesis_approved, applied_grad, start_date ) VALUES ('66666667', 'MS', FALSE, FALSE, FALSE, 'Spring 2021' );
-- add classes and grades


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000007', 'rstarr2', 'password', 'Ringo', 'Starr2', '012-13-0014', 'In the Sky with Diamonds, as well', 'student' );
INSERT INTO students ( uid, degree_type, is_suspended, thesis_approved, applied_grad, start_date ) VALUES ('00000007', 'PHD', FALSE, FALSE, FALSE, 'Spring 2020' );
-- add classes, grades, thesis stuff?


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '77777777', 'eclapton', 'password', 'Eric', 'Clapton', '013-14-0015', 'Ripley, UK', 'alumni' );
INSERT INTO alumni (uid, grad_year, degree_type, email) VALUES ('77777777', 'Spring 2014', 'MS', 'eclapton@jtu.edu');
-- add classes, grades, thesis stuff?


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000008', 'gparmer', 'password', 'Gabriel', 'Parmer', '015-16-0017', 'The SEAS CS Department', 'employee' );
INSERT INTO employee (uid, is_professor, is_advisor, is_review_chair, is_reviewer) VALUES ('00000008', FALSE, FALSE, TRUE, FALSE);


INSERT INTO users ( uid, username, password, first_name, last_name, ssn, address, user_type ) VALUES ( '00000009', 'zrahbar', 'password', 'Zack', 'Rahbar', '016-17-0018', 'Shenkman Hall', 'recommender' );

--advisors
-- Narahari and McCartney
INSERT INTO advisor_assignments VALUES ('00000001', '55555555');
-- Parmer and Harrison
INSERT INTO advisor_assignments VALUES ('00000008', '66666667');
-- Parmer and Ringo2
INSERT INTO advisor_assignments VALUES ('00000008', '00000007');


--sections
-- 2014 1
INSERT INTO current_sections VALUES (1,'2014-1-1-1','00000001',2014,1,'M',1);
INSERT INTO current_sections VALUES (2,'2014-1-2-1','00000001',2014,1,'T',1);
INSERT INTO current_sections VALUES (3,'2014-1-3-1','00000002',2014,1,'W',1);
INSERT INTO current_sections VALUES (4,'2014-1-4-1','00000002',2014,1,'W',1);
INSERT INTO current_sections VALUES (5,'2014-1-5-1','00000001',2014,1,'M',3);
INSERT INTO current_sections VALUES (6,'2014-1-6-1','00000001',2014,1,'T',3);
INSERT INTO current_sections VALUES (7,'2014-1-7-1','00000001',2014,1,'W',3);
INSERT INTO current_sections VALUES (8,'2014-1-8-1','00000001',2014,1,'R',3);
INSERT INTO current_sections VALUES (9,'2014-1-9-1','00000002',2014,1,'T',1);
INSERT INTO current_sections VALUES (11,'2014-1-11-1','00000002',2014,1,'M',3);
INSERT INTO current_sections VALUES (12,'2014-1-12-1','00000002',2014,1,'M',1);
INSERT INTO current_sections VALUES (10,'2014-1-10-1','00000002',2014,1,'R',3);
INSERT INTO current_sections VALUES (13,'2014-1-13-1','00000002',2014,1,'W',3);
INSERT INTO current_sections VALUES (14,'2014-1-14-1','00000002',2014,1,'T',3);
INSERT INTO current_sections VALUES (15,'2014-1-15-1','00000001',2014,1,'M',3);
INSERT INTO current_sections VALUES (16,'2014-1-16-1','00000001',2014,1,'W',3);
INSERT INTO current_sections VALUES (19,'2014-1-19-1','00000001',2014,1,'W',1);
INSERT INTO current_sections VALUES (20,'2014-1-20-1','00000002',2014,1,'M',3);
INSERT INTO current_sections VALUES (21,'2014-1-21-1','00000002',2014,1,'T',3);
INSERT INTO current_sections VALUES (22,'2014-1-22-1','00000002',2014,1,'W',3);
INSERT INTO current_sections VALUES (18,'2014-1-18-1','00000002',2014,1,'R',2);

-- 2023 1
INSERT INTO current_sections VALUES (1,'2023-1-1-1','00000001',2023,1,'M',1);
INSERT INTO current_sections VALUES (2,'2023-1-2-1','00000001',2023,1,'T',1);
INSERT INTO current_sections VALUES (3,'2023-1-3-1','00000002',2023,1,'W',1);
INSERT INTO current_sections VALUES (4,'2023-1-4-1','00000002',2023,1,'W',1);
INSERT INTO current_sections VALUES (5,'2023-1-5-1','00000001',2023,1,'M',3);
INSERT INTO current_sections VALUES (6,'2023-1-6-1','00000001',2023,1,'T',3);
INSERT INTO current_sections VALUES (7,'2023-1-7-1','00000001',2023,1,'W',3);
INSERT INTO current_sections VALUES (8,'2023-1-8-1','00000001',2023,1,'R',3);
INSERT INTO current_sections VALUES (9,'2023-1-9-1','00000002',2023,1,'T',1);
INSERT INTO current_sections VALUES (11,'2023-1-11-1','00000002',2023,1,'M',3);
INSERT INTO current_sections VALUES (12,'2023-1-12-1','00000002',2023,1,'M',1);
INSERT INTO current_sections VALUES (10,'2023-1-10-1','00000002',2023,1,'R',3);
INSERT INTO current_sections VALUES (13,'2023-1-13-1','00000002',2023,1,'W',3);
INSERT INTO current_sections VALUES (14,'2023-1-14-1','00000002',2023,1,'T',3);
INSERT INTO current_sections VALUES (15,'2023-1-15-1','00000001',2023,1,'M',3);
INSERT INTO current_sections VALUES (16,'2023-1-16-1','00000001',2023,1,'W',3);
INSERT INTO current_sections VALUES (19,'2023-1-19-1','00000001',2023,1,'W',1);
INSERT INTO current_sections VALUES (20,'2023-1-20-1','00000002',2023,1,'M',3);
INSERT INTO current_sections VALUES (21,'2023-1-21-1','00000002',2023,1,'T',3);
INSERT INTO current_sections VALUES (22,'2023-1-22-1','00000002',2023,1,'W',3);
INSERT INTO current_sections VALUES (18,'2023-1-18-1','00000002',2023,1,'R',2);

-- 2023 2
INSERT INTO current_sections VALUES (1,'2023-2-1-1','00000001',2023,2,'M',1);
INSERT INTO current_sections VALUES (2,'2023-2-2-1','00000001',2023,2,'T',1);
INSERT INTO current_sections VALUES (3,'2023-2-3-1','00000001',2023,2,'W',1);
INSERT INTO current_sections VALUES (5,'2023-2-5-1','00000001',2023,2,'M',3);
INSERT INTO current_sections VALUES (6,'2023-2-6-1','00000001',2023,2,'T',3);
INSERT INTO current_sections VALUES (7,'2023-2-7-1','00000001',2023,2,'W',3);
INSERT INTO current_sections VALUES (8,'2023-2-8-1','00000001',2023,2,'R',3);
INSERT INTO current_sections VALUES (9,'2023-2-9-1','00000002',2023,2,'T',1);
INSERT INTO current_sections VALUES (11,'2023-2-11-1','00000002',2023,2,'M',3);
INSERT INTO current_sections VALUES (12,'2023-2-12-1','00000002',2023,2,'M',1);
INSERT INTO current_sections VALUES (10,'2023-2-10-1','00000002',2023,2,'R',3);
INSERT INTO current_sections VALUES (13,'2023-2-13-1','00000002',2023,2,'W',3);
INSERT INTO current_sections VALUES (14,'2023-2-14-1','00000002',2023,2,'T',3);
INSERT INTO current_sections VALUES (15,'2023-2-15-1','00000001',2023,2,'M',3);
INSERT INTO current_sections VALUES (16,'2023-2-16-1','00000001',2023,2,'W',3);
INSERT INTO current_sections VALUES (19,'2023-2-19-1','00000001',2023,2,'W',1);
INSERT INTO current_sections VALUES (20,'2023-2-20-1','00000002',2023,2,'M',3);
INSERT INTO current_sections VALUES (21,'2023-2-21-1','00000002',2023,2,'T',3);
INSERT INTO current_sections VALUES (22,'2023-2-22-1','00000002',2023,2,'W',3);
INSERT INTO current_sections VALUES (18,'2023-2-18-1','00000002',2023,2,'R',2);

-- 2023 3
INSERT INTO current_sections VALUES (1,'2023-3-1-1','00000001',2023,3,'M',1);
INSERT INTO current_sections VALUES (2,'2023-3-2-1','00000001',2023,3,'T',1);
INSERT INTO current_sections VALUES (3,'2023-3-3-1','00000001',2023,3,'W',1);
INSERT INTO current_sections VALUES (5,'2023-3-5-1','00000001',2023,3,'M',3);
INSERT INTO current_sections VALUES (6,'2023-3-6-1','00000001',2023,3,'T',3);
INSERT INTO current_sections VALUES (7,'2023-3-7-1','00000001',2023,3,'W',3);
INSERT INTO current_sections VALUES (8,'2023-3-8-1','00000001',2023,3,'R',3);
INSERT INTO current_sections VALUES (9,'2023-3-9-1','00000002',2023,3,'T',1);
INSERT INTO current_sections VALUES (11,'2023-3-11-1','00000002',2023,3,'M',3);
INSERT INTO current_sections VALUES (12,'2023-3-12-1','00000002',2023,3,'M',1);
INSERT INTO current_sections VALUES (10,'2023-3-10-1','00000002',2023,3,'R',3);
INSERT INTO current_sections VALUES (13,'2023-3-13-1','00000002',2023,3,'W',3);
INSERT INTO current_sections VALUES (14,'2023-3-14-1','00000002',2023,3,'T',3);
INSERT INTO current_sections VALUES (15,'2023-3-15-1','00000001',2023,3,'M',3);
INSERT INTO current_sections VALUES (16,'2023-3-16-1','00000001',2023,3,'W',3);
INSERT INTO current_sections VALUES (19,'2023-3-19-1','00000001',2023,3,'W',1);
INSERT INTO current_sections VALUES (20,'2023-3-20-1','00000002',2023,3,'M',3);
INSERT INTO current_sections VALUES (21,'2023-3-21-1','00000002',2023,3,'T',3);
INSERT INTO current_sections VALUES (22,'2023-3-22-1','00000002',2023,3,'W',3);
INSERT INTO current_sections VALUES (18,'2023-3-18-1','00000002',2023,3,'R',2);


-- 2024 1
INSERT INTO current_sections VALUES (1,'2024-1-1-1','00000001',2024,1,'M',1);
INSERT INTO current_sections VALUES (2,'2024-1-2-1','00000001',2024,1,'T',1);
INSERT INTO current_sections VALUES (3,'2024-1-3-1','00000001',2024,1,'W',1);
INSERT INTO current_sections VALUES (5,'2024-1-5-1','00000001',2024,1,'M',3);
INSERT INTO current_sections VALUES (6,'2024-1-6-1','00000001',2024,1,'T',3);
INSERT INTO current_sections VALUES (7,'2024-1-7-1','00000001',2024,1,'W',3);
INSERT INTO current_sections VALUES (8,'2024-1-8-1','00000001',2024,1,'R',3);
INSERT INTO current_sections VALUES (9,'2024-1-9-1','00000002',2024,1,'T',1);
INSERT INTO current_sections VALUES (11,'2024-1-11-1','00000002',2024,1,'M',3);
INSERT INTO current_sections VALUES (12,'2024-1-12-1','00000002',2024,1,'M',1);
INSERT INTO current_sections VALUES (10,'2024-1-10-1','00000002',2024,1,'R',3);
INSERT INTO current_sections VALUES (13,'2024-1-13-1','00000002',2024,1,'W',3);
INSERT INTO current_sections VALUES (14,'2024-1-14-1','00000002',2024,1,'T',3);
INSERT INTO current_sections VALUES (15,'2024-1-15-1','00000001',2024,1,'M',3);
INSERT INTO current_sections VALUES (16,'2024-1-16-1','00000001',2024,1,'W',3);
INSERT INTO current_sections VALUES (19,'2024-1-19-1','00000001',2024,1,'W',1);
INSERT INTO current_sections VALUES (20,'2024-1-20-1','00000002',2024,1,'M',3);
INSERT INTO current_sections VALUES (21,'2024-1-21-1','00000002',2024,1,'T',3);
INSERT INTO current_sections VALUES (22,'2024-1-22-1','00000002',2024,1,'W',3);
INSERT INTO current_sections VALUES (18,'2024-1-18-1','00000002',2024,1,'R',2);

-- 2024 2
INSERT INTO current_sections VALUES (1,'2024-2-1-1','00000001',2024,2,'M',1);
INSERT INTO current_sections VALUES (2,'2024-2-2-1','00000001',2024,2,'T',1);
INSERT INTO current_sections VALUES (3,'2024-2-3-1','00000001',2024,2,'W',1);
INSERT INTO current_sections VALUES (5,'2024-2-5-1','00000001',2024,2,'M',3);
INSERT INTO current_sections VALUES (6,'2024-2-6-1','00000001',2024,2,'T',3);
INSERT INTO current_sections VALUES (7,'2024-2-7-1','00000001',2024,2,'W',3);
INSERT INTO current_sections VALUES (8,'2024-2-8-1','00000001',2024,2,'R',3);
INSERT INTO current_sections VALUES (9,'2024-2-9-1','00000002',2024,2,'T',1);
INSERT INTO current_sections VALUES (11,'2024-2-11-1','00000002',2024,2,'M',3);
INSERT INTO current_sections VALUES (12,'2024-2-12-1','00000002',2024,2,'M',1);
INSERT INTO current_sections VALUES (10,'2024-2-10-1','00000002',2024,2,'R',3);
INSERT INTO current_sections VALUES (13,'2024-2-13-1','00000002',2024,2,'W',3);
INSERT INTO current_sections VALUES (14,'2024-2-14-1','00000002',2024,2,'T',3);
INSERT INTO current_sections VALUES (15,'2024-2-15-1','00000001',2024,2,'M',3);
INSERT INTO current_sections VALUES (16,'2024-2-16-1','00000001',2024,2,'W',3);
INSERT INTO current_sections VALUES (19,'2024-2-19-1','00000001',2024,2,'W',1);
INSERT INTO current_sections VALUES (20,'2024-2-20-1','00000002',2024,2,'M',3);
INSERT INTO current_sections VALUES (21,'2024-2-21-1','00000002',2024,2,'T',3);
INSERT INTO current_sections VALUES (22,'2024-2-22-1','00000002',2024,2,'W',3);
INSERT INTO current_sections VALUES (18,'2024-2-18-1','00000002',2024,2,'R',2);

-- 2024 3
INSERT INTO current_sections VALUES (1,'2024-3-1-1','00000001',2024,3,'M',1);
INSERT INTO current_sections VALUES (2,'2024-3-2-1','00000001',2024,3,'T',1);
INSERT INTO current_sections VALUES (3,'2024-3-3-1','00000001',2024,3,'W',1);
INSERT INTO current_sections VALUES (5,'2024-3-5-1','00000001',2024,3,'M',3);
INSERT INTO current_sections VALUES (6,'2024-3-6-1','00000001',2024,3,'T',3);
INSERT INTO current_sections VALUES (7,'2024-3-7-1','00000001',2024,3,'W',3);
INSERT INTO current_sections VALUES (8,'2024-3-8-1','00000001',2024,3,'R',3);
INSERT INTO current_sections VALUES (9,'2024-3-9-1','00000002',2024,3,'T',1);
INSERT INTO current_sections VALUES (11,'2024-3-11-1','00000002',2024,3,'M',3);
INSERT INTO current_sections VALUES (12,'2024-3-12-1','00000002',2024,3,'M',1);
INSERT INTO current_sections VALUES (10,'2024-3-10-1','00000002',2024,3,'R',3);
INSERT INTO current_sections VALUES (13,'2024-3-13-1','00000002',2024,3,'W',3);
INSERT INTO current_sections VALUES (14,'2024-3-14-1','00000002',2024,3,'T',3);
INSERT INTO current_sections VALUES (15,'2024-3-15-1','00000001',2024,3,'M',3);
INSERT INTO current_sections VALUES (16,'2024-3-16-1','00000001',2024,3,'W',3);
INSERT INTO current_sections VALUES (19,'2024-3-19-1','00000001',2024,3,'W',1);
INSERT INTO current_sections VALUES (20,'2024-3-20-1','00000002',2024,3,'M',3);
INSERT INTO current_sections VALUES (21,'2024-3-21-1','00000002',2024,3,'T',3);
INSERT INTO current_sections VALUES (22,'2024-3-22-1','00000002',2024,3,'W',3);
INSERT INTO current_sections VALUES (18,'2024-3-18-1','00000002',2024,3,'R',2);


-- student classes
-- Billie Holiday
INSERT INTO student_classes VALUES ('88888888','2','2023-2-2-1','IP',0);
INSERT INTO student_classes VALUES ('88888888','3','2023-2-3-1','IP',0);

-- Paul McCartney 
INSERT INTO student_classes VALUES ('55555555','1','2023-1-1-1','A',1);
INSERT INTO student_classes VALUES ('55555555','2','2023-1-2-1','A',1);
INSERT INTO student_classes VALUES ('55555555','3','2023-1-3-1','A',1);
INSERT INTO student_classes VALUES ('55555555','5','2023-1-5-1','A',1);
INSERT INTO student_classes VALUES ('55555555','6','2023-1-6-1','A',1);
INSERT INTO student_classes VALUES ('55555555','7','2023-1-7-1','B',1);
INSERT INTO student_classes VALUES ('55555555','9','2023-1-9-1','B',1);
INSERT INTO student_classes VALUES ('55555555','13','2023-1-13-1','B',1);
INSERT INTO student_classes VALUES ('55555555','14','2023-1-14-1','B',1);
INSERT INTO student_classes VALUES ('55555555','8','2023-1-8-1','B',1);

--George Harrison
INSERT INTO student_classes VALUES ('66666667','21','2023-1-21-1','C',1);
INSERT INTO student_classes VALUES ('66666667','1','2023-1-1-1','B',1);
INSERT INTO student_classes VALUES ('66666667','2','2023-1-2-1','B',1);
INSERT INTO student_classes VALUES ('66666667','3','2023-1-3-1','B',1);
INSERT INTO student_classes VALUES ('66666667','5','2023-1-5-1','B',1);
INSERT INTO student_classes VALUES ('66666667','6','2023-1-6-1','B',1);
INSERT INTO student_classes VALUES ('66666667','7','2023-1-7-1','B',1);
INSERT INTO student_classes VALUES ('66666667','8','2023-1-8-1','B',1);
INSERT INTO student_classes VALUES ('66666667','14','2023-1-14-1','B',1);
INSERT INTO student_classes VALUES ('66666667','15','2023-1-15-1','B',1);

--Ringo Starr2
INSERT INTO student_classes VALUES ('00000007','1','2023-1-1-1','A',1);
INSERT INTO student_classes VALUES ('00000007','2','2023-1-2-1','A',1);
INSERT INTO student_classes VALUES ('00000007','3','2023-1-3-1','A',1);
INSERT INTO student_classes VALUES ('00000007','4','2023-1-4-1','A',1);
INSERT INTO student_classes VALUES ('00000007','5','2023-1-5-1','A',1);
INSERT INTO student_classes VALUES ('00000007','6','2023-1-6-1','A',1);
INSERT INTO student_classes VALUES ('00000007','7','2023-1-7-1','A',1);
INSERT INTO student_classes VALUES ('00000007','8','2023-1-8-1','A',1);
INSERT INTO student_classes VALUES ('00000007','9','2023-1-9-1','A',1);
INSERT INTO student_classes VALUES ('00000007','10','2023-1-10-1','A',1);
INSERT INTO student_classes VALUES ('00000007','11','2023-1-11-1','A',1);
INSERT INTO student_classes VALUES ('00000007','12','2023-1-12-1','A',1);

-- Eric Clapton
INSERT INTO student_classes VALUES ('77777777','1','2014-1-1-1','B',1);
INSERT INTO student_classes VALUES ('77777777','3','2014-1-3-1','B',1);
INSERT INTO student_classes VALUES ('77777777','2','2014-1-2-1','B',1);
INSERT INTO student_classes VALUES ('77777777','5','2014-1-5-1','B',1);
INSERT INTO student_classes VALUES ('77777777','6','2014-1-6-1','B',1);
INSERT INTO student_classes VALUES ('77777777','7','2014-1-7-1','B',1);
INSERT INTO student_classes VALUES ('77777777','8','2014-1-8-1','B',1);
INSERT INTO student_classes VALUES ('77777777','14','2014-1-14-1','A',1);
INSERT INTO student_classes VALUES ('77777777','15','2014-1-15-1','A',1);
INSERT INTO student_classes VALUES ('77777777','16','2014-1-16-1','A',1);



