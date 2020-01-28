import datetime
import json
import os
import random
import requests
import sqlite3
from sqlite3 import Error


class DashDBmanager:

    def __init__(self, db_path='./walktraceDB.db'):

        self.table_name = f'STEPS'
        self.columns = f'''
        DATE, USERNAME, DESC, 
        S1_VALUE, S1_ANOMALY, S2_VALUE, S2_ANOMALY,
        S3_VALUE, S3_ANOMALY, S4_VALUE, S4_ANOMALY,
        S5_VALUE, S5_ANOMALY, S6_VALUE, S6_ANOMALY,
        IS_ANOMALY
        '''

        existed = os.path.isfile(db_path)

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        #print(f'\nTrying to connect to {db_path}...')

        if not existed:
            #print(f'Database {db_path} not found, creating new...')

            query = f'''

            CREATE TABLE {self.table_name} (

            ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,

            DATE DATETIME NOT NULL,

            USERNAME VARCHAR(25) NOT NULL, 

            DESC VARCHAR(50),

            S1_VALUE INT NOT NULL,
            S1_ANOMALY BOOLEAN NOT NULL,

            S2_VALUE INT NOT NULL,
            S2_ANOMALY BOOLEAN NOT NULL,

            S3_VALUE INT NOT NULL,
            S3_ANOMALY BOOLEAN NOT NULL,

            S4_VALUE INT NOT NULL,
            S4_ANOMALY BOOLEAN NOT NULL,

            S5_VALUE INT NOT NULL,
            S5_ANOMALY BOOLEAN NOT NULL,

            S6_VALUE INT NOT NULL,
            S6_ANOMALY BOOLEAN NOT NULL,

            IS_ANOMALY BOOLEAN NOT NULL

            )
            '''

            self.connection.execute(query)
            #print('Database created successfully.\n')
        #print('Connected.')

    # def select_row_with_anomaly(self, imie, czas):
    #     #print(f'\nSelecting row with imie = {imie}, czas = {czas}')
    #     query = f'''
    #     SELECT *
    #     FROM {self.table_name}
    #     WHERE USERNAME = '{imie}' AND DATE = '{czas}' AND IS_ANOMALY = 1
    #     '''
    #     cursor = self.connection.execute(query)
    #     i = 0
    #     for row in cursor:
    #         i += 1
    #         #print(row)
    #     #print(f'{i} row selected.\n')
    #     return row[1]

    def select_all(self):
        #print(f'\nSelecting all rows...')

        cursor = self.connection.execute(f'''
        SELECT * 
        FROM {self.table_name}
        ''')

        qty = 0
        for row in cursor:
            qty += 1
            #print(row)
        #print(f'{qty} row(s) selected.')

    def insert_row(self, row_list):
        query = f'INSERT INTO {self.table_name} ({self.columns}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        self.connection.execute(query, row_list)
        self.connection.commit()
        #print(f'Row inserted with id = {row_list[0]}')

    @staticmethod
    def parseJSON(json_data):

        trace = json_data['trace']
        row_list = []

        # DATE
        dt = datetime.datetime.strptime(str(trace['id']), '%H%M%S%d%m%Y')
        dt = dt.strftime("%m-%d-%Y %H:%M:%S")
        row_list.append(f'{dt}')

        # USERNAME
        row_list.append(f'{json_data["firstname"]} {json_data["lastname"]}')

        # DESC
        row_list.append(f'{trace["name"]}')

        # S1_VALUE, S1_ANOMALY ... S6_VALUE, S6_ANOMALY
        for sensor in trace['sensors']:
            row_list.append(sensor['value'])
            row_list.append(bool(sensor['anomaly']))

        # IS_ANOMALY
        is_anomaly = any([sensor['anomaly'] for sensor in trace['sensors']])
        row_list.append(bool(is_anomaly))

        return row_list

    def list_anomalies(self, imie):

        #print(f'\nSelecting all rows of {imie} with anomalies...')
        query = f'''
        SELECT * 
        FROM {self.table_name}
        WHERE IS_ANOMALY=1 AND USERNAME = '{imie}'
        '''
        cursor = self.connection.execute(query)
        ids = []
        times = []
        sensors = []
        anomaly_value_indeces = list(range(5, 16, 2))
        qty = 0
        for row in cursor:
            anomalies_on = []
            for index, sensor_id in zip(anomaly_value_indeces, range(1, 7)):
                if row[index] == 1:
                    anomalies_on.append(f'S{sensor_id}')
            anomalies_on = ', '.join(anomalies_on)
            sensors.append(anomalies_on)
            times.append(row[1])
            ids.append(row[1])
            #print(row)
            qty += 1

        #print(f'{qty} row(s) selected.\n')
        anomaly_descriptions = [
            f"{anomaly_sensors}"
            for anomaly_time, anomaly_sensors
            in zip(times, sensors)
        ]
        return [{'sensors': an_desc, 'date': an_id} for an_id, an_desc in zip(ids, anomaly_descriptions)]

    def select_area(self, czas, imie, delta=5):

        dt = datetime.datetime.strptime(czas, "%Y-%m-%dT%H:%M:%S")
        left = dt - datetime.timedelta(seconds=delta)
        right = dt + datetime.timedelta(seconds=delta)

        dt = dt.strftime("%m-%d-%Y %H:%M:%S")
        left = left.strftime("%m-%d-%Y %H:%M:%S")
        right = right.strftime("%m-%d-%Y %H:%M:%S")

        #print(f'Selecting rows of {imie} with date {dt} +- {delta} seconds...')
        query = f"SELECT ID, {self.columns} FROM {self.table_name} WHERE USERNAME = '{imie}' AND DATE >= '{left}' AND DATE <= '{right}'"
        cursor = self.connection.execute(query)

        qty = 0
        rows = []
        for qty, row in enumerate(cursor, 1):
            #print(row)
            dt = datetime.datetime.strptime(row[1], "%m-%d-%Y %H:%M:%S")
            l = []
            l.append(dt)
            l.append(row[4:])
            rows.append(l)

        #print(f'\n{qty} row(s) selected.')

        series = [[] for _ in range(6)]
        for row in sorted(rows, key=lambda x: x[0]):
            for i, j in enumerate(range(0, 12, 2)):
                series[i].append(row[1][j])

        return series


