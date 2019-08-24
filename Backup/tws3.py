from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
from tkinter import *
from tkinter import ttk
from msvcrt import getch
import time

class Application(Frame):

	def __init__(self, master):
			ttk.Frame.__init__(self,master)
		
			self.grid()
			self.create_widgets()
			self.account_code = None
			self.symbol_id, symbol = 0, 'EUR.USD'
			
	def create_widgets(self):
		myfont = ('Lucida Grande',10)
	
		self.btnconnect = ttk.Button(self, text='Connect', command=self.main)
		self.btnconnect.grid(row=0, column=0)
		self.btndisconnect = ttk.Button(self, text='Disconnect', command=self.main).grid(row=0, column=1, sticky=W)
		self.btnrqdata = ttk.Button(self, text='Request', command=self.main).grid(row=0, column=2, sticky=W)
		
		
		n= ttk.Notebook(root, width=550, height=350)
		f1= ttk.Frame(n)
		f2= ttk.Frame(n)
		n.add(f1, text='One')
		n.add(f2, text='Two')
		n.grid(row=3, column = 0, padx = 5,pady=5,sticky=W)
		
		self.listbox1 = Listbox(f1, font=myfont, width=7)
		#was auch immer das hier ist -> self.listbox1.bind('<Double-Button-1>', self.OnDoubleClick_listbox)
		self.listbox1.insert(1, 'USD')
		self.listbox1.insert(2, 'JPY')
		self.listbox1.insert(3, 'CAD')
		self.listbox1.grid(row=0, rowspan=5,column=0,padx=5)
		
		
		self.label4 = Label(f1, font=myfont, text="Symbol").grid(row=0, column=1)
		self.label5 = Label(f1, font=myfont, text="Quantity").grid(row=0, column=2)
		self.label6 = Label(f1, font=myfont, text="Limit Price").grid(row=0, column=3)
		self.label7 = Label(f1, font=myfont, text="Market").grid(row=0, column=4)
		
		self.cbSymbol = ttk.Combobox(f1, font = myfont, width=6, textvariable = varSymbol)
		#self.cbSymbol.bind("<Return>", self.main)
		#self.cbSymbol.bind('<<ComboboxSelected>>',self.main)
		self.cbSymbol['values'] = ('USD','JPY','CAD')
		self.cbSymbol.grid(row=1, column=1, sticky = W)
		
		self.cbMarkert = ttk.Combobox(f1, font=myfont, width=7, textvariable=varMarket).grid(row=1,column=4, sticky=W)
		
		self.label9 = Label(f1, font=myfont, text="Visible").grid(row=2, column=2)
		self.label10 = Label(f1, font=myfont, text="Primary Ex.").grid(row=2, column=3)
		self.label11 = Label(f1, font=myfont, text="TIF").grid(row=2, column=4)
		
		self.tbPrimaryEx = Entry(f1, font=myfont, width=8, textvariable=varPrimaryEx).grid(row=3,column=3, sticky=W)
		
		
		self.label12 = Label(f1, font=myfont,width=7, text="Bid").grid(row=4, column=2)
		self.label13 = Label(f1, font=myfont,width=7, text="Ask").grid(row=4, column=3)
		self.label14 = Label(f1, font=myfont,width=8, text="Last").grid(row=6, column=1)
		self.tbBid = Entry(f1,font=myfont,width=7,textvariable=varBid).grid(row=5, column=2, sticky=E)
		self.tbBid = Entry(f1,font=myfont,width=7,textvariable=varAsk).grid(row=5, column=3, sticky=E)
		self.tbBid = Entry(f1,font=myfont,width=7,textvariable=varMP).grid(row=6, column=2, sticky=W)
			
	def nextValidId_handler(self, msg):
		global id;
		id = msg.orderId
		# start now when you know it's connected
		self.makeRequest()

	def error_handler(self, msg):
		# only print interesting errors
		if msg.id > 0:
			print(msg)

	# show Bid and Ask quotes
	def my_BidAsk(self, msg):
		global bid,ask,midPoint  
		print(msg.field)		
		if msg.field == 1:
			print ('bid: %s' % ( msg.price)) 
			bid=msg.price
			print("änderung bid")
			varBid.set(bid)
		elif msg.field == 2:
			print ('ask: %s' % (msg.price)) 
			ask=msg.price
			print("änderung ask")
			varAsk.set(ask)
		# there is no last price in forex, maybe just the last close.

		if (bid is not None) and (ask is not None):
			midPoint = (bid + ask)/2
			varMP.set(midPoint)
			print ('global variables:',bid, ask, midPoint)
			# disconnect after getting all the data we want
			self.disconnect()
		
	def makeStkContract(self, contractTuple):
		newContract = Contract() 

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
		contractTuple = ('EUR', 'CASH', 'IDEALPRO','IDEALPRO','USD')
		#contractTuple = ('AMS', 'STK', 'SMART','TSE','CAD')
		stkContract = self.makeStkContract(contractTuple)
		print ('* * * * REQUESTING MARKET DATA * * * *')
		self.con.reqMktData(tickId, stkContract, '', False)


	def disconnect(self):
		print ('* * * * CANCELING MARKET DATA * * * *')
		self.con.cancelMktData(tickId)
		self.con.disconnect()

	def main(self):
		
		global con
		self.con = ibConnection(port=7497, clientId=325)
		self.con.register(self.error_handler, message.Error)
		self.con.register(self.nextValidId_handler, message.nextValidId)
		self.con.register(self.my_BidAsk, message.tickPrice)
		self.con.connect() 
		time.sleep(1)
	

bid = None
ask = None
midPoint = None
root = Tk()
root.title("Connect to IB TWS")
root.geometry('600x480')
root.attributes('-topmost', True)
varBid = StringVar()
varAsk= StringVar()
varMP=StringVar()
varSymbol = StringVar(root, value='USD')
varMarket = StringVar(root, value='IDEALPRO')
varPrimaryEx = StringVar(root, value='IDEALPRO')
app = Application(root)


root.mainloop()


