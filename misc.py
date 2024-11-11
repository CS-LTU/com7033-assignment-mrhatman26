def is_number(text, check_float):
    try:
        if check_float is True:
            float(text)
        else:
            int(text)
        return True
    except:
        return False
    #This function checks if the given text is a number or not.
    #text = The string to check. (String)
    #check_float = If True, check if the string is a float instead. (Boolean)
    
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
    
def clean_subdata(subdata):
	subdata["patient_gender"] = subdata["patient_gender"].upper()
	subdata["patient_age"] = int(subdata["patient_age"])
	subdata["patient_hyperT"] = int(subdata["patient_hyperT"])
	subdata["patient_hDisease"] = int(subdata["patient_hDisease"])
	subdata["patient_married"] = str_to_booInt(subdata["patient_married"])
	subdata["patient_work_type"] = subdata["patient_work_type"].upper()
	subdata["patient_residence_type"] = subdata["patient_residence_type"].upper()
	subdata["patient_avg_gLevel"] = float(subdata["patient_avg_gLevel"])
	subdata["patient_bmi"] = float(subdata["patient_bmi"])
	subdata["patient_smoked"] = subdata["patient_smoked"].upper()
	subdata["patient_stroke"] = int(subdata["patient_stroke"])
	return subdata
    #This function takes the subdata and puts it in the formats needed to be added to the database.
    #subdata = A dictionary that contains the data to modify. (Dictionary)