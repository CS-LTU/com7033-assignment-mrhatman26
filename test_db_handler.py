import pytest
import mysql.connector
from db_handler import *
from db_config import get_db_config

#Before running these tests, please make sure the database has been started.

class TempUser():
    def __init__(self):
        self.name = "TestUser"
        self.password = "TestPassword"
        self.email = "TestUser@example.com"
        self.phone = "07234 928184"
        self.alt_name = "UserTest"
        self.alt_email = "UserTest@example.co.uk"
        self.alt_password = "alt_password"
        self.alt_phone = "07555 777777"
        self.creation_dict = {"fullname": self.name, "email": self.email, "password": self.password, "phone": self.phone}
        self.modify_dict = {"fullname": self.alt_name, "email": self.alt_email, "password": self.alt_password, "phone": self.alt_phone}
        self.id = None

class TempPatient():
    def __init__(self):
        self.gender = "MALE"
        self.age = 24
        self.hyperT = 0 
        self.hDisease = 0 
        self.married = 0
        self.work_type = "PRIVATE"
        self.residence_type = "RURAL"
        self.avg_gLevel = 80
        self.bmi = 25
        self.smoked = "NEVER SMOKED" 
        self.stroke = 0
        self.alt_gender = "FEMALE"
        self.alt_age = 42
        self.alt_hyperT = 0 
        self.alt_hDisease = 0 
        self.alt_married = 0
        self.alt_work_type = "CHILDREN"
        self.alt_residence_type = "URBAN"
        self.alt_avg_gLevel = 90
        self.alt_bmi = 22
        self.alt_smoked = "NEVER SMOKED" 
        self.alt_stroke = 0
        self.creation_dict = {"patient_gender": self.gender, "patient_age": self.age, "patient_hyperT": self.hyperT, "patient_hDisease": self.hDisease, "patient_married": self.married, "patient_work_type": self.work_type, "patient_residence_type": self.residence_type, "patient_avg_gLevel": self.avg_gLevel, "patient_bmi": self.bmi, "patient_smoked": self.smoked, "patient_stroke": self.stroke}
        self.modify_dict = {"patient_gender": self.alt_gender, "patient_age": self.alt_age, "patient_hyperT": self.alt_hyperT, "patient_hDisease": self.alt_hDisease, "patient_married": self.alt_married, "patient_work_type": self.alt_work_type, "patient_residence_type": self.alt_residence_type, "patient_avg_gLevel": self.alt_avg_gLevel, "patient_bmi": self.alt_bmi, "patient_smoked": self.alt_smoked, "patient_stroke": self.alt_stroke}
        self.id = None


def create_temp_user():
    temp_user = TempUser()
    user_create(temp_user.creation_dict)
    temp_user.id = user_get_id(temp_user.email)
    return temp_user

def create_temp_patient(insert):
    temp_patient = TempPatient()
    if insert is True:
        temp_patient.id = insert_patient_data(temp_patient.creation_dict)
    return temp_patient    

def delete_temp_user(temp_user):
    admin_delete_user(temp_user.id)

def delete_temp_patient(temp_patient):
    admin_delete_patient_data(temp_patient.id)

def test_str_to_bool():
    assert str_to_bool("Yes") is True
    assert str_to_bool("No") is False


def test_user_check_exists():
    assert user_check_exists("28975827893276468932987687051273984672901587") is False
    temp_user = create_temp_user()
    assert user_check_exists(temp_user.email) is True
    delete_temp_user(temp_user)
    del temp_user

def test_user_check_reconfirm():
    assert user_check_reconfirm(-1) is None or user_check_reconfirm(-1) == []
    temp_user = create_temp_user()
    assert user_check_reconfirm(temp_user.id)[0] == temp_user.id
    delete_temp_user(temp_user)
    del temp_user

def test_user_check_validate():
    assert user_check_validate({"username": "28975827893276468932987687051273984672901587", "password": "NothingToSeeHere"}) is False
    temp_user = create_temp_user()
    assert user_check_validate({"username": temp_user.email, "password": "NothingToSeeHere"}) is False
    assert user_check_validate({"username": "NothingToSeeHere", "password": temp_user.password}) is False
    assert user_check_validate({"username": temp_user.email, "password": temp_user.password}) is True
    delete_temp_user(temp_user)
    del temp_user

