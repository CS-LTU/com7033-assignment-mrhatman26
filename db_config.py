def get_db_config(deployed):
    db_config = {}
    if deployed:
        db_config = {
            'user': 'root',
            'password': 'healthyboi',
            'host': 'db',
            'database': 'healthDB'
        }
    else:
        db_config = {
            'user': 'root',
            'password': 'healthyboi',
            'host': 'localhost',
            'port': 1234,
            'database': 'healthDB'
        }
    return db_config