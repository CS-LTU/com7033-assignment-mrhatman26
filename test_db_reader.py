import pytest, pymongo
from db_reader import *
from db_handler import admin_nuke

def test_str_to_booInt():
    assert str_to_booInt("Yes") == 1
    assert str_to_booInt("No") == 0
    assert str_to_booInt("1") == 1
    assert str_to_booInt("0") == 0

def test_read_presaved_data():
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    admin_nuke(m_client)
    assert read_presaved_data(False, True, None) is True
    assert read_presaved_data(True, False, m_client) is True
    m_client.close()
    del m_client