

import sqlite3
from sqlite3 import Error


db_file = './walktraceDB.db'
conn = sqlite3.connect(db_file)

conn.execute('''

INSERT  INTO STEPS (
    ID, DATE, USERNAME, DESC, 
    S1_VALUE, S1_ANOMALY, S2_VALUE, S2_ANOMALY,
    S3_VALUE, S3_ANOMALY, S4_VALUE, S4_ANOMALY,
    S5_VALUE, S5_ANOMALY, S6_VALUE, S6_ANOMALY,
    IS_ANOMALY
    )

    VALUES (
        1, 12121212122012, 'jAS', 'po kanapke', 
        14, 'False', 14, 'False',
        14, 'False', 14, 'False',
        14, 'False', 14, 'False',
        'False'
    )
''')



conn.commit()


print('Data insert sycc.')
