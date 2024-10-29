import pymongo
def mongo_create(data):
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    x = m_collection.insert_one(data)
    print(x.inserted_id) 