def test_user_get_amount():
    assert type(user_get_amount()) == int and user_get_amount() >= 0

def test_user_get_last_id():
    assert type(user_get_last_id()) == int
    temp_user = create_temp_user()
    assert user_get_last_id() == temp_user.id + 1
    delete_temp_user(temp_user)
    del temp_user

def test_user_get_id():
    assert user_get_id("28975827893276468932987687051273984672901587") is None
    temp_user = create_temp_user()
    assert user_get_id(temp_user.email) == temp_user.id
    delete_temp_user(temp_user)
    del temp_user

def test_user_get_all():
    assert type(user_get_all()) == list
    temp_user = create_temp_user()
    for user in user_get_all():
        assert user.get("user_id") is not None
        assert user.get("user_fullname") is not None
        assert user.get("user_email") is not None
        assert user.get("user_phone") is not None
        assert user.get("user_admin") is not None
        if user["user_id"] == temp_user.id:
            assert user["user_fullname"] == temp_user.name
            assert user["user_email"] == temp_user.email
            assert user["user_phone"] == temp_user.phone
            assert user["user_admin"] == 0
    delete_temp_user(temp_user)
    del temp_user

def test_user_get_username():
    assert user_get_username("-1") == "Unknown User"
    temp_user = create_temp_user()
    assert user_get_username(temp_user.id) == temp_user.email
    delete_temp_user(temp_user)
    del temp_user

def test_user_get_single():
    assert user_get_single(-1) == {} and len(user_get_single(-1)) == 0
    temp_user = create_temp_user()
    temp_user_data = user_get_single(temp_user.id)
    assert temp_user_data["user_fullname"] == temp_user.name and temp_user_data["user_email"] == temp_user.email and temp_user_data["user_phone"] == temp_user.phone
    delete_temp_user(temp_user)
    del temp_user

def test_user_create():
    temp_user = create_temp_user()
    assert user_check_exists(temp_user.email) is True
    assert user_create(temp_user.creation_dict) is False
    delete_temp_user(temp_user)
    del temp_user

def test_user_update():
    temp_user = create_temp_user()
    update_dict = temp_user.modify_dict
    update_dict["password"] = ""
    update_dict["id"] = temp_user.id
    assert user_update(update_dict) is True
    assert user_get_username(temp_user.id) == temp_user.alt_email
    user_update(temp_user.creation_dict)
    assert user_get_username(temp_user.id) == temp_user.email
    delete_temp_user(temp_user)
    del temp_user

def test_get_patient():
    assert get_patient(-1) is None
    temp_patient = create_temp_patient(True)
    assert type(get_patient(temp_patient.id)) == dict and get_patient(temp_patient.id)["patient_gender"] == temp_patient.gender
    delete_temp_patient(temp_patient)
    del temp_patient

def test_insert_new_patient_link():
    temp_user = create_temp_user()
    temp_patient = create_temp_patient(False)
    temp_patient.id = insert_new_patient_link(temp_patient.creation_dict, temp_user.id)
    assert link_get(temp_user.id)["patient_id"] == temp_patient.id
    link_delete(temp_user.id)
    delete_temp_user(temp_user)
    delete_temp_patient(temp_patient)
    del temp_user
    del temp_patient

def test_update_patient():
    temp_patient = create_temp_patient(True)
    update_patient(temp_patient.modify_dict, temp_patient.id)
    assert get_patient(temp_patient.id) is not None and get_patient(temp_patient.id)["patient_gender"] == temp_patient.alt_gender
    update_patient(temp_patient.creation_dict, temp_patient.id)
    assert get_patient(temp_patient.id) is not None and get_patient(temp_patient.id)["patient_gender"] == temp_patient.gender
    delete_temp_patient(temp_patient)
    del temp_patient

def test_link_check_exists():
    assert link_check_exists(-1, False) is False
    assert link_check_exists(-1, True) is False
    temp_user = create_temp_user()
    temp_patient = create_temp_patient(False)
    temp_patient.id = insert_new_patient_link(temp_patient.creation_dict, temp_user.id)
    assert link_check_exists(temp_user.id, False) is True
    assert link_check_exists(temp_patient.id, True) is True
    link_delete(temp_user.id)
    delete_temp_user(temp_user)
    delete_temp_patient(temp_patient)
    del temp_user
    del temp_patient

