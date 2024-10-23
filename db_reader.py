import csv
with open("healthcare-dataset-stroke-data.csv") as csvfile:
    table = csv.reader(csvfile, delimiter=" ")
    for row in table:
        