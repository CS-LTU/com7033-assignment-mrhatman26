def is_number(text, check_float):
    try:
        if check_float is True:
            float(text)
        else:
            int(text)
        return True
    except:
        return False
    
def str_to_booInt(YesNo):
    if is_number(YesNo, False):
        return int(YesNo)
    else:
        if YesNo.upper() == "YES":
            return 1
        else:
            return 0
    
def clean_subdata(subdata):
	subdata["patient_gender"] = subdata["patient_gender"].upper()
	subdata["patient_age"] = int(subdata["patient_age"])
	subdata["patient_hyperT"] = int(subdata["patient_hyperT"])
	subdata["patient_hDisease"] = subdata["patient_hDisease"]
	subdata["patient_married"] = str_to_booInt(subdata["patient_married"])
	subdata["patient_work_type"] = subdata["patient_work_type"].upper()
	subdata["patient_residence_type"] = subdata["patient_residence_type"].upper()
	subdata["patient_avg_gLevel"] = float(subdata["patient_avg_gLevel"])
	subdata["patient_bmi"] = float(subdata["patient_bmi"])
	subdata["patient_smoked"] = subdata["patient_smoked"].upper()
	subdata["patient_stroke"] = int(subdata["patient_stroke"])
	return subdata