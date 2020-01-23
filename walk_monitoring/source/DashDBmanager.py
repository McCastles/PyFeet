import datetime
import random
import os
import sqlite3
from sqlite3 import Error


class DashDBmanager:

    def __init__(self, db_path='./walktraceDB.db'):

        self.table_name = f'STEPS'
        self.columns = f'''
        ID, DATE, USERNAME, DESC, 
        S1_VALUE, S1_ANOMALY, S2_VALUE, S2_ANOMALY,
        S3_VALUE, S3_ANOMALY, S4_VALUE, S4_ANOMALY,
        S5_VALUE, S5_ANOMALY, S6_VALUE, S6_ANOMALY,
        IS_ANOMALY
        '''

        existed = os.path.isfile(db_path)

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        print(f'Trying to connect to {db_path}...')

        if existed:

            print(f'Database {db_path} is not empty.')

        else:

            print(f'Database {db_path} not found, creating new...')

            query = f'''

            CREATE TABLE {self.table_name} (
            ID BIGINT PRIMARY KEY NOT NULL,

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
            print('Database created successfully.\n')

    def select_row(self, row_id, verbose=True):

        print(f'\nSelecting row with id = {row_id}')

        query = f'''
        SELECT *
            
        FROM {self.table_name}

        WHERE ID = {row_id};
        '''

        cursor = self.connection.execute(query)

        qty = 0
        for row in cursor:
            qty += 1
            if verbose:
                print(row)
        print(f'{qty} row(s) selected successfully.')

    def select_all(self):
        print(f'\nSelecting all rows...')

        cursor = self.connection.execute(f'''
        
        select * from steps
        
        ''')
        qty = 0

        for row in cursor:
            qty += 1
            print(row)

    def select_area(self, id_anomaly, margin=3, verbose=False):

        query = f'''

        SELECT 

            {self.columns}
            
            from {self.table_name}

            WHERE ID BETWEEN {id_anomaly - margin} AND {id_anomaly + margin}

        '''

        cursor = self.connection.execute(query)

        if verbose:
            for row in cursor:
                print(row)

        print('Fetching successfully.')
        return cursor

    def insert_row(self, row_list, verbose=False):
        query = f'REPLACE INTO {self.table_name}  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        self.connection.execute(query, row_list)
        self.connection.commit()

    @staticmethod
    def parseJSON(json_data, verbose=False):

        trace = json_data['trace']
        row_list = []

        # ID
        row_list.append(str(trace['id']))  # .zfill(14))

        # DATE
        dt = datetime.datetime.strptime(str(trace['id']), '%H%M%S%d%m%Y')
        dt = dt.strftime("%m/%d/%Y %H:%M:%S")
        row_list.append(f"'{dt}'")

        # USERNAME
        row_list.append(f"'{json_data['firstname']} {json_data['lastname']}'")

        # DESC
        row_list.append(f"'{trace['name']}'")

        # S1_VALUE, S1_ANOMALY ... S6_VALUE, S6_ANOMALY
        for sensor in trace['sensors']:
            row_list.append(str(sensor['value']))
            row_list.append(str(sensor['anomaly']))

        # IS_ANOMALY
        is_anomaly = any([sensor['anomaly'] for sensor in trace['sensors']])
        row_list.append(str(is_anomaly))

        if verbose:
            print(row_list, '\n')

        return row_list


if __name__ == "__main__":
    db_name = './test_class.db'

    # Deleting old database
    # os.remove(db_name), print('\nDeleted db successfully.')

    # Creation
    db = DashDBmanager(db_name)

    json_data = {
        'birthdate': '1982',
        'disabled': False,
        'firstname': 'Janek',
        'id': 12,
        'lastname': 'Grzegorczyk',
        'trace': {
            'id': 11111111111121,
            'name': 'bach',
            'sensors': [
                {'anomaly': False, 'id': 0, 'value': 710},
                {'anomaly': False, 'id': 1, 'value': 148},
                {'anomaly': False, 'id': 2, 'value': 1023},
                {'anomaly': False, 'id': 3, 'value': 1023},
                {'anomaly': False, 'id': 4, 'value': 245},
                {'anomaly': False, 'id': 5, 'value': 1023}
            ]
        }
    }

    # JSON parsing
    row_list = DashDBmanager.parseJSON(json_data)
    db.insert_row(row_list)

    # Test
    db.select_all()
    db.select_row(row_id=11111111111111)
    db.select_row(row_id=2572401012014)
