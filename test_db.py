import pytest
import mysql.connector
from db_handler import *
from db_config import get_db_config

#Before running these tests, please make sure the database has been started.

class TempUser():
    def __init__(self):
        self.username = "TestUser"
        self.password = "TestPassword"
        self.email = "TestUser@example.com"
        self.phone = "07234 928184"
        self.creation_dict = {"fullname": self.username, "email": self.email, "password": self.password, "phone": self.phone}

def test_str_to_bool():
    assert str_to_bool("Yes") is True
    assert str_to_bool("No") is False


def test_user_check_exists():
    assert user_check_exists("28975827893276468932987687051273984672901587") is False
    temp_user = TempUser()
    user_create(temp_user.creation_dict)
    #assert user_check_exists(temp_user.email) is True
    print(user_get_id(temp_user.username))
    admin_delete_user(user_get_id(temp_user.username))
    del temp_user