def test_link_get_all():
    temp_user = create_temp_user()
    temp_patient = create_temp_patient(False)
    temp_patient.id = insert_new_patient_link(temp_patient.creation_dict, temp_user.id)
    link_exists = False
    for item in link_get_all():
        if item["patient_id"] == temp_patient.id:
            link_exists = True
    assert link_exists is True
    link_delete(temp_user.id)
    delete_temp_user(temp_user)
    delete_temp_patient(temp_patient)
    del temp_user
    del temp_patient

def test_link_get():
    assert link_get(-1) is None
    temp_user = create_temp_user()
    temp_patient = create_temp_patient(False)
    temp_patient.id = insert_new_patient_link(temp_patient.creation_dict, temp_user.id)
    assert link_get(temp_user.id)["user_id"] == temp_user.id and link_get(temp_user.id)["patient_id"] == temp_patient.id
    link_delete(temp_user.id)
    delete_temp_user(temp_user)
    delete_temp_patient(temp_patient)
    del temp_user
    del temp_patient

def test_link_delete():
    temp_user = create_temp_user()
    temp_patient = create_temp_patient(False)
    temp_patient.id = insert_new_patient_link(temp_patient.creation_dict, temp_user.id)
    assert link_check_exists(temp_user.id, False) is True
    link_delete(temp_user.id)
    assert link_check_exists(temp_user.id, False) is False
    link_delete(temp_user.id)
    delete_temp_user(temp_user)
    delete_temp_patient(temp_patient)
    del temp_user
    del temp_patient

def test_admin_user_admin_check():
    temp_user = create_temp_user()
    assert admin_user_admin_check(temp_user.email) is False
    admin_apply_admin_user(temp_user.id)
    assert admin_user_admin_check(temp_user.email) is True
    delete_temp_user(temp_user)
    del temp_user

def test_admin_check_basepass():
    assert type(admin_check_basepass()) == bool

def test_admin_get_patient_data():
    temp_patient = create_temp_patient(True)
    for patient in admin_get_patient_data():
        assert patient.get("id") is not None
        assert patient.get("user_link") is None
        assert patient.get("gender") is not None
        assert patient.get("age") is not None
        assert patient.get("hypert") is not None
        assert patient.get("hdisease") is not None
        assert patient.get("married") is not None
        assert patient.get("wtype") is not None
        assert patient.get("rtype") is not None
        assert patient.get("glevel") is not None
        assert type(patient.get("bmi")) == float or type(patient.get("bmi")) == int or patient.get("bmi") is None
        assert patient.get("smoked") is not None
        assert patient.get("stroke") is not None
        if patient["id"] == temp_patient.id:
            assert patient["id"] == temp_patient.id
            assert patient["gender"] == temp_patient.gender
            assert patient["age"] == temp_patient.age
            assert patient["hypert"] == temp_patient.hyperT
            assert patient["hdisease"] == temp_patient.hDisease
            assert patient["married"] == temp_patient.married
            assert patient["wtype"] == temp_patient.work_type
            assert patient["rtype"] == temp_patient.residence_type
            assert patient["glevel"] == temp_patient.avg_gLevel
            assert patient["bmi"] == temp_patient. bmi
            assert patient["smoked"] == temp_patient.smoked
            assert patient["stroke"] == temp_patient.stroke
    delete_temp_patient(temp_patient)
    del temp_patient

def test_admin_apply_admin_user():
    temp_user = create_temp_user()
    assert admin_user_admin_check(temp_user.email) is False
    admin_apply_admin_user(temp_user.id)
    assert admin_user_admin_check(temp_user.email) is True
    delete_temp_user(temp_user)
    del temp_user

def test_admin_delete_user():
    temp_user = create_temp_user()
    assert user_check_exists(temp_user.email) is True
    admin_delete_user(temp_user.id)
    assert user_check_exists(temp_user.email) is False
    delete_temp_user(temp_user)
    del temp_user

def test_admin_delete_patient_data():
    temp_patient = create_temp_patient(True)
    assert get_patient(temp_patient.id) is not None
    admin_delete_patient_data(temp_patient.id)
    assert get_patient(temp_patient.id) is None
    delete_temp_patient(temp_patient)
    del temp_patient