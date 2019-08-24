from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from tkinter import *
from tkinter import ttk
from msvcrt import getch
import csv, time


class Application(Frame):

	def __init__(self, master):
			ttk.Frame.__init__(self,master)

			self.grid()
			self.create_widgets()
			self.account_code = None
			self.symbol_id, symbol = 0, 'EUR.USD'

	def create_widgets(self):
		myfont = ('Lucida Grande',10)

		self.btnconnect = ttk.Button(self, text='CSV', command=self.tick_csv)
		self.btnconnect.grid(row=0, column=0)
		self.btndisconnect = ttk.Button(self, text='Disconnect', command=self.disconnect).grid(row=0, column=2, sticky=W)
		self.btnrqdata = ttk.Button(self, text='Tick', command=self.onetick).grid(row=0, column=1, sticky=W)
		#self.btnlearn = ttk.Button(self, text='Learn', command=self.onetick).grid(row=0, column=3, sticky=W)


		n= ttk.Notebook(root, width=550, height=350)
		f1= ttk.Frame(n)
		f2= ttk.Frame(n)
		n.add(f1, text='One')
		n.add(f2, text='Two')
		n.grid(row=3, column = 0, padx = 5,pady=5,sticky=W)

		#Liste an der Seite
		#self.listbox1 = Listbox(f1, font=myfont, width=7)
		#was auch immer das hier ist -> self.listbox1.bind('<Double-Button-1>', self.OnDoubleClick_listbox)
		#self.listbox1.insert(1, 'USD')
		#self.listbox1.insert(2, 'JPY')
		#self.listbox1.insert(3, 'CAD')
		#self.listbox1.grid(row=0, rowspan=5,column=0,padx=5)


		self.label4 = Label(f1, font=myfont, text="Symbol").grid(row=0, column=1)
		self.label7 = Label(f1, font=myfont, text="Market").grid(row=0, column=2)

		self.cbSymbol = ttk.Combobox(f1, font = myfont, width=6, textvariable = varSymbol)
		self.cbSymbol.bind("<Return>", self.cbSymbol_onEnter)
		self.cbSymbol.bind('<<ComboboxSelected>>',self.cbSymbol_onEnter)
		self.cbSymbol['values'] = ('USD','JPY','CAD','GBP')
		self.cbSymbol.grid(row=1, column=1, sticky = W)

		self.cbMarkert = ttk.Combobox(f1, font=myfont, width=10, textvariable=varMarket).grid(row=1,column=2, sticky=W)

		self.label10 = Label(f1, font=myfont, text="Primary Ex.").grid(row=0, column=3)


		self.tbPrimaryEx = Entry(f1, font=myfont, width=10, textvariable=varPrimaryEx).grid(row=1,column=3, sticky=W)


		self.label12 = Label(f1, font=myfont,width=7, text="Bid").grid(row=2, column=1)
		self.label13 = Label(f1, font=myfont,width=7, text="Ask").grid(row=2, column=2, stick = W)
		self.label14 = Label(f1, font=myfont,width=7, text="Midpoint").grid(row=2, column=3)
		self.tbBid = Entry(f1,font=myfont,width=8,textvariable=varBid).grid(row=3, column=1, sticky=W)
		self.tbAsk = Entry(f1,font=myfont,width=8,textvariable=varAsk).grid(row=3, column=2, sticky=W)
		self.tbMP = Entry(f1,font=myfont,width=12,textvariable=varMP).grid(row=3, column=3, sticky=W)

	def cbSymbol_onEnter(self, event):
		varSymbol.set(varSymbol.get().upper())

	def nextValidId_handler(self, msg):
		global id;
		id = msg.orderId
		# start now when you know it's connected
		self.makeRequest()

	def error_handler(self, msg):
		# only print interesting errors
		if msg.id != None:
			if msg.id > 0:
				print(msg)

	# show Bid and Ask quotes
	def my_BidAsk_one(self, msg):
		global bid,ask,midPoint
		if msg.field == 1:
			#print ('bid: %s' % ( msg.price))
			bid=msg.price
			varBid.set(bid)
		elif msg.field == 2:
			#print ('ask: %s' % (msg.price))
			ask=msg.price
			varAsk.set(ask)
		# there is no last price in forex, maybe just the last close.

		if (bid is not None) and (ask is not None):
			midPoint = (bid + ask)/2
			varMP.set(midPoint)
			print ('bid: %s' % (bid))
			print ('ask: %s' % (ask))
			print ('global variables:',bid, ask, midPoint)
			# disconnect after getting all the data we want
			self.disconnect()

	def my_BidAsk(self, msg):
		global bid,ask,bidsz,asksz, midPoint, vol, timetest2
		if msg.field == 1:
			#print ('bid: %s' % ( msg.price))
			bid=msg.price
			varBid.set(bid)
		elif msg.field==0:
			#print ('bid size: %s' % (msg.size))
			bidsz=msg.size
		elif msg.field == 2:
			#print ('ask: %s' % (msg.price))
			ask=msg.price
			varAsk.set(ask)
		elif msg.field==3:
			#print ('ask size: %s' % (msg.size))
			asksz=msg.size
		elif msg.field==8:
			print ('++++++++++++++++++++++vol: %s' % (msg.size))
			vol=msg.size
		# there is no last price in forex, maybe just the last close.
		if (bid is not None) and (ask is not None):
			midPoint = (bid + ask)/2
			varMP.set(midPoint)
			# disconnect after getting all the data we want
		#timetest1 = time.strftime("%H%M%S")
		#if int(timetest1) > (int(timetest2) + 4):
		#if timetest1 != timetest2:
		if bid != None and ask != None and asksz != None and bidsz != None and midPoint != None:
			timetest2= time.strftime("%H%M%S")
			writer.writerow([time.strftime("%H:%M:%S"), bid, bidsz, ask, asksz, midPoint])
			time.sleep(10)
			print ('* * * * SLEEP * * * *')

	def makeStkContract(self, contractTuple):
		newContract = Contract()
		#if contractTuple[4] != varSymbol.get():
			#contractTuple[4] = varSymbol.get()

		newContract.m_symbol = contractTuple[0]
		newContract.m_secType = contractTuple[1]
		newContract.m_exchange = contractTuple[2]
		newContract.m_primaryExch=contractTuple[3]
		newContract.m_currency = contractTuple[4]

		print ('Contract Values:%s,%s,%s,%s,%s:' % contractTuple)
		return newContract

	def makeRequest(self):
		global tickId
		tickId = 1
		contractTuple = (varSymbol.get())
		contractTuple = ('EUR', 'CASH', 'IDEALPRO','IDEALPRO','GBP')
		stkContract = self.makeStkContract(contractTuple)
		print ('* * * * REQUESTING MARKET DATA * * * *')
		self.con.reqMktData(tickId, stkContract, '', False)



	def disconnect(self):
		global status
		if status == 0:
			print('* * * * NOT CONNECTED * * * *')
		else:
			print ('* * * * DISCONNECTING * * * *')
			self.con.cancelMktData(tickId)
			self.con.disconnect()
			bid = None
			ask = None
			midPoint = None
			status = 0


	def onetick(self):
		global con, status
		if status == 1:
			self.disconnect()
		status = 1
		self.con = ibConnection(port=7497, clientId=325)
		self.con.register(self.error_handler, message.Error)
		self.con.register(self.nextValidId_handler, message.nextValidId)
		self.con.register(self.my_BidAsk_one, message.tickPrice)
		self.con.connect()

	def tick_csv(self):
		global con, status, f, writer
		zeit = time.strftime("%d.%m.%Y %H'%M'%S")
		security = varSymbol.get()
		myFile = "C:/Users/Tobias/Documents/Coding/data/EUR." + str(security) + " " + str(zeit) +  ".txt"
		f= open(myFile,"w+")
		writer = csv.writer(f, delimiter=' ')
		csvheader= ["Time","Bid","Bidsize","Ask","Asksize", "Midpoint"]
		writer.writerow(csvheader)
		if status == 1:
			self.disconnect()
		status = 1
		self.con = ibConnection(port=7497, clientId=325)
		self.con.register(self.error_handler, message.Error)
		self.con.register(self.nextValidId_handler, message.nextValidId)
		self.con.register(self.my_BidAsk, message.tickPrice, message.tickSize)
		self.con.connect()


global status,timetest2
timetest2 = 0
status = 0
bid = None
ask = None
midPoint = None
bidsz = None
asksz = None
tickId = None
root = Tk()
root.title("Connect to IB TWS")
root.geometry('600x480')
root.attributes('-topmost', True)
varBid = StringVar()
varAsk= StringVar()
varMP=StringVar()
varSymbol = StringVar(root, value='GBP')
varMarket = StringVar(root, value='IDEALPRO')
varPrimaryEx = StringVar(root, value='IDEALPRO')

app = Application(root)


root.mainloop()
