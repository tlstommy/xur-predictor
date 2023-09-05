import sqlite3
from sqlite3 import Error


DATABASE_PATH = "xurHistory.db"
TABLE_NAME = "history"
OVERWRITE_OLD = False

class XurPredictor():
    def __init__(self,dbPath):
        
        self.databasePath = dbPath
        self.tableName = TABLE_NAME.upper()
        self.createDB(self.tableName)
    
    def createDB(self,name):
        self.database = sqlite3.connect(self.databasePath)
        self.cursor = self.database.cursor()

        #table header info
        sqlTable = f"""
            CREATE TABLE {name} (
            Weeks_Since_11_13_2020 INT NOT NULL,
            Date DATETIME NOT NULL,
            LocationID VARCHAR(255) NOT NULL
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

    def addToDB(self,data):
        weekID=data[0]
        date = data[1]
        locationID = data[2]

        #connect to db
        self.database = sqlite3.connect(self.databasePath)
        self.cursor = self.database.cursor()

        self.cursor.execute(f'''INSERT INTO {self.tableName} VALUES ('{weekID}','{date}','{locationID}')''')
        self.database.commit()

        print(f"Added {data} to database")
        
        
predictor = XurPredictor(DATABASE_PATH)