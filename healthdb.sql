DROP DATABASE IF EXISTS healthDB;
CREATE DATABASE healthDB;
DROP TABLE IF EXISTS table_users;
CREATE TABLE table_users(
    user_id INT NOT NULL,
    user_name TEXT NOT NULL,
    user_fullname TEXT NOT NULL,
    user_password INT NOT NULL,
    user_email TEXT NOT NULL,
    user_phone TEXT NOT NULL,
    user_admin BOOLEAN NOT NULL,
    PRIMARY KEY (user_id)
);

DROP TABLE IF EXISTS table_patient_data;
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
    patient_smoked INT NOT NULL,
    patient_stroke BOOLEAN NOT NULL,
    PRIMARY KEY (patient_id) 
);

DROP TABLE IF EXISTS link_user_patient_data;
CREATE TABLE link_user_patient_data(
    user_id INT NOT NULL,
    patient_id INT NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY(user_id) REFERENCES table_users(user_id),
    FOREIGN KEY(patient_id) REFERENCES table_patient_data(patient_id)
);