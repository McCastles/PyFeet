
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
        
        self.connection = sqlite3.connect(db_path)
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
            print('Database created sycc.\n')
        
        print(f'Database connection sycc.\n')


    # TODO: JSON unpacking?
    def insert_row(self, trace_id):

        query = f'''

        INSERT  INTO {self.table_name} (
            {self.columns}
            )

            VALUES (
                {trace_id}, 12121212122012, 'jAS', 'po kanapke', 
                {random.randint(1, 100)}, 'False', {random.randint(1, 100)}, 'False',
                {random.randint(1, 100)}, 'False', {random.randint(1, 100)}, 'False',
                {random.randint(1, 100)}, 'False', {random.randint(1, 100)}, 'False',
                'False'
            )
        '''

        self.connection.execute(query)
        self.connection.commit()
        print(f'Row inserted with id = {trace_id}')



    # TODO: WHERE
    def select_row(self, verbose=False):

        print(f'\nSelecting all rows...')

        query = f'''
        SELECT 
            {self.columns}
            from {self.table_name}
        '''

        cursor = self.connection.execute(query)
        
        if verbose:
            for row in cursor:
                print(row)
        print(f'Row selected sycc.')




    def select_area(self, id_anomaly, margin=3, verbose=False):

        print(f'\nFetching row: id = {id_anomaly} +- {margin}')
            
        query = f'''

        SELECT 

            {self.columns}
            
            from {self.table_name}

            WHERE ID BETWEEN {id_anomaly-margin} AND {id_anomaly+margin}

        '''

        cursor = self.connection.execute(query)

        if verbose:
            for row in cursor:
                print(row)

        print('Fetching sycc.')
        return cursor
    



if __name__ == "__main__":

    db_name = './test_class.db'
    os.remove(db_name), print('\nDeleted db sycc.')


    # Creation
    db = DashDBmanager(db_name)


    # Insert dummy data
    for i in range(1, 11):
        db.insert_row(i)


    # Test
    db.select_row(verbose=True)
    db.select_area(1, verbose=True)
    db.select_area(5, verbose=True)
    db.select_area(10, verbose=True)


