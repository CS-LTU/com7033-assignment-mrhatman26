import csv
from db_handler import insert_patients_data
def read_presaved_data():
    with open("healthcare-dataset-stroke-data.csv") as csvfile:
        table = csv.reader(csvfile, delimiter=" ")
        for row in table:
            insert_patients_data(row)
    csvfile.close()