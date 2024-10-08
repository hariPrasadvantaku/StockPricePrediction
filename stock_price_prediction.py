# -*- coding: utf-8 -*-
"""stock price prediction

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15KO5KSWp-NIgXakcqWB6cnjhtXTAmSDZ

using artifical recurrent neural network called Long Short Term Memory(LSTM) to predict the closing stock price of a corparation
"""

#import libraries
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.callbacks import EarlyStopping
from datetime import datetime
plt.style.use('fivethirtyeight')

#get the stock quote
df=yf.download('GS',start='2012-01-01',end='2024-09-13')
df

#no of rows and columns
df.shape

#visulize the closeing price histroy
plt.figure(figsize=(16,8))
plt.title('close price histroy')
plt.plot(df['Close'])
plt.xlabel('Date',fontsize=18)
plt.ylabel('Close Price USD($)',fontsize=18)
plt.show()

#create new dataframe with only the close column
data=df.filter(['Close'])
#convert the dataframe to an numpy array
dataset=data.values
#get the number of rows to train the model on
training_data_len=math.ceil(len(dataset)*.8)
training_data_len

#scale the data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)
scaled_data

#create the training data set
#create the scaled training data set
train_data = scaled_data[0:training_data_len,:]
#split the data into x_train and y_train data sets
x_train = []
y_train = []
for i in range(60,len(train_data)):
  x_train.append(train_data[i-60:i,0])
  y_train.append(train_data[i,0])
  if i<=61:
    print(x_train)
    print(y_train)
    print()

#convert the x_train and y_train to numpy array
#to train LSTM model
x_train,y_train = np.array(x_train),np.array(y_train)

#reshape the data
#because the LSTM network experts the input to be three-dimensional in no of samples no of time steps and no of features
x_train = np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
x_train.shape

#build the LSTM model
model = Sequential()
model.add(LSTM(units=50,return_sequences=True,input_shape=(x_train.shape[1],1)))
model.add(LSTM(units=50,return_sequences=False))
model.add(Dense(units=25))
model.add(Dense(units=1))

#compile the model
model.compile(optimizer='adam',loss='mean_squared_error')

#train the model
model.fit(x_train,y_train,batch_size=1,epochs=1)

#create the testing data set
#create a new array containing sales values
test_data = scaled_data[training_data_len-60:,:]
#create the data sets x_test and y_test
x_test=[]
y_test=dataset[training_data_len:,:]
for i in range(60,len(test_data)):
  x_test.append(test_data[i-60:i,0])

#convert the data to a numpy array
x_test = np.array(x_test)

#reshape the data
x_test = np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))

#get the models predicted price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#get the root mean squreed error(RSME)
rmse = np.sqrt(np.mean(predictions-y_test)**2)
rmse

#plot the data
train = data[:training_data_len]
vaild = data[training_data_len:]
vaild['Predictions'] = predictions
#Visulize the data
plt.title('Model')
plt.xlabel('Date',fontsize=18)
plt.ylabel('Close Price USD ($)',fontsize=18)
plt.plot(train['Close'])
plt.plot(vaild[['Close','Predictions']])
plt.legend(['Train','Val','Predictions'],loc='lower right')
plt.show()

#show the valid and predicted prices
vaild

# Get the last date in the existing data to calculate the future days
last_date = df.index[-1]
last_date = pd.to_datetime(last_date)

from datetime import datetime
#get user input for the future date
user_data_input = input("Enter the future date (YYYY-MM-DD) for stock prediction: ")
user_date = datetime.strptime(user_data_input, '%Y-%m-%d')

# Calculate the number of days from the last available date to the user-specified date
days_difference = (user_date - last_date).days

if days_difference <= 0:
  print("Please enter a future date after the last available date.")
else:
  #prepare the input data to predict future stock prices
  last_60_days = data['Close'][-60:].values.reshape(-1,1)
  last_60_days_scaled = scaler.transform(last_60_days)
  #use the last 60 days from the training data
  X_test = []
  X_test.append(last_60_days_scaled)
  X_test = np.array(X_test)
  X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

  #predict the price for the specified future date
  for i in range(days_difference):
    predicted_price = model.predict(X_test)
    predicted_price_unscaled = scaler.inverse_transform(predicted_price)
    #update last 60 days scaled with the new predicted price
    last_60_days_scaled = np.append(last_60_days_scaled,predicted_price)
    last_60_days_scaled = last_60_days_scaled[-60:]#keep only last 60 days

    #update X_test for the next prediction
    X_test = []
    X_test.append(last_60_days_scaled)
    X_test = np.array(X_test)
    X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
#print the predicted price for the specified future date
print(f"Predicted stock price for {user_data_input} is : ${predicted_price_unscaled[0][0]:.2f}")

plt.figure(figsize=(16,8))
plt.title('Predicted stock prices for user specified date')
plt.scatter([user_date],[predicted_price_unscaled[0][0]],color='red',label='Predicted Price')
plt.xlabel('Date')
plt.ylabel('Close Price USD ($)')
plt.legend()
plt.show()