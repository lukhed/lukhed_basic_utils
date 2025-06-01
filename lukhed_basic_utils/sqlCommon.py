from lukhed_basic_utils import classCommon
from typing import Optional
from lukhed_basic_utils import osCommon as osC
from mysql.connector.connection import MySQLConnection
import mysql.connector
import atexit

class SqlHelper(classCommon.LukhedAuth):
    def __init__(self, datbase_project, datbase_name, key_management='github', auth_type='basic', 
                 auth_dict=None):
        
        # Creates the files needed for re-use either locally or on Github
        super().__init__(datbase_project, key_management=key_management)

        self.auth_type = auth_type
        self._auth_dict = auth_dict

        self.database_project = datbase_project
        self.database_name = datbase_name

        if self._auth_data is None:
            self._auth_setup()

        self.db_connection = None                       # type: Optional[MySQLConnection]
        self.cursor = None
        atexit.register(self.close_connection)


    ###################
    # Auth and Connection
    def _auth_setup(self):
        """
        Set up authentication for the SQL database.
        """
        if self.auth_type == 'basic':
            if self._auth_dict is None:
                # Walk the user through the basic auth setup
                input("Basic auth requires the following information: 'host', 'user', 'password'. "
                    "Press enter to start inputting these values.")
                host = input("Enter host (e.g. 123.241.123.12): ")
                user = input("Enter user: ")
                password = input("Enter password: ")

                self._auth_data = {
                    "host": host,
                    "user": user,
                    "password": password
                }
            
            # Write auth data to user specified storage
            self.kM.force_update_key_data(self._auth_data)
            print("Basic auth data has been set up successfully.")

        else:
            raise ValueError(f"Unsupported auth_type: {self.auth_type}")
        
    def _check_connect_db(self):
        if self.db_connection is None:
            self.connect()
        elif self.db_connection.is_connected():
            pass
        else:
            self.connect()
        
    def connect(self):
        self.db_connection = mysql.connector.connect(
            host=self._auth_data['host'],
            user=self._auth_data['user'],
            password=self._auth_data['password'],
            database=self.database_name
        )
        self.cursor = self.db_connection.cursor()

    def test_connection(self):
        self._check_connect_db()
        if self.db_connection.is_connected():
            print("Connected to the database " + self.database_name)
        else:
            print("Failed to connect to the database")

    def close_connection(self):
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            print("Connection was closed to " + self.database_name)

    def change_database(self, database_name):
        self.close_connection()
        self.database = self._parse_database_input(database_name)
        print("New database is: " + self.database)

    def update_auth_data(self, force_new_auth_dict=None):
        if force_new_auth_dict is not None:
            self._auth_dict = force_new_auth_dict
        self._auth_setup()

    ##################
    # Table Management
    def get_all_tables(self):
        self._check_connect_db()
        query = "SHOW TABLES;"
        self.cursor.execute(query)
        tables = [table[0] for table in self.cursor.fetchall()]
        return tables

    

    
        
    
        
    


    