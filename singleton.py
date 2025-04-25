import sqlite3

class DatabaseConnection:
    _instance = None

    def __init__(self):
        self.connection = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('books.db', check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        else:
            try:
                self.connection.execute('SELECT 1')
            except sqlite3.ProgrammingError:
                
                self.connection = sqlite3.connect('books.db', check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
        return self.connection
