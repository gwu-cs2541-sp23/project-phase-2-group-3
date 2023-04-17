-- Active: 1679968300621@@apps10.c4sp2x9fdfly.us-east-1.rds.amazonaws.com@3306@apps10

use apps10;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
   userID INTEGER NOT NULL AUTO_INCREMENT,
   username VARCHAR(32) NOT NULL UNIQUE,
   userpass VARCHAR(32) NOT NULL,
   email VARCHAR(32) NOT NULL,
   usertype VARCHAR(32) NOT NULL,

   PRIMARY KEY (userID)

);
DROP TABLE IF EXISTS applicant;
-- add a reviewer table because students can have > 1 reviewers
-- have recommends table, to connect the reviewer table to a student
CREATE TABLE applicant (   
   studentID INT(8) NOT NULL,
   ssn INT(9) NOT NULL,
   appStatus VARCHAR(32) NOT NULL,
   recommended VARCHAR(32),
   username VARCHAR(32) NOT NULL,
   PRIMARY KEY (studentID, username),
   Foreign Key (username) REFERENCES users(username) ON DELETE CASCADE

);



DROP TABLE IF EXISTS reviewers;
CREATE TABLE reviewers (

   studentID INT(8) NOT NULL,
   reviewer VARCHAR(32) NOT NULL,

   PRIMARY KEY (studentID, reviewer),

   Foreign Key (reviewer) REFERENCES users(username) ON DELETE CASCADE, 
   Foreign Key (studentID) REFERENCES applicant(studentID) ON DELETE CASCADE

);



DROP TABLE IF EXISTS applicationForm;
-- decide whether a student can apply more than once
-- make sure that a recommender can submit the letter
-- make sure that a transcript can be uploaded
CREATE TABLE applicationForm (
   studentID INT(8) NOT NULL,
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
   PRIMARY KEY (startDate, studentID)
);


DROP TABLE IF EXISTS reviewForm;
CREATE TABLE reviewForm (
   studentID INT(8) NOT NULL,
   reviewer VARCHAR(32) NOT NULL,
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
   PRIMARY KEY(studentID, reviewer),
   Foreign Key (studentID) REFERENCES applicant(studentID) ON DELETE CASCADE
);

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO users VALUES ('1','Admin','AdminPass','admin@university.edu','Systems Administrator');
INSERT INTO users VALUES ('2','Secretary','SecretaryPass','secretary@university.edu','Graduate Secretary');
INSERT INTO users VALUES ('3','Chair','ChairPass','chair@university.edu','Chair');
INSERT INTO users VALUES ('4','Narahari','NarahariPass','narahari@university.edu','Faculty Reviewer');
INSERT INTO users VALUES ('5','John Lennon','JLPass','johnlennon@university.edu','Applicant');
INSERT INTO applicant VALUES ('12312312','111111111','Application Under Review','', 'John Lennon');
INSERT INTO applicationForm VALUES ('12312312','PHD','Yes','Comp Sci','2023','Duke','4.00','Yes','Comp Sci','2021','Georgetown','4.00','1500','1500','2023','1500','Physics','1500','01-23-45','None','fall 2023','No','No','Professor Taylor','taylor@gwu.edu','Professor of Computer Science','professor','letter.pdf','','','','','','','','','','','','');
INSERT INTO users VALUES ('6','Ringo Starr','RSPass','ringostarr@university.edu','Applicant');
INSERT INTO applicant VALUES ('66666666','222111111 ','Application Incomplete','', 'Ringo Starr');