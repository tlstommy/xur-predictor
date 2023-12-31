import sqlite3
import numpy as np
import json
import random
import requests
import tensorflow as tf
from sqlite3 import Error
from collections import Counter
import keras.models
from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, Dropout
from keras.preprocessing.sequence import TimeseriesGenerator
import matplotlib.pyplot as plt
from datetime import date, timedelta


API_ENDPOINT = "https://xurtracker.com/api/prediction-data"
DATABASE_PATH = "xurHistory.db"
TABLE_NAME = "history"
MODEL_NAME = "xp-main.keras"
OVERWRITE_OLD = False


class XurPredictor():

    def __init__(self,dbPath):
        self.databasePath = dbPath
        self.tableName = TABLE_NAME.upper()
        self.createDB()
        self.data = None
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


    #train model for predictions
    def trainModel(self,modelName,epochs):
        locationData = np.array(self.getIDs())

        print(locationData)
        
        locationData = locationData.reshape((len(locationData), self.datasetFeatures))
        locationData = locationData.reshape(-1, 1)
        
        #get training datasets
        trainingData, validationData = self.createTrainingData(locationData)


        generator = TimeseriesGenerator(trainingData, trainingData, length=self.datasetInputLength, batch_size=8)
        validationGenerator = TimeseriesGenerator(validationData, validationData, length=self.datasetInputLength, batch_size=8)
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=False)


        model = Sequential()
        model.add(LSTM(100, activation='relu', return_sequences=True, input_shape=(self.datasetInputLength, self.datasetFeatures)))
        model.add(Dropout(0.2))
        model.add(LSTM(50, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(3, activation='softmax'))
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        model.fit(generator, steps_per_epoch=1, epochs=epochs, verbose=1,validation_data=validationGenerator)
        #model.fit(generator, steps_per_epoch=1, epochs=epochs, verbose=1,validation_data=validationGenerator,callbacks=[early_stop])
        
        model.save(modelName)


    #create 80% training 20% validation
    def createTrainingData(self,data):
        dataSplitPoint = int(0.8 * len(data))
        
        trainingData = data[:dataSplitPoint]
        validationData = data[dataSplitPoint:]

        print("Training data: ", trainingData)
        print("Validation data: ", validationData)

        return [trainingData,validationData]

    def loadModel(self,modelName):
        return keras.models.load_model(modelName)

    #pure random
    def duplicatePrediction(self,nextLocationPrediction):
        print("Duplicate prediction, getting second most likely option.\n")
        
        
        resultDict = { 
            0:nextLocationPrediction[0][0],
            1:nextLocationPrediction[0][1], 
            2:nextLocationPrediction[0][2]
        }
        
        #sort results by val
        resultsSorted = sorted(resultDict, key=lambda k: resultDict[k],reverse=True)

        print(resultDict)
        print(resultsSorted)
        
        return resultsSorted[1]
    
    #softmax func
    def softmax(self,x):
        return np.exp(x) / np.sum(np.exp(x), axis=0)
    
    def getWeeksSince(self,startDate):
        
        days = date.today() - startDate
     
        return (days.days // 7) - 1
    
    def addNewLocData(self):
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
        self.addDataToDB([int(apiCurrentWeek),apiCurrentDate,int(apiCurrentLocationID)])
        
        print(apiData["week"])
    
    
    def makePrediction(self,modelName):
        testLocationData = [0, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 0, 2, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 2, 1, 0, 0, 2, 1, 0, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 0, 2, 1, 0, 1, 0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 0, 2, 0, 2, 0, 2, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 1, 0, 0, 2, 1, 2, 1, 2, 1, 0, 1, 1, 0, 2, 0, 2, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 2, 0, 2, 1, 2, 1, 1, 0, 1, 2, 0, 1, 2, 0, 1, 0, 1, 2, 1, 2, 0, 1,2,1,0]

        removeNWeeks = 0

        targetVal = None
        #remove last n items for testing
        for i in range(removeNWeeks):
            targetVal = testLocationData.pop()

        #get locational input data and reshape it
        locationData = np.array(self.getIDs())
        print(locationData)

        #locationData = np.array(testLocationData)


        #reshape location date
        locationData = locationData.reshape((len(locationData), self.datasetFeatures))

        model = self.loadModel(modelName)

        # predict the next item
        last_sequence = locationData[-self.datasetInputLength:].reshape((1, self.datasetInputLength, self.datasetFeatures))
        nextLocationPrediction = model.predict(last_sequence, verbose=0)
        print(nextLocationPrediction,"\n")
        predictedLoc = np.argmax(nextLocationPrediction)
        

        if predictedLoc == locationData[-1][0]:
            predictedLoc = self.duplicatePrediction(nextLocationPrediction)

        #calc as %
        percentages = self.softmax(nextLocationPrediction[0]) * 100
        
        print(f"\nPredicted Next Item in Sequence: {predictedLoc}")
        print(f"0: {percentages[0]:.2f}% ({nextLocationPrediction[0][0] * 100}%)")
        print(f"1: {percentages[1]:.2f}% ({nextLocationPrediction[0][1] * 100}%)")
        print(f"2: {percentages[2]:.2f}% ({nextLocationPrediction[0][2] * 100}%)")
        print(f"\n\nPrev Week: {locationData[-1][0]}")
        print(f"Prediction: {predictedLoc}")
        print(f"Target: {targetVal}")


        return[predictedLoc,percentages]


def makeGraph(data):
    labels = ["Tower Hangar","Winding Cove","Watcher's Grave"]
    plt.pie(data[1],labels=labels,autopct='%1.2f%%')
    plt.title(f"XUR Location Prediction:\n {predictor.translateID(data[0])}")
    plt.show() 
        
 
        



#using input size of 10
#Predicted Next Item in Sequence: 2
#   0: 29.33% (0.2117965817451477)
#   1: 32.12% (0.30273646116256714)
#   2: 38.56% (0.4854668974876404)
MODEL_NAME = "xp-main.keras"
        
predictor = XurPredictor(DATABASE_PATH)

#grab and add new data to the db from xurtracker
#predictor.addNewLocData()

#predictor.trainModel(MODEL_NAME,500)

#predictor.addDataToDB([151,"10-13-2023",2])
makeGraph(predictor.makePrediction(MODEL_NAME))
