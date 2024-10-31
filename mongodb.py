import pymongo
#Insert
def mongo_insert(data):
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    x = m_collection.insert_one(data)

#Find
def mongo_find_all():
    records = []
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    for item in m_collection.find():
        records.append(item)
    return records