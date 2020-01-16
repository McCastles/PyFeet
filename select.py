

import sqlite3
from sqlite3 import Error


db_file = './walktraceDB.db'
conn = sqlite3.connect(db_file)

cursor = conn.execute('''

SELECT 

    ID, DATE, USERNAME, DESC, 
    S1_VALUE, S1_ANOMALY, S2_VALUE, S2_ANOMALY,
    S3_VALUE, S3_ANOMALY, S4_VALUE, S4_ANOMALY,
    S5_VALUE, S5_ANOMALY, S6_VALUE, S6_ANOMALY,
    IS_ANOMALY
    
    from STEPS

''')



# for ko in conn:
    # print(ko)

# for row in cursor:
    # for i in row:

        # print(row)
#    print("USERNAME = ", row[2])
   

conn.commit()

print(cursor)
print('Data select sycc.')
