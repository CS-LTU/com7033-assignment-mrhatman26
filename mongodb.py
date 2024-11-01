import pymongo
#Insert
def mongo_insert(data):
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    x = m_collection.insert_one(data)

#Find
def mongo_find_all(admin):
    records = []
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    for item in m_collection.find():
        if admin is False:
            item.pop("_id")
            item.pop("MySQL_ID")
        records.append(item)
    return records

#Delete
def mongo_delete(delete_query):
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    print(type(delete_query["MySQL_ID"]), flush=True)
    m_collection.delete_many(delete_query)

#Update
def mongo_update(update_query, new_values):
    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client["healthdb"]
    m_collection = m_database["patient_data"]
    new_values = {"$set": new_values}
    m_collection.update_many(update_query, new_values)