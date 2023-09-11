import sqlite3
import numpy as np
import random
import tensorflow as tf
from sqlite3 import Error
from collections import Counter
import keras.models
from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM
from keras.preprocessing.sequence import TimeseriesGenerator


DATABASE_PATH = "xurHistory.db"
TABLE_NAME = "history"
OVERWRITE_OLD = False


#util stuff
dcvIDs = [0, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 0, 2, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 2, 1, 0, 0, 2, 1, 0, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 0, 2, 1, 0, 1, 0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 0, 2, 0, 2, 0, 2, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 1, 0, 0, 2, 1, 2, 1, 2, 1, 0, 1, 1, 0, 2, 0, 2, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 2, 0, 2, 1, 2, 1, 1, 0, 1, 2, 0, 1, 2, 0, 1, 0, 1, 2, 1, 2, 0, 1]
dcvDates = ['11-13-2020', '11-20-2020', '11-27-2020', '12-04-2020', '12-11-2020', '12-18-2020', '12-25-2020', '01-01-2021', '01-08-2021', '01-15-2021', '01-22-2021', '01-29-2021', '02-05-2021', '02-12-2021', '02-19-2021', '02-26-2021', '03-05-2021', '03-12-2021', '03-19-2021', '03-26-2021', '04-02-2021', '04-09-2021', '04-16-2021', '04-23-2021', '04-30-2021', '05-07-2021', '05-14-2021', '05-21-2021', '05-28-2021', '06-04-2021', '06-11-2021', '06-18-2021', '06-25-2021', '07-02-2021', '07-09-2021', '07-16-2021', '07-23-2021', '07-30-2021', '08-06-2021', '08-13-2021', '08-20-2021', '08-27-2021', '09-03-2021', '09-10-2021', '09-17-2021', '09-24-2021', '10-01-2021', '10-08-2021', '10-15-2021', '10-22-2021', '10-29-2021', '11-05-2021', '11-12-2021', '11-19-2021', '11-26-2021', '12-03-2021', '12-10-2021', '12-17-2021', '12-24-2021', '12-31-2021', '01-07-2022', '01-14-2022', '01-21-2022', '01-28-2022', '02-04-2022', '02-11-2022', '02-18-2022', '02-25-2022', '03-04-2022', '03-11-2022', '03-18-2022', '03-25-2022', '04-01-2022', '04-08-2022', '04-15-2022', '04-22-2022', '04-29-2022', '05-06-2022', '05-13-2022', '05-20-2022', '05-27-2022', '06-03-2022', '06-10-2022', '06-17-2022', '06-24-2022', '07-01-2022', '07-08-2022', '07-15-2022', '07-22-2022', '07-29-2022', '08-05-2022', '08-12-2022', '08-19-2022', '08-26-2022', '09-02-2022', '09-09-2022', '09-16-2022', '09-23-2022', '09-30-2022', '10-07-2022', '10-14-2022', '10-21-2022', '10-28-2022', '11-04-2022', '11-11-2022', '11-18-2022', '11-25-2022', '12-02-2022', '12-09-2022', '12-16-2022', '12-23-2022', '12-30-2022', '01-06-2023', '01-13-2023', '01-20-2023', '01-27-2023', '02-03-2023', '02-10-2023', '02-17-2023', '02-24-2023', '03-03-2023', '03-10-2023', '03-17-2023', '03-24-2023', '03-31-2023', '04-07-2023', '04-14-2023', '04-21-2023', '04-28-2023', '05-05-2023', '05-12-2023', '05-19-2023', '05-26-2023', '06-02-2023', '06-09-2023', '06-16-2023', '06-23-2023', '06-30-2023', '07-07-2023', 
'07-14-2023', '07-21-2023', '07-28-2023', '08-04-2023', '08-11-2023', '08-18-2023', '08-25-2023', '09-01-2023']



