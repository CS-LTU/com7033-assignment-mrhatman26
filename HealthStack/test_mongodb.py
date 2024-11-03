import pytest
from mongodb import *

class TempPatient():
    def __init__(self):
        self.mysql_id = -1
        self.gender = "MALE"
        self.age = "24"
        self.hyperT = 0 
        self.hDisease = 0 
        self.married = 0
        self.work_type = "PRIVATE"
        self.residence_type = "RURAL"
        self.avg_gLevel = "80"
        self.bmi = "25"
        self.smoked = "NEVER SMOKED" 
        self.stroke = 0
        self.alt_gender = "FEMALE"
        self.alt_age = "42"
        self.alt_hyperT = 0 
        self.alt_hDisease = 0 
        self.alt_married = 0
        self.alt_work_type = "CHILDREN"
        self.alt_residence_type = "URBAN"
        self.alt_avg_gLevel = "90"
        self.alt_bmi = "22"
        self.alt_smoked = "NEVER SMOKED" 
        self.alt_stroke = 0
        self.creation_dict = {"MySQL_ID": self.mysql_id, "patient_gender": self.gender, "patient_age": self.age, "patient_hyperT": self.hyperT, "patient_hDisease": self.hDisease, "patient_married": self.married, "patient_work_type": self.work_type, "patient_residence_type": self.residence_type, "patient_avg_gLevel": self.avg_gLevel, "patient_bmi": self.bmi, "patient_smoked": self.smoked, "patient_stroke": self.stroke}
        self.modify_dict = {"MySQL_ID": self.mysql_id,"patient_gender": self.alt_gender, "patient_age": self.alt_age, "patient_hyperT": self.alt_hyperT, "patient_hDisease": self.alt_hDisease, "patient_married": self.alt_married, "patient_work_type": self.alt_work_type, "patient_residence_type": self.alt_residence_type, "patient_avg_gLevel": self.alt_avg_gLevel, "patient_bmi": self.alt_bmi, "patient_smoked": self.alt_smoked, "patient_stroke": self.alt_stroke}
        self.id = None

def create_temp_patient(insert, m_client):
    temp_patient = TempPatient()
    if insert is True:
        temp_patient.id = mongo_insert(temp_patient.creation_dict, m_client)
    return temp_patient

def delete_temp_patient(temp_patient, m_client):
    mongo_delete({"MySQL_ID": temp_patient.mysql_id}, m_client)

def test_mongo_insert():
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    temp_patient = create_temp_patient(True, m_client)
    user_insert = False
    for patient in mongo_find_all(True, m_client):
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            user_insert = True
    assert user_insert is True
    delete_temp_patient(temp_patient, m_client)
    del temp_patient
    m_client.close()
    del m_client

def test_mongo_find_all():
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    temp_patient = create_temp_patient(True, m_client)
    for patient in mongo_find_all(True, m_client):
        assert patient["patient_gender"] is not None
        assert patient["patient_age"] is not None
        assert patient["patient_hyperT"] is not None
        assert patient["patient_hDisease"] is not None
        assert patient["patient_married"] is not None
        assert patient["patient_work_type"] is not None
        assert patient["patient_residence_type"] is not None
        assert patient["patient_avg_gLevel"] is not None
        assert type(patient["patient_bmi"]) == str or patient["patient_bmi"] is None
        assert patient["patient_smoked"] is not None
        assert patient["patient_stroke"] is not None
        assert patient["MySQL_ID"] is not None
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            assert patient["patient_gender"] == temp_patient.gender
            assert patient["patient_age"] == temp_patient.age
            assert patient["patient_hyperT"] == temp_patient.hyperT
            assert patient["patient_hDisease"] == temp_patient.hDisease
            assert patient["patient_married"] == temp_patient.married
            assert patient["patient_work_type"] == temp_patient.work_type
            assert patient["patient_residence_type"] == temp_patient.residence_type
            assert patient["patient_avg_gLevel"] == temp_patient.avg_gLevel
            assert patient["patient_bmi"] == temp_patient.bmi
            assert patient["patient_smoked"] == temp_patient.smoked
            assert patient["patient_stroke"] == temp_patient.stroke
    delete_temp_patient(temp_patient, m_client)
    del temp_patient
    m_client.close()
    del m_client

def test_mongo_delete():
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    temp_patient = create_temp_patient(True, m_client)
    user_insert = False
    for patient in mongo_find_all(True, m_client):
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            user_insert = True
    assert user_insert is True
    mongo_delete({"MySQL_ID": temp_patient.mysql_id}, m_client)
    user_deleted = True
    for patient in mongo_find_all(True, m_client):
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            user_deleted = False
    assert user_insert is True
    delete_temp_patient(temp_patient, m_client)
    del temp_patient
    m_client.close()
    del m_client

def test_mongo_update():
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    temp_patient = create_temp_patient(True, m_client)
    user_insert = False
    for patient in mongo_find_all(True, m_client):
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            user_insert = True
    assert user_insert is True
    user_insert = False
    mongo_update({"MySQL_ID": temp_patient.mysql_id}, temp_patient.modify_dict, m_client)
    for patient in mongo_find_all(True, m_client):
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            assert patient["patient_gender"] == temp_patient.alt_gender
            user_insert = True
    assert user_insert is True
    user_insert = False
    mongo_update({"MySQL_ID": temp_patient.mysql_id}, temp_patient.creation_dict, m_client)
    for patient in mongo_find_all(True, m_client):
        if patient["MySQL_ID"] == temp_patient.mysql_id:
            assert patient["patient_gender"] == temp_patient.gender
            user_insert = True
    assert user_insert is True
    delete_temp_patient(temp_patient, m_client)
    del temp_patient
    m_client.close()
    del m_client