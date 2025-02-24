import csv
from db_handler import insert_patient_data
from mongodb import mongo_insert
from misc import is_number
import time as t

def str_to_booInt(YesNo):
    if is_number(YesNo, False):
        return int(YesNo)
    else:
        if YesNo.upper() == "YES":
            return 1
        else:
            return 0
    #A simple function to convert "Yes" "No" strings to their boolean counterparts.
    #YesNo = The text to convert to a bool. (String)

    
def read_presaved_data(mongodb, mysql, m_client):
    with open("healthcare-dataset-stroke-data.csv") as csvfile: #Open the CSV file as csvfile.
        reader = csv.reader(csvfile, delimiter=" ") #Create an instance of CSV Reader on the CSV File.
        data = list(reader) #Convert the reader to a list.
        row_count = len(data) #Get the total length of the file.
        index = 0
        for row in data:
            if len(row) > 1: #Sometimes, the rows in the file are split into two. If this is the case, join them back together.
                row = row[0] + row[1]
                row = row.split(",") #Split the row into 12 items using the commas as a seperator.
            else:
                row = row[0].split(",") #Split the row into 12 items using the commas as a seperator.
            if row[9] == "N/A": #If the BMI is equal to "N/A", set it to None.
                row[9] = None
            row[10] = row[10].replace("smoked", " smoked") #If the smoked data does not contain a space, add one.
            row_dict = { #Add all of the data to a dictionary so it can easily be saved to the database.
                "patient_gender": row[1].upper(),
                "patient_age": row[2].upper(),
                "patient_hyperT": str_to_booInt(row[3]),
                "patient_hDisease": str_to_booInt(row[4]),
                "patient_married": str_to_booInt(row[5]),
                "patient_work_type": row[6].upper(),
                "patient_residence_type": row[7].upper(),
                "patient_avg_gLevel": row[8].upper(),
                "patient_bmi": row[9],
                "patient_smoked": row[10].upper(),
                "patient_stroke": str_to_booInt(row[11].upper())
            }
            if row[0] != "id": #Make sure the headers aren't saved.
                if mysql is True: #If MySQL is True, save the data to MySQL.
                    mysql_id = insert_patient_data(row_dict)
                else:
                    mysql_id = -99
                if mongodb is True: #If mongodb is True, save the data to MongoDB.
                    row_dict["MySQL_ID"] = mysql_id
                    mongo_insert(row_dict, m_client)
            print(str(index) + "/" + str(row_count) + " rows loaded from healthcare-dataset-stroke-data.csv", flush=True, end="\r")
            #Print the progress of the reading of the file.
            index += 1
    csvfile.close() #Close the CSV File.
    print(str(index) + "/" + str(row_count) + " rows loaded from healthcare-dataset-stroke-data.csv", flush=True)
    return True