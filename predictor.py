import sqlite3
from sqlite3 import Error

from datetime import datetime

DATABASE_PATH = "xurHistory.db"
TABLE_NAME = "history"
OVERWRITE_OLD = False


class XurPredictor():
    def __init__(self,dbPath):
        
        self.databasePath = dbPath
        self.tableName = TABLE_NAME.upper()
        self.createDB(self.tableName)
        
        
        self.addToDB()

    def createDB(self,name):
        self.database = sqlite3.connect(self.databasePath)
        self.cursor = self.database.cursor()

        #table header info
        sqlTable = f"""
            CREATE TABLE {name} (
            Date DATETIME NOT NULL,
            Location VARCHAR(255) NOT NULL,
            ID VARCHAR(252) NOT NULL
            );
            """
        

        try:
            self.cursor.execute(sqlTable)
        except sqlite3.OperationalError:
            if(OVERWRITE_OLD):
                print(f"[Error] table '{name}' already exists, would you like to overwrite it?")
                uinput = input("Overwrite? (Y/n): ")
                if uinput.upper() == "Y" or uinput.upper() == "YES":
                    print("Dropping old table...")
                    self.cursor.execute(f"DROP TABLE IF EXISTS {name}")
                    self.cursor.execute(sqlTable)

    def addToDB(self):

        #connect to db
        self.database = sqlite3.connect(self.databasePath)
        self.cursor = self.database.cursor()

        print("DB and Cursor connected")


        self.cursor.execute(f'''INSERT INTO {self.tableName} VALUES ('{datetime.now()}', '1', '2')''')
        self.database.commit()
        
        
predictor = XurPredictor(DATABASE_PATH)