if __name__ == "__main__":
    # db_path = './test_class.db'
    db_path = '../../walktraceDB.db'

    # Deleting old database
    # os.remove(db_path), #print('\nDeleted db successfully.')

    db = DashDBmanager(db_path)

    # json_data = {
    #     'birthdate': '1982',
    #     'disabled': False,
    #     'firstname': 'Janek',
    #     'id': 12,
    #     'lastname': 'Grzegorczyk',
    #     'trace': {
    #         'id': 11110411111121,
    #         'name': 'bach',
    #         'sensors': [
    #             {'anomaly': False, 'id': 0, 'value': 710},
    #             {'anomaly': False, 'id': 1, 'value': 148},
    #             {'anomaly': True, 'id': 2, 'value': 1023},
    #             {'anomaly': False, 'id': 3, 'value': 1023},
    #             {'anomaly': True, 'id': 4, 'value': 245},
    #             {'anomaly': False, 'id': 5, 'value': 1023}
    #         ]
    #     }
    # }

    # JSON parsing
    # for pac in range(1, 7):
    # url = f'http://127.0.0.1:5000/{pac}'
    #     for i in range(30):
    #         json_data = json.loads(requests.get(url).text)
    # row_list = DashDBmanager.parseJSON(json_data)
    # db.insert_row(row_list)

    db.select_all()

    slownicks = db.list_anomalies('Bartosz Moskalski')
    #print(slownicks, '\n')

    lista_list = db.select_area(slownicks[-1]['date'], delta=5, imie='Bartosz Moskalski')
    #print('\n', lista_list)