class XurPredictor():
    def __init__(self,dbPath):
        
        self.databasePath = dbPath
        self.tableName = TABLE_NAME.upper()
        self.createDB()
        self.data = None
        self.datasetInputLength = 10
        self.datasetFeatures = 1

    
    #create a new db using the GLOBALS above
    def createDB(self):
        name = self.tableName
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()

            #table header info
            sqlTable = f"""
                CREATE TABLE {name} (
                Weeks_Since_11_13_2020 INT NOT NULL,
                Date DATETIME NOT NULL,
                LocationID VARCHAR(255) NOT NULL
                );
                """
            try:
                cursor.execute(sqlTable)
            except sqlite3.OperationalError:
                if(OVERWRITE_OLD):
                    
                    print("OVERWRITING OLD TABLE\n")
                    cursor.execute(f"DROP TABLE IF EXISTS {name}")
                    cursor.execute(sqlTable)

    #append new data to db
    def addDataToDB(self,data):
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()

            cursor.execute(f'''INSERT INTO {self.tableName} VALUES ('{data[0]}','{data[1]}','{data[2]}')''')
            database.commit()

            print(f"Added {data} to database")
            
    def translateID(self,id):
        if id == 0:
            location = "Tower Hangar\nThe Last City, Earth"
        if id == 1:
            location = "Winding Cove\nEuropean Dead Zone, Earth"
        if id == 2:
            location = "Watcher's Grave\nArcadian Valley, Nessus"
        return location
    #get location id data
    def getIDs(self):
        with sqlite3.connect(self.databasePath) as database:
            cursor = database.cursor()
            
            #get locationIDS and return them as a list for predictions
            cursor.execute(f'''SELECT LocationID FROM {self.tableName}''')
            return [int(item[0]) for item in cursor.fetchall()]

    def trainModel(self,modelName,epochs):

       
        
        locationData = np.array(self.getIDs())
        locationData = locationData.reshape((len(locationData), self.datasetFeatures))
        
        #get training datasets
        trainingData, validationData = self.createTrainingData(locationData)


        generator = TimeseriesGenerator(trainingData, trainingData, length=self.datasetInputLength, batch_size=8)
        validationGenerator = TimeseriesGenerator(validationData, validationData, length=self.datasetInputLength, batch_size=8)

        
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=False)


        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(self.datasetInputLength, self.datasetFeatures)))
        model.add(Dense(3))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            

        
        #verbose = 0 is no output
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

    def handleRepeat(self,predictionValue,previousValue):
        print(predictionValue,previousValue)
        if predictionValue <= 0.85:
            predictionValue = np.round(predictionValue) - 1
        
        print(f"adjusted repeat value: {predictionValue}" )

    #pure random
    def predictNextMath(self,sequence):
        print("Dplicate prediction, generating random.\n")

        #last second to last and 3rd to last vals
        lastValue = sequence[-1]
        secondValue = sequence[-2]
        thirdValue = sequence[-3]
        
        # Predict based on recent patterns
        if lastValue == secondValue:
            # If the last two values are the same, choose a value different from the last value
            possible_next_values = [x for x in [0, 1, 2] if x != lastValue]
        elif lastValue == thirdValue:
            # If a pattern of alternating values, predict a value different from the second to last value
            possible_next_values = [x for x in [0, 1, 2] if x != secondValue]
        else:
            # If no pattern is detected, consider any value except the last value
            possible_next_values = [x for x in [0, 1, 2] if x != lastValue]
        
        # Randomly select a value from the possible next values
        nextValue = random.choice(possible_next_values)
        
        return nextValue

    def makePrediction(self):
        testLocationData = [0, 2, 0, 1, 0, 1, 0, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 0, 2, 1, 0, 0, 0, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 2, 1, 0, 0, 2, 1, 0, 0, 2, 1, 0, 2, 0, 1, 2, 0, 2, 0, 2, 1, 0, 1, 0, 1, 2, 0, 1, 2, 1, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 0, 2, 0, 2, 0, 2, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 2, 1, 0, 0, 2, 1, 2, 1, 2, 1, 0, 1, 1, 0, 2, 0, 2, 0, 1, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 2, 0, 2, 1, 2, 1, 1, 0, 1, 2, 0, 1, 2, 0, 1, 0, 1, 2, 1, 2, 0, 1]

        removeNWeeks = 0

        targetVal = None
        #remove last n items for testing
        for i in range(removeNWeeks):
            targetVal = testLocationData.pop()

        #get locational input data and reshape it
        locationData = np.array(self.getIDs())
        #locationData = np.array(testLocationData)


        #reshape location date
        locationData = locationData.reshape((len(locationData), self.datasetFeatures))

        model = self.loadModel("xp.keras")

        # predict the next item
        last_sequence = locationData[-self.datasetInputLength:].reshape((1, self.datasetInputLength, self.datasetFeatures))
        nextLocationPredection = model.predict(last_sequence, verbose=0)
        print(nextLocationPredection,"\n")
        predictedLoc = np.argmax(nextLocationPredection)
        
        if predictedLoc == locationData[-1][0]:
            predictedLoc = self.predictNextMath(self.getIDs())
    
        



        print(f"Predicted Next Item in Sequence: {predictedLoc}")
        print("0:", nextLocationPredection[0][0])
        print("1:", nextLocationPredection[0][1])
        print("2:", nextLocationPredection[0][2])
        print(f"\n\nPrev Week: {locationData[-1][0]}")
        print(f"Target: {targetVal}")

        print(predictedLoc)
        return(predictedLoc)


        
  
        
predictor = XurPredictor(DATABASE_PATH)

#predictor.trainModel("xp.keras",500)

predictor.makePrediction()
