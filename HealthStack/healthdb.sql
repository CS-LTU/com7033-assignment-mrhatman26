DROP DATABASE IF EXISTS healthDB; /*If the database already exists, drop it*/
CREATE DATABASE healthDB; /*Create the database*/
USE healthDB; /*Use the created database*/
DROP TABLE IF EXISTS table_users; /*If table_users exists, drop it*/
CREATE TABLE table_users(
    user_id INT NOT NULL,
    user_fullname TEXT NOT NULL,
    user_password TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_phone TEXT NOT NULL,
    user_admin BOOLEAN NOT NULL,
    PRIMARY KEY (user_id)
); /*Create table_users and set the primary key to be the user_id*/
/*This table holds all users*/

DROP TABLE IF EXISTS table_patient_data; /*If table_patient_data exists, drop it*/
CREATE TABLE table_patient_data(
    patient_id INT NOT NULL,
    patient_gender TEXT NOT NULL,
    patient_age INT NOT NULL,
    patient_hyperT BOOLEAN NOT NULL,
    patient_hDisease BOOLEAN NOT NULL,
    patient_married BOOLEAN NOT NULL,
    patient_work_type TEXT NOT NULL,
    patient_residence_type TEXT NOT NULL,
    patient_avg_gLevel FLOAT NOT NULL,
    patient_bmi FLOAT,
    patient_smoked TEXT NOT NULL,
    patient_stroke BOOLEAN NOT NULL,
    PRIMARY KEY (patient_id) 
); /*Create table_patient_data and set the primary key to be patient_id*/
/*This table holds all of the patient data*/

DROP TABLE IF EXISTS link_user_patient_data; /*If link_user_patient_data exists, drop it*/
CREATE TABLE link_user_patient_data(
    user_id INT NOT NULL,
    patient_id INT NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY(user_id) REFERENCES table_users(user_id),
    FOREIGN KEY(patient_id) REFERENCES table_patient_data(patient_id)
); /*Creae link_user_patient_data and set the primary key to be the user_id and link user_id and patient_id to their corresponding values in the other two tables*/
/*This table holds all links between users and patients*/

INSERT INTO table_users VALUES(
    0, "BaseAdmin", "-1", "baseadmin@example.com", "N/A", 1
); /*Create the BaseAdmin*/