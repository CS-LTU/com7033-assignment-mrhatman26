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

    
def read_presaved_data():
    with open("healthcare-dataset-stroke-data.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=" ")
        data = list(reader)
        row_count = len(data)
        index = 0
        for row in data:
            if len(row) > 1:
                row = row[0] + row[1]
                row = row.split(",")
            else:
                row = row[0].split(",")
            if row[9] == "N/A":
                row[9] = None
            row[10] = row[10].replace("smoked", " smoked")
            row_dict = {
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
            if row[0] != "id":
                mysql_id = insert_patient_data(row_dict)
                row_dict["MySQL_ID"] = mysql_id
                mongo_insert(row_dict)
            print(str(index) + "/" + str(row_count) + " row loaded from healthcare-dataset-stroke-data.csv", flush=True, end="\r")
            index += 1
    csvfile.close()
    print(str(index) + "/" + str(row_count) + " loaded from healthcare-dataset-stroke-data.csv", flush=True)