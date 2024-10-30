def is_number(text, check_float):
    try:
        if check_float is True:
            float(text)
        else:
            int(text)
        return True
    except:
        return False