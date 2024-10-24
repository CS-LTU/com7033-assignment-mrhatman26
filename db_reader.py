import csv, pyperclip
from db_handler import insert_patients_data

def str_to_int(YesNo):
    if YesNo.upper() == "YES":
        return 1
    else:
        return 0
    
def read_presaved_data():
    with open("healthcare-dataset-stroke-data.csv") as csvfile:
        table = csv.reader(csvfile, delimiter=" ")
        for row in table:
            print(row)
            if len(row) > 1:
                row = row[0] + row[1]
                row = row.split(",")
            else:
                row = row[0].split(",")
            if row[9] == "N/A":
                row[9] = None
            row_dict = {
                "patient_gender": row[1].upper(),
                "patient_age": row[2].upper(),
                "patient_hyperT": str_to_int(row[3]),
                "patient_hDisease": str_to_int(row[4]),
                "patient_married": str_to_int(row[5]),
                "patient_work_type": row[6].upper(),
                "patient_residence_type": row[7].upper(),
                "patient_avg_gLevel": row[8].upper(),
                "patient_bmi": row[9],
                "patient_smoked": row[10].upper(),
                "patient_stroke": str_to_int(row[11].upper())
            }
            if row[0] != "id":
                insert_patients_data(row_dict)
    csvfile.close()