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
        self.windowSize = 14 #number of past items to analyze
        self.data = None
        self.trainingDataX = None
        self.trainingDataY = None
        self.locationData = None
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
            0: "Tower Hangar, The Last City, Earth",
            1: "Winding Cove, European Dead Zone, Earth",
            2: "Watcher's Grave, Arcadian Valley, Nessus"
        }
        return locations.get(id)
    
    #get last week num in database
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
    
    #get the data from the xurtracker api
    def addNewLocDataFromApi(self):
        previousWeek = self.getWeeksSince(self.startDate)
        
        apiData = json.loads(str(requests.get(API_ENDPOINT).content.decode()))
        apiCurrentWeek = apiData["week"]
        apiCurrentLocationID = apiData["id"]
        apiCurrentDate = apiData["date"]

        print(apiData)

        #make sure data isnt old or doesnt already exist in the db
        if(previousWeek <= self.getLastWeekInDB()):
            print("OLD DATA")
            return -1
        
        print("Adding new data")
        print(int(apiCurrentWeek),apiCurrentDate,int(apiCurrentLocationID))
        self.addDataToDB([int(apiCurrentWeek),apiCurrentDate,int(apiCurrentLocationID)])
        
        print(apiData["week"])
    
    
    #create a dataset 
    def createDataset(self):
        
        xVals = []
        yVals = []

        self.locationData = self.getIDs()
        
        #self.locationData.pop()

        #print(locationData)

        for i in range(len(self.locationData) - self.windowSize):

            #append a list of size windowSize to a list
            xVals.append(self.locationData[i:i + self.windowSize])
            #append the items after the nth windowsize item.
            yVals.append(self.locationData[i + self.windowSize])
            
        self.makeTrainingData(np.array(xVals), np.array(yVals))

    #Split data into training data
    def makeTrainingData(self, xVals, yVals):
    
        self.trainingDataX = xVals[:-(self.windowSize)]
        self.trainingDataY = yVals[:-(self.windowSize)]
    
    #make a model and predict the next item
    def makePrediction(self):
        
        self.createDataset()
        
        model = LogisticRegression(max_iter=200)  #max iter is the epochs for conv
        model.fit(self.trainingDataX, self.trainingDataY)
        
        prediction = model.predict([self.locationData[-self.windowSize:]])
        predictionProbs = model.predict_proba([self.locationData[-self.windowSize:]])
        
        print(f"Prediction probabilities:")
        print(f"Probability of 0: {predictionProbs[0][0]*100}%")
        print(f"Probability of 1: {predictionProbs[0][1]*100}%")
        print(f"Probability of 2: {predictionProbs[0][2]*100}%\n")
        
        print(f"The most likely next item in the sequence is: {prediction[0]} ({self.translateID(prediction[0])})")
        print(f"Last location: {self.locationData[-1]} ({self.translateID(self.locationData[-1])})")


predictor = XurPredictor(DATABASE_PATH)
#predictor.addNewLocDataFromApi()
#predictor.addDataToDB([157,"11-24-2023",1])


predictor.makePrediction()