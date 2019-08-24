import time
from tkinter import *
from tkinter import ttk
from ib.ext.Contract import Contract
from ib.opt import Connection, message
from ib.ext import EWrapper, EClientSocket
from msvcrt import getch

class Application(Frame):

	def __init__(self, master):
		ttk.Frame.__init__(self, master)
	
		self.grid()
		self.create_widgets()
		self.account_code = None
		self.symbol_id, self.symbol = 0, 'EUR.USD'
		
	def create_widgets(self):
	
		myfont = ('Lucida Grande',10)
	
		self.btnconnect = ttk.Button(self, text='Connect', command=self.connect)
		self.btnconnect.grid(row=0, column=0)
		self.btndisconnect = ttk.Button(self, text='Disconnect', command=self.disconnect).grid(row=0, column=1, sticky=W)
		self.btnrqdata = ttk.Button(self, text='Request', command=self.cbSymbol_onEnter).grid(row=0, column=2, sticky=W)
		
		
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
		self.cbSymbol.bind("<Return>", self.cbSymbol_onEnter)
		self.cbSymbol.bind('<<ComboboxSelected>>',self.cbSymbol_onEnter)
		self.cbSymbol['values'] = ('USD','JPY','CAD')
		self.cbSymbol.grid(row=1, column=1, sticky = W)
		
		self.spinQuantity = Spinbox(f1, font=myfont, increment=100, from_=0, to_=1000, width=7, textvariable=varQuantity).grid(row=1,column=2)
		
		self.spinLimitPrice = Spinbox(f1, font=myfont,format='%8.2f', increment=0.1,  from_=0.0, to_=1000.0, width=7, textvariable=varLimitPrice).grid(row=1,column=3)
		
		self.cbMarkert = ttk.Combobox(f1, font=myfont, width=7, textvariable=varMarket).grid(row=1,column=4, sticky=W)
		
		self.label8 = Label(f1, font=myfont, text="Ordertype").grid(row=2, column=1, sticky=W)
		self.label9 = Label(f1, font=myfont, text="Visible").grid(row=2, column=2)
		self.label10 = Label(f1, font=myfont, text="Primary Ex.").grid(row=2, column=3)
		self.label11 = Label(f1, font=myfont, text="TIF").grid(row=2, column=4)
		
		self.cbOrdertype = ttk.Combobox(f1, font = myfont, width=6, textvariable = varOrderType)
		self.cbOrdertype['values'] = ('LMT','MKT','STP','STP LMT', 'TRAIL', 'MOC', 'LOC')
		self.cbOrdertype.grid(row=3, column=1, sticky = W)
		
		self.tbPrimaryEx = Entry(f1, font=myfont, width=8, textvariable=varPrimaryEx).grid(row=3,column=3, sticky=W)
		
		self.cbTIF= ttk.Combobox(f1, font = myfont, width=7, textvariable = varTIF)
		self.cbTIF['values'] = ('GTC','DAY')
		self.cbTIF.grid(row=3, column=4, sticky = W)
		
		self.label12 = Label(f1, font=myfont,width=7, text="Bid").grid(row=4, column=2)
		self.label13 = Label(f1, font=myfont,width=7, text="Ask").grid(row=4, column=3)
		self.label14 = Label(f1, font=myfont,width=8, text="Last").grid(row=6, column=1)
		self.tbBid = Entry(f1,font=myfont,width=7,textvariable=varBid).grid(row=5, column=2, sticky=E)
		self.tbBid = Entry(f1,font=myfont,width=7,textvariable=varAsk).grid(row=5, column=3, sticky=E)
		self.tbBid = Entry(f1,font=myfont,width=8,textvariable=varLast).grid(row=6, column=2, sticky=W)
		
		

	def connect(self):
		self.tws_conn = Connection.create(port=7496, clientId=325)
		self.tws_conn.connect()
		time.sleep(1)
		
		self.register_callback_functions()
		
	def disconnect(self):
		self.tws_conn.disconnect()
		
	def register_callback_functions(self):
		self.tws_conn.registerAll(self.server_handler)
		self.tws_conn.register(self.error_handler)
		self.tws_conn.register(self.tick_event, message.tickPrice, message.tickSize)
		print("registercallback")
	
	def server_handler(self, msg):
		if msg.typeName == "nextValidID":
			self.order_id = msg.orderID
		elif msg.typeName == "managedAccounts":
			self.account_code = msg.accountsList
		elif msg.typeName == "updatePortfolio" and msg.contract.m_symbol == self.symbol:
			self.unrealized_pnl = msg.unrealizedPNL
			self.realized_pnl = msg.realizedPNL
			print(self.unrealized_pnl)
			self.position = msg.position
			self.average_price = msg.averageCost
		elif msg.typeName == "error" and msg.id != -1:
			return
			
	def error_handler(self, msg):
		print("error")
		if msg.typeName == 'error' and msg.id != -1:
			print('Server error:',msg)
			
	def cbSymbol_onEnter(self, event):
		self.tws_conn.reqAccountUpdates(False, self.account_code)
		varSymbol.set(varSymbol.get().upper())
		mytext=varSymbol.get()
		vals = self.cbSymbol.cget('values')
		self.cbSymbol.select_range(0, END)
		if not vals:
			self.cbSymbol.configure(values = (mytext, ))
		elif mytext not in vals:
			self.cbSymbol.configure(values = vals + (mytext, ))
		mySymbol = varSymbol.get()
		self.symbol = mySymbol
		self.cancel_market_data()
		self.request_market_data(self.symbol_id, self.symbol)
		time.sleep(1)
		self.request_account_updates(self.account_code)
		print("cbsymbolonenter")
		#varBid.set('0.00')
		#varAsk.set('0.00')
		
	def monitor_position(self, msg):
		print("monitor")
		print ('Last Price = %s' & (self.last_prices))
		#varLast.set(self.last_prices)
		varBid.set(self.bid_price)
		varAsk.set(self.Ask_price)
		
	def create_contract(self, symbol, sec_type, exch, prim_exchange, curr):
		contract = Contract()
		contract.m_symbol = symbol
		contract.m_sectype = sec_type
		contract.m_exchange = exch
		contract.m_primaryExch = prim_exchange
		contract.m_currency = curr
		return contract
		
	def request_account_updates(self, account_code):
		print("account")
		self.tws_conn.reqAccountUpdates(True, self.account_code)
		
	def cancel_market_data(self):
		self.tws_conn.cancelMktData(self.symbol_id)
		
	def request_market_data(self, symbol_id, symbol):
		print("mktdata")
		print(symbol)
		contract = self.create_contract(symbol, 'CASH', 'IDEALPRO', 'IDEALPRO', 'JPY')
		self.tws_conn.reqMktData(symbol_id, contract, '', False)
		time.sleep(2)
		print("sleep")
	
	def tick_event(self, msg):
		print("tick")
		if msg.field == 1:
			self.bid_price = msg.price
			print(self.bid_price)
		if msg.field == 2:
			self.ask_price = msg.price
			print(self.ask_price)
		if msg.field == 4:
			self.last_prices = msg.price
			print(self.last_prices)
			self.monitor_position(msg)
	
root = Tk()
root.title("Connect to IB TWS")
root.geometry('600x480')
root.attributes('-topmost', True)
varSymbol = StringVar(root, value='EUR')
varQuantity = StringVar(root, value='100')
varLimitPrice = StringVar()
varMarket = StringVar(root, value='IDEALPRO')
varOrderType = StringVar(root, value='LMT')
varPrimaryEx = StringVar(root, value='IDEALPRO')
varTIF = StringVar(root, value='DAY')
varBid = StringVar()
varAsk = StringVar()
varLast= StringVar()
app = Application(root)


root.mainloop()