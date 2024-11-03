import pymongo
#Insert
def mongo_insert(data, m_client):
    m_database = m_client["healthdb"] #Open the Database 
    m_collection = m_database["patient_data"] #Open the patient_data collection (collection == table) in the database. 
    x = m_collection.insert_one(data) #Adds the given data to the table and returns the new entry's ID as x.
    return x #Return the given ID
    #This function takes the given data and adds it to the MongoDB database while also returning the new entry's ID.
    #data = The data to add to the database, (Dictionary)
    #m_client = The connection to mongodb to use. (MongoClient)

#Find
def mongo_find_all(admin, m_client):
    records = []
    m_database = m_client["healthdb"] #Open the Database
    m_collection = m_database["patient_data"] #Open the patient_data collection (collection == table) in the database.
    for item in m_collection.find(): #For each record in mongodb, remove the ID and MySQL_ID if admin is False, and save it to the records list.
        if admin is False:
            item.pop("_id")
            item.pop("MySQL_ID")
        records.append(item)
    return records #Return all records from mongodb.
    #This function gets all records stored in the mongodb database.
    #admin = If True, the ID and MySQL_ID records aren't saved. (Boolean)
    #m_client = The connection to mongodb to use. (MongoClient)

#Delete
def mongo_delete(delete_query, m_client):
    m_database = m_client["healthdb"] #Open the Database
    m_collection = m_database["patient_data"] #Open the patient_data collection (collection == table) in the database.
    x = m_collection.delete_many(delete_query) #Delete the records that match the given query. E.G: {"MySQL_ID": 1} will delete all records in which MySQL_ID is equal to 1.
    return x
    #delete_query = A small dictionary that defines what to delete. (Boolean)
    #m_client = The connection to mongodb to use. (MongoClient)

def mongo_nuke(m_client):
    m_database = m_client["healthdb"] #Open the Database
    m_collection = m_database["patient_data"] #Open the patient_data collection (collection == table) in the database.
    x = m_collection.delete_many({}) #Deletes everything from the mongodb database.
    #m_client = The connection to mongodb to use. (MongoClient)

#Update
def mongo_update(update_query, new_values, m_client):
    m_database = m_client["healthdb"] #Open the Database
    m_collection = m_database["patient_data"] #Open the patient_data collection (collection == table) in the database.
    new_values = {"$set": new_values} #This is required to update the database.
    x = m_collection.update_many(update_query, new_values) #Update all records that match the query with the new values.
    return x
    #update_query = A small dictionary that defines what to update. (Dictionary.)
    #new_values = A dictionary that contains the new values to update the record with. (Dictionary)
    #m_client = The connection to mongodb to use. (MongoClient)