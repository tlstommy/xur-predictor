from sklearn.linear_model import LogisticRegression
import numpy as np
from datetime import date, timedelta
import sqlite3
import json
import random
import requests
from sqlite3 import Error

API_ENDPOINT = "https://xurtracker.com/api/prediction-data"
DATABASE_PATH = "xurHistory.db"
TABLE_NAME = "history"

OVERWRITE_OLD = False


class XurPredictor():

    def __init__(self,dbPath):
        self.databasePath = dbPath
        self.tableName = TABLE_NAME.upper()
        self.createDB()
        self.windowSize = 12 #number of past items to analyze
        self.data = None
        self.trainingDataX = None
        self.trainingDataY = None
        self.datasetInputLength = 10
        self.datasetFeatures = 1
        self.startDate = date(2020,11,13)
    #create a new db using the GLOBALS above
    def createDB(self):
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.tableName} (
                    Weeks_Since_11_13_2020 INT NOT NULL,
                    Date DATETIME NOT NULL,
                    LocationID VARCHAR(255) NOT NULL
                );
            """
            cursor.execute(create_table_sql)
            if OVERWRITE_OLD:
                print("OVERWRITING OLD TABLE")
                cursor.execute(f"DROP TABLE IF EXISTS {self.tableName}")
                cursor.execute(create_table_sql)
    
    #append new data to db
    def addDataToDB(self,data):
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()
            cursor.execute(f"INSERT INTO {self.tableName} VALUES (?, ?, ?)", data)
            database.commit()
            print(f"Added {data} to database")
    
    #translate id to loc string
    def translateID(self,id):
        locations = {
            0: "Tower Hangar\nThe Last City, Earth",
            1: "Winding Cove\nEuropean Dead Zone, Earth",
            2: "Watcher's Grave\nArcadian Valley, Nessus"
        }
        return locations.get(id)
    
    #get last week in database
    def getLastWeekInDB(self):
        weeks = []
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()
            cursor.execute(f'''SELECT Weeks_Since_11_13_2020 FROM {self.tableName}''')
            weeks = [int(item[0]) for item in cursor.fetchall()]

        return weeks[-1]

    #get locationIDS and return them as a list for predictions
    def getIDs(self):
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()
            cursor.execute(f'''SELECT LocationID FROM {self.tableName}''')
            return [int(item[0]) for item in cursor.fetchall()]

    def getWeeksSince(self,startDate):
        
        days = date.today() - startDate
     
        return (days.days // 7) - 1
    
    #create a dataset 
    def createDataset(self):
        
        xVals = []
        yVals = []

        locationData = self.getIDs()
        #print(locationData)

        for i in range(len(locationData) - self.windowSize):

            #append a list of size windowSize to a list
            xVals.append(locationData[i:i + self.windowSize])
            #append the items after the nth windowsize item.
            yVals.append(locationData[i + self.windowSize])
            
        return np.array(xVals), np.array(yVals)

    #Split data into training data
    def makeTrainingData(self, xVals, yVals):
    
        self.trainingDataX = xVals[:-(self.windowSize)]
        self.trainingDataY = yVals[:-(self.windowSize)]
    
    #make a model and predict the next item
    def makePrediction(self):
        model = LogisticRegression(max_iter=200)  # Increased max_iter to ensure convergence
        model.fit(self.trainingDataX, self.trainingDataY)



predictor = XurPredictor(DATABASE_PATH)

predictor.createDataset()