import csv
import time as t
with open("healthcare-dataset-stroke-data.csv") as csvfile:
    table = csv.reader(csvfile, delimiter=" ")
    data = list(table)
    row_count = len(data)
    print(row_count)
    index = 0
    for row in data:
        print(str(index) + "/" + str(row_count) + " loaded", end="\r")
        index += 1
        t.sleep(0.5)
csvfile.close()
