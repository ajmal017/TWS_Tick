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
		myfont = ('Helvetica',10)

		#csv button
		self.btnconnect = ttk.Button(self, text='CSV', command=self.tick_csv)
		self.btnconnect.grid(row=0, column=0, sticky=E)

		#disconnect button
		self.btndisconnect = ttk.Button(self, text='Disconnect', command=self.disconnect).grid(row=1, column=0)
		
		self.label_led = Label(self, font=myfont, text="Connection").grid(row=0, column=1, padx=20)
		#Canvas for drawing circles
		self.circleCanvas = Canvas(self, width=50, height=50)
		self.circleCanvas.grid(row=1, column=1)
		self.circleCanvas.create_oval(10, 10, 40, 40, width=0, fill='red')

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
	
	def led_on(self):
		self.circleCanvas.create_oval(10, 10, 40, 40, width=0, fill='green')

	def led_off(self):
		self.circleCanvas.create_oval(10, 10, 40, 40, width=0, fill='red')

	def nextValidId_handler(self, msg):
		#called by tick_csv
		id = msg.orderId
		self.makeRequest()

	def error_handler(self, msg):
		#called by tick_csv & onetick
		if msg.id != None:
			if msg.id > 0:
				print(msg)

	def BidAsk(self, msg):
		#create bid ask csv file
		#called by tick_csv
		if msg.field == 1:
			self.bid=msg.price
			varBid.set(msg.price)
		elif msg.field==0:
			self.bidsz=msg.size
		elif msg.field == 2:
			self.ask=msg.price
			varAsk.set(msg.price)
		elif msg.field==3:
			self.asksz=msg.size

		#TODO: Only write when not empty
		if self.bid != None and self.bidsz != None and self.ask != None and self.asksz:
			self.writer.writerow([time.strftime("%H:%M:%S"), self.bid, self.bidsz, self.ask, self.asksz])

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
		self.tickId = 1
		#contractTuple = ('symbol', 'securityType', 'exchange','primaryExchange', 'currency')
		contractTuple = ('EUR', 'CASH', 'IDEALPRO','IDEALPRO', varSymbol.get())
		stkContract = self.makeStkContract(contractTuple)
		print ('* * * * REQUESTING MARKET DATA * * * *')

		#data request
		self.con.reqMktData(self.tickId, stkContract, '', False)

	def disconnect(self):
		#linked to button "disconnect"
		#called by tick_csv
		connected = varCon.get()

		if not connected:
			self.led_off()
		else:
			self.con.cancelMktData(self.tickId)
			self.con.disconnect()
			self.led_off()
			bid = None
			ask = None
			connected = FALSE

	def tick_csv(self):
		#linked to button "csv"
		connected = varCon.get()

		#init variables
		self.bid = None
		self.bidsz = None
		self.ask = None
		self.asksz = None

		#create csv
		init_time = time.strftime("%d-%m-%Y_%H'%M'%S")
		security = varSymbol.get()
		myFile =  "data/Tick/EUR." + str(security) + "_" + str(init_time) +  ".txt"

		#create csv header
		csvheader= ["Time","Bid","Bidsize","Ask","Asksize"]
		f= open(str(myFile),"w+")
		self.writer = csv.writer(f, delimiter=' ')
		self.writer.writerow(csvheader)

		#check if connected
		if connected:
			self.disconnect()
			self.led_off()
		connected = TRUE
		self.led_on()

		#establish connection
		self.con = ibConnection(port=myPort, clientId=myclientId)
		self.con.register(self.error_handler, message.Error)
		self.con.register(self.nextValidId_handler, message.nextValidId)
		self.con.register(self.BidAsk, message.tickPrice, message.tickSize)
		self.con.connect()

#user variables
myPort = 7497
myclientId = 325

#finalize GUI
root = Tk()
root.title("Connect to IB TWS")
root.geometry('600x480')
root.attributes('-topmost', True)

#GUI variables
varCon = BooleanVar(root, value=FALSE)
CheckVar = BooleanVar(root, value=FALSE)
varBid= StringVar()
varAsk= StringVar()
varSymbol = StringVar(root, value='USD')
varMarket = StringVar(root, value='IDEALPRO')
varPrimaryEx = StringVar(root, value='IDEALPRO')

#launch
app = Application(root)
root.mainloop()
