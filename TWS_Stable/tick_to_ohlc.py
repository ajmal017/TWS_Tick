#convert tick data to ohlc data using pandas

import pandas as pd
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt
from datetime import *

#read file
file_name = "EUR.USD 28.05.2019 11'25'50"
df = pd.read_csv("data/tick/" + str(file_name) + ".txt", names=['Time','Bid', 'Bidsize','Ask', 'Asksize', 'Midpoint'], delim_whitespace=True)

#format file for pandas ohlc
df.drop(df.index[0], inplace=True)
cache= df['Time']
df['Date'] = '01.01.2000'
df['date_time'] = df['Date'] + ' ' + df['Time']
cache= df['date_time']
df.drop(columns=['Bidsize','Asksize','Midpoint','Time','Date'],inplace=True)
df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')
df.set_index('date_time', inplace=True)
data_ask =  pd.to_numeric(df['Ask']).resample('1Min').ohlc()
data_bid =  pd.to_numeric(df['Bid']).resample('1Min').ohlc()
ohlc= data_bid.copy()

#create candlestick ohlc chart w/ mpl_finance
f1, ax = plt.subplots(figsize = (10,5))
candlestick_ohlc(ax, zip(mdates.date2num(ohlc.index.to_pydatetime()),ohlc['open'],ohlc['high'],ohlc['low'],ohlc['close']), width=0.5/(24*60), colorup='green', colordown='red') #width=0.5/(24*x) x=60/candletime -> 5 min chart -> x=60/5=12
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

#save & show plot
plt.savefig("data/ohlc/img/" + str(file_name) +" ohlc 5min.png")
plt.show()

#save converted file
ohlc.to_csv("data/ohlc/" + str(file_name) + " ohlc 5min.txt", sep = ",")
