#Extracts realtime tick data via the tws Api
#requires api-enabled tws

from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from tkinter import *
from tkinter import ttk
import csv
import time

class Application(Frame):


	def __init__(self, master):
			ttk.Frame.__init__(self,master)

			#create GUI
			self.grid()
			self.create_widgets()
			self.account_code = None
			self.symbol_id, symbol = 0, 'EUR.USD'

	def create_widgets(self):
		myfont = ('Lucida Grande',10)

		#csv button
		self.btnconnect = ttk.Button(self, text='CSV', command=self.tick_csv)
		self.btnconnect.grid(row=0, column=0)

		#disconnect button
		self.btndisconnect = ttk.Button(self, text='Disconnect', command=self.disconnect).grid(row=0, column=2, sticky=W)
		self.btnrqdata = ttk.Button(self, text='Tick', command=self.onetick).grid(row=0, column=1, sticky=W)

		#Tabs
		n= ttk.Notebook(root, width=550, height=350)
		f1= ttk.Frame(n)
		f2= ttk.Frame(n)
		n.add(f1, text='One')
		n.add(f2, text='Two')
		n.grid(row=3, column = 0, padx = 5,pady=5,sticky=W)

		#dropdown label
		self.label1 = Label(f1, font=myfont, text="Symbol").grid(row=0, column=1)
		self.label2 = Label(f1, font=myfont, text="Market").grid(row=0, column=2)
		self.label3 = Label(f1, font=myfont, text="Primary Ex.").grid(row=0, column=3)
		self.label4 = Label(f1, font=myfont,width=7, text="Bid").grid(row=2, column=1)
		self.label5 = Label(f1, font=myfont,width=7, text="Ask").grid(row=2, column=2, stick = W)

		#symbol dropdown
		self.cbSymbol = ttk.Combobox(f1, font = myfont, width=6, textvariable = varSymbol)
		self.cbSymbol.bind("<Return>", self.cbSymbol_onEnter)
		self.cbSymbol.bind('<<ComboboxSelected>>',self.cbSymbol_onEnter)
		self.cbSymbol['values'] = ('USD','JPY','CAD','GBP')
		self.cbSymbol.grid(row=1, column=1, sticky = W)

		#market & primary exchange dropdown
		self.cbMarkert = ttk.Combobox(f1, font=myfont, width=10, textvariable=varMarket).grid(row=1,column=2, sticky=W)
		self.tbPrimaryEx = Entry(f1, font=myfont, width=10, textvariable=varPrimaryEx).grid(row=1,column=3, sticky=W)

		#bid & ask box
		self.tbBid = Entry(f1,font=myfont,width=8,textvariable=varBid).grid(row=3, column=1, sticky=W)
		self.tbAsk = Entry(f1,font=myfont,width=8,textvariable=varAsk).grid(row=3, column=2, sticky=W)


	def cbSymbol_onEnter(self, event):
		#enables symbol change via dropdown
		#called by create_widgets
		varSymbol.set(varSymbol.get().upper())

	def nextValidId_handler(self, msg):
		#called by tick_csv & onetick
		global id;
		id = msg.orderId
		self.makeRequest()

	def error_handler(self, msg):
		#only print interesting errors
		#called by tick_csv & onetick
		if msg.id != None:
			if msg.id > 0:
				print(msg)


	def my_BidAsk_oneTick(self, msg):
		#show one tick Bid and Ask quotes
		#called by onetick
		global bid,ask
		if msg.field == 1:
			bid=msg.price
			varBid.set(bid)
		elif msg.field == 2:
			ask=msg.price
			varAsk.set(ask)

		if bid != None and ask != None:
			self.disconnect()
			bid=None
			ask=None

	def my_BidAsk(self, msg):
		#create bid ask csv file
		#called by tick_csv

		global bid, ask, bidsz, asksz, vol
		if msg.field == 1:
			bid=msg.price
			varBid.set(msg.price)
		elif msg.field==0:
			bidsz=msg.size
		elif msg.field == 2:
			ask=msg.price
			varAsk.set(msg.price)
		elif msg.field==3:
			asksz=msg.size
		elif msg.field==8:
			print ('vol: %s' % (msg.size))
			vol=msg.price

		#writerow only when data is available
		if bid != None and ask != None and asksz != None and bidsz != None:
			writer.writerow([time.strftime("%H:%M:%S"), bid, bidsz, ask, asksz])

	def makeStkContract(self, contractTuple):
		#called by makeRequest
		newContract = Contract()

		newContract.m_symbol = contractTuple[0]
		newContract.m_secType = contractTuple[1]
		newContract.m_exchange = contractTuple[2]
		newContract.m_primaryExch=contractTuple[3]
		newContract.m_currency = contractTuple[4]

		print ('Contract Values:%s,%s,%s,%s,%s:' % contractTuple)
		return newContract

	def makeRequest(self):
		#called by nextValidId_handler

		global tickId
		tickId = 1
		#contractTuple = ('symbol', 'securityType', 'exchange','primaryExchange', 'currency')
		contractTuple = ('EUR', 'CASH', 'IDEALPRO','IDEALPRO', varSymbol.get())
		stkContract = self.makeStkContract(contractTuple)
		print ('* * * * REQUESTING MARKET DATA * * * *')

		#data request
		self.con.reqMktData(tickId, stkContract, '', False)

	def disconnect(self):
		#linked to button "disconnect"
		#called by tick_csv & onetick

		global status
		if status == 0: #status = connection status
			print('* * * * NOT CONNECTED * * * *')
		else:
			print('* * * * DISCONNECTING * * * *')
			self.con.cancelMktData(tickId)
			self.con.disconnect()
			bid = None
			ask = None
			status = 0


	def onetick(self):
		#linked to button "tick"
		global con, status

		#check if connected
		if status == 1: #status = connection status
			self.disconnect()
		status = 1

		#establish connection
		#port & clientId may need to be altered
		self.con = ibConnection(port=7497, clientId=325)
		self.con.register(self.error_handler, message.Error)
		self.con.register(self.nextValidId_handler, message.nextValidId)
		self.con.register(self.my_BidAsk_oneTick, message.tickPrice)
		self.con.connect()

	def tick_csv(self):
		#linked to button "csv"
		global con, status, writer

		#create csv
		zeit = time.strftime("%d.%m.%Y %H'%M'%S")
		security = varSymbol.get()
		myFile = "C:/Users/Tobias/Documents/Coding/data/EUR." + str(security) + " " + str(zeit) +  ".txt"

		#create csv header
		csvheader= ["Time","Bid","Bidsize","Ask","Asksize"]
		f= open(myFile,"w+")
		writer = csv.writer(f, delimiter=' ')
		writer.writerow(csvheader)

		#check if connected
		if status == 1:
			self.disconnect()
		status = 1

		#establish connection
		self.con = ibConnection(port=7497, clientId=325)
		self.con.register(self.error_handler, message.Error)
		self.con.register(self.nextValidId_handler, message.nextValidId)
		self.con.register(self.my_BidAsk, message.tickPrice, message.tickSize)
		self.con.connect()

#define variables
global status
status = 0 #status = conncection status (1=connected; 0=not connected)
bid = None
ask = None
bidsz = None
asksz = None
tickId = None

#finalize GUI
root = Tk()
root.title("Connect to IB TWS")
root.geometry('600x480')
root.attributes('-topmost', True)

#GUI variables
varBid= StringVar()
varAsk= StringVar()
varSymbol = StringVar(root, value='USD')
varMarket = StringVar(root, value='IDEALPRO')
varPrimaryEx = StringVar(root, value='IDEALPRO')

#launch
app = Application(root)
root.mainloop()
