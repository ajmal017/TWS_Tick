from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from tkinter import *
from tkinter import ttk
from msvcrt import getch
import time
			
def nextValidId_handler(msg, id):
	id = msg.orderId
	print("id:",id)
	# start now when you know it's connected
	makeRequest(tickId)

def error_handler(msg):
	# only print interesting errors
	if msg.id > 0:
		print(msg)

# show Bid and Ask quotes
def my_BidAsk(msg):
	global bid,ask    
	if msg.field == 1:
		print ('bid: %s' % ( msg.price)) 
		bid=msg.price
	elif msg.field == 2:
		print ('ask: %s' % (msg.price)) 
		ask=msg.price
	# there is no last price in forex, maybe just the last close.

	if (bid is not None) and (ask is not None):
		midPoint = (bid + ask)/2
		print ('global variables:',bid, ask, midPoint)
		# disconnect after getting all the data we want
		disconnect()
	
def makeStkContract(contractTuple):
	newContract = Contract() 

	newContract.m_symbol = contractTuple[0]
	newContract.m_secType = contractTuple[1]
	newContract.m_exchange = contractTuple[2]
	newContract.m_primaryExch=contractTuple[3]
	newContract.m_currency = contractTuple[4]

	print ('Contract Values:%s,%s,%s,%s,%s:' % contractTuple)
	return newContract

def makeRequest(tickId):

	contractTuple = ('EUR', 'CASH', 'IDEALPRO','IDEALPRO','USD')
	#contractTuple = ('AMS', 'STK', 'SMART','TSE','CAD')
	stkContract = makeStkContract(contractTuple)
	print ('* * * * REQUESTING MARKET DATA * * * *')
	print (tickId)
	con.reqMktData(tickId, stkContract, '', False)


def disconnect():
	print ('* * * * CANCELING MARKET DATA * * * *')
	con.cancelMktData(tickId)
	con.disconnect()

def main():
	global con
	con = ibConnection(port=7497, clientId=325)
	con.register(error_handler, message.Error)
	con.register(nextValidId_handler, message.nextValidId)
	con.register(my_BidAsk, message.tickPrice)
	con.connect() 
	time.sleep(1)
	
bid = None
ask = None
root = Tk()
global id
id = None
tickId = 1 
	

main()
id = None
main()
id = None
main()



