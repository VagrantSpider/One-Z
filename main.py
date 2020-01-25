from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from random import randint
import os, pyperclip, json,subprocess
import netifaces as ni
import DB

global PROGRAM_DIR; PROGRAM_DIR = os.path.dirname(os.path.realpath(__file__))
global DB_PATH; DB_PATH ='%s/db.sqlite3' %PROGRAM_DIR
global LOCAL_IP; LOCAL_IP = "127.0.0.1"
global REMOTE_IP; REMOTE_IP = "127.0.0.1"
global LOCAL_PORT; LOCAL_PORT = "4444"
global REMOTE_PORT; REMOTE_PORT = "6666"
global OS_TYPES; OS_TYPES = []
global FORMAT_TYPES; FORMAT_TYPES = ["Select an OS Type"]
global MAIN_WIN; MAIN_WIN = None
global FILTER_TYPES; FILTER_TYPES = []

class TrayIcon:

	def __init__(self, master):
		self.master = master
		self.master.wm_attributes('-type', 'splash')
		self.master.wm_attributes("-topmost", 1)
		self.master.title("One-Z TrayIcon")


		global appicon
		appicon=PhotoImage(file="%s/app-icon.png" %PROGRAM_DIR)
		self.btn = Button(self.master, image=appicon, command=self.ToggleMain)
		self.buttonwidth = self.btn.winfo_reqwidth()
		self.buttonheight = self.btn.winfo_reqheight()
		self.btn.pack()

		self.master.geometry("{}x{}".format(self.buttonwidth, self.buttonheight))
		self.windowWidth = self.master.winfo_reqwidth()
		self.windowHeight = self.master.winfo_reqheight()
		self.positionRight = int(0)
		self.positionDown = int(self.master.winfo_screenheight() - self.buttonheight )

		# snaps window to bottom left corner
		self.master.geometry("+{}+{}".format(self.positionRight, self.positionDown))

		self.MainWin = Toplevel(self.master)
		self.MainWin.bind("<FocusOut>",self.LoseFocus)
		self.master.bind("<FocusOut>",self.LoseFocus)

		self.MainApp = MainWin(self.MainWin)
		self.MainWin.withdraw()

	def LoseFocus(self,evobj=None):
		#use xdotool to see if our app has lost focus
		rootfocus = subprocess.Popen(['xdotool', 'getwindowfocus' ,'getwindowname'], stdout=subprocess.PIPE)
		stdout, stderr = rootfocus.communicate()
		if "One-Z " not in str(stdout):
			self.MainWin.withdraw()
			self.master.lift()




	def ToggleMain(self):
		if self.MainWin.winfo_viewable():
			self.MainWin.withdraw()
		else:
			self.MainWin.deiconify()
			self.MainWin.geometry("+{}+{}".format((self.master.winfo_x()+15),(self.master.winfo_y()- self.MainWin.winfo_height() - 5)))
			self.MainWin.focus_set()


class MainWin:
	def __init__(self, master):
		global LOCALIP
		self.master = master
		self.master.title("One-Z Main")

		self.cfgWin = Toplevel(self.master)
		self.cfgapp = ConfigWin(self.cfgWin)
		self.cfgWin.withdraw()

		self.addWin = Toplevel(self.master)
		self.addapp = AddLinerWin(self.addWin)
		self.addWin.withdraw()

		self.editWin = Toplevel(self.master)
		self.editapp = EditLinerWin(self.editWin)
		self.editWin.withdraw()

		self.removeapp = LinerRemove(self.master)

		self.master.wm_attributes('-type', 'splash')
		self.master.wm_attributes("-topmost", 1)


		################## widgets ##################################3
		self.framevar = Frame(self.master, bd=1, relief=SOLID)
		self.framevar.grid(row = 0, column = 0,columnspan=4,sticky = NSEW, padx=5,pady=5)

		self.lblvars = Label(self.framevar,text="Address Variables")
		f = font.Font(self.lblvars, self.lblvars.cget("font"))
		f.configure(underline=True)
		self.lblvars.configure(font=f)
		self.lblvars.grid(row=0,column=0,padx=5,pady=5)

		self.framefilter = Frame(self.master, bd=1, relief=SOLID)
		self.framefilter.grid(row = 1, column = 0,columnspan=4,sticky = NSEW, padx=5,pady=5)

		self.lblostype = Label(self.framefilter,text="Target OS:")
		self.lblostype.grid(row = 0, column = 0,padx=5,pady=5)
		self.cbostype = ttk.Combobox(self.framefilter,state='readonly',values=OS_TYPES, width=10)
		self.cbostype.grid(row = 0,column = 1,padx=5,pady=5)
		self.populate_os_list()
		self.cbostype.bind("<<ComboboxSelected>>", self.callback_cbostype)

		self.lblformattype = Label(self.framefilter,text="Format:")
		self.lblformattype.grid(row = 0, column = 2,padx=5,pady=5)
		self.cbformattype = ttk.Combobox(self.framefilter,state='readonly',values=FORMAT_TYPES, width=10)
		self.cbformattype.grid(row = 0,column = 3,padx=5,pady=5)
		self.cbformattype.bind("<<ComboboxSelected>>", self.callback_cbformattype)

		self.lblfiltertype = Label(self.framefilter,text="Function:")
		self.lblfiltertype.grid(row = 0, column = 4)
		self.cbfiltertype = ttk.Combobox(self.framefilter,state='readonly',values=FILTER_TYPES)
		self.cbfiltertype.grid(row = 0,column = 5,padx=5, sticky=EW)
		self.cbfiltertype.bind("<<ComboboxSelected>>", self.callback_cbfiltertype)

		self.linerlist = Listbox(self.master,width=50)
		self.linerlist.grid(row = 2, column = 0,rowspan = 5, columnspan = 3, sticky=EW,padx=(5,0),pady=5)
		self.linerlist.bind('<<ListboxSelect>>', self.callback_linerlist_onselect)

		self.txtliner = Entry(self.master,textvariable=svliner)
		self.txtliner.grid(row=10,column=0,columnspan=4,sticky=EW,padx=5,pady=5)

		self.lbldescription = Message(self.master,text="", width=500, justify=LEFT,anchor=W,relief=SOLID) # could use Message
		self.lbldescription.grid(row=9,column=0,columnspan=4,sticky=EW,padx=5,pady=5)

		self.lbllocalip = Label(self.framevar,text=" Local IP:",justify=RIGHT)
		self.lbllocalip.grid(row = 1, column = 0,padx=5)
		self.txtlocalip = Entry(self.framevar,textvariable=svlocalip)
		self.txtlocalip.bind("<KeyRelease>", self.callback_parse_vars)
		self.txtlocalip.insert(END, LOCAL_IP)
		self.txtlocalip.grid(row = 1, column = 1,padx=5)

		self.lblremoteip = Label(self.framevar,text=" Remote IP:",justify=RIGHT)
		self.lblremoteip.grid(row = 1, column = 2,padx=5)
		self.txtremoteip = Entry(self.framevar,textvariable=svremoteip)
		self.txtremoteip.bind("<KeyRelease>", self.callback_parse_vars)
		self.txtremoteip.insert(END, REMOTE_IP)
		self.txtremoteip.grid(row = 1, column = 3,padx=5)

		self.lbllocalport = Label(self.framevar,text=" Local Port:",width=8,justify=RIGHT)
		self.lbllocalport.grid(row = 2, column = 0,padx=5,pady=(0,5))
		self.txtlocalport = Entry(self.framevar,textvariable=svlocalport)
		self.txtlocalport.bind("<KeyRelease>", self.callback_parse_vars)
		self.txtlocalport.insert(END, LOCAL_PORT)
		self.txtlocalport.grid(row = 2, column = 1,padx=5,pady=(0,5))

		self.lblremoteport = Label(self.framevar,text=" Remote Port:",justify=RIGHT)
		self.lblremoteport.grid(row = 2, column = 2,padx=5,pady=(0,5))
		self.txtremoteport = Entry(self.framevar,textvariable=svremoteport)
		self.txtremoteport.bind("<KeyRelease>", self.callback_parse_vars)
		self.txtremoteport.insert(END, REMOTE_PORT)
		self.txtremoteport.grid(row = 2, column = 3,padx=5,pady=(0,5))

		self.frame = Frame(self.master,bd=1, relief=SOLID)
		self.frame.grid(row = 2, column = 3)#, padx=(0,5),pady=0)

		self.lblxtravars = Label(self.frame,text="Additional Variables")
		f = font.Font(self.lblvars, self.lblvars.cget("font"))
		f.configure(underline=True)
		self.lblxtravars.configure(font=f)

		self.lblurl = Label(self.frame,text="URL:")
		self.txturl = Entry(self.frame,textvariable=svurl)
		self.txturl.bind("<KeyRelease>", self.callback_parse_vars)

		self.lblcommand = Label(self.frame,text="COMMAND:")
		self.txtcommand = Entry(self.frame,textvariable=svcommand)
		self.txtcommand.bind("<KeyRelease>", self.callback_parse_vars)


		self.lblfilepath = Label(self.frame,text="FILE_PATH:")
		self.txtfilepath = Entry(self.frame,textvariable=svfilepath)
		self.txtfilepath.bind("<KeyRelease>", self.callback_parse_vars)

		self.lblusername = Label(self.frame,text="USERNAME:")
		self.txtusername = Entry(self.frame,textvariable=svusername)
		self.txtusername.bind("<KeyRelease>", self.callback_parse_vars)

		self.lblpassword = Label(self.frame,text="PASSWORD:")
		self.txtpassword = Entry(self.frame,textvariable=svpassword)
		self.txtpassword.bind("<KeyRelease>", self.callback_parse_vars)

		######################### buttons ###############################
		self.framebtns = Frame(self.master, bd=1, relief=SOLID)
		self.framebtns.grid(row = 11, column = 0,columnspan=4,sticky = NSEW, padx=5,pady=5)

		self.btnHide = Button(self.framebtns, text="Hide", command=self.Hide)
		self.btnHide.grid(row = 0, column = 0,sticky=W,padx=5)

		self.btnAdd = Button(self.framebtns, text="Add", command=self.BtnAdd)
		self.btnAdd.grid(row = 0, column = 1, padx=(108,5))

		self.btnEdit = Button(self.framebtns, text="Edit", command=self.BtnEdit)
		self.btnEdit.grid(row = 0, column = 2, padx=5)

		self.btnRem = Button(self.framebtns, text="Remove", command=self.BtnRemove)
		self.btnRem.grid(row = 0, column = 3)

		global photo
		photo=PhotoImage(file="%s/applications-system.png" %PROGRAM_DIR)
		self.btnConfig = Button(self.framebtns,text = "Config", image=photo, command=self.BtnConfig)
		self.btnConfig.grid(row = 0, column = 4, padx=(5,108))

		self.btnCopy = Button(self.framebtns, text="Copy", command=self.BtnCopy)
		self.btnCopy.grid(row = 0 ,column = 5, sticky=E,padx=5)


		self.populate_liner_list()

	def Hide(self):
		self.master.withdraw()

	def BtnAdd(self):
		self.addapp.Show(self.refresh_lists)

	def BtnEdit(self):
		# self.editapp.LoadLiner()
		self.editapp.Show(self.refresh_lists)

	def BtnRemove(self):
		self.removeapp.RemoveGo(self.refresh_lists)

	def BtnConfig(self):
		self.cfgapp.Show()

	def BtnCopy(self):
		pyperclip.copy(str(svliner.get()))
		self.master.withdraw()

	def callback_cbostype(self, eventObject):
		self.populate_format_list()
		self.populate_function_list()

	def callback_cbformattype(self, eventObject):
		self.populate_liner_list()
		self.populate_function_list()

	def callback_cbfiltertype(self, eventObject):
		self.populate_liner_list()

	def callback_linerlist_onselect(self, eventObject):
		ostype = self.cbostype.get()
		formattype = self.cbformattype.get()
		try:
			selection = self.linerlist.get(self.linerlist.curselection())
		except:
			selection = ''
			self.lbldescription['text'] = ''

		if selection != '' and selection != 'Select OS':
			linerstr = selection
			svlinerselection.set(linerstr)

			targ,form,func,name = linerstr.split('/')

			db = DB.LinerDB(DB_PATH)
			liner_result = db.GetLiner(targ, form, func, name)


			info_description = liner_result.Description
			sinfo_vars = liner_result.Vars
			info_vars = sinfo_vars.split(',')
			info_liner = liner_result.Liner

			self.lbldescription['text'] = info_description
			self.txtliner.delete(0,END)
			self.callback_parse_vars()
			self.lblxtravars.grid_remove()
			self.frame.grid_remove()

			self.frame.grid(row = 2, column = 3)
			self.lblxtravars.grid(row=0,column=0,padx=10,pady=10)
			self.lblurl.grid_remove()
			self.txturl.grid_remove()
			self.lblcommand.grid_remove()
			self.txtcommand.grid_remove()
			self.lblfilepath.grid_remove()
			self.txtfilepath.grid_remove()
			self.lblusername.grid_remove()
			self.txtusername.grid_remove()
			self.lblpassword.grid_remove()
			self.txtpassword.grid_remove()

			r = 1
			for info_var in info_vars:
				if "URL" == info_var:
					self.lblurl.grid(row=r,column=0,padx=5)
					self.txturl.grid(row=r+1,column=0,padx=5,pady=(0,5))
					r = r + 2

				if "COMMAND" == info_var:
					self.lblcommand.grid(row=r,column=0,padx=5)
					self.txtcommand.grid(row=r+1,column=0,padx=5,pady=(0,5))
					r = r + 2

				if "FILE_PATH" == info_var:
					self.lblfilepath.grid(row=r,column=0,padx=5)
					self.txtfilepath.grid(row=r+1,column=0,padx=5,pady=(0,5))
					r = r + 2

				if "USERNAME" == info_var:
					self.lblusername.grid(row=r,column=0,padx=5)
					self.txtusername.grid(row=r+1,column=0,padx=5,pady=(0,5))
					r = r + 2

				if "PASSWORD" == info_var:
					self.lblpassword.grid(row=r,column=0,padx=5)
					self.txtpassword.grid(row=r+1,column=0,padx=5,pady=(0,5))
					r = r + 2

	def callback_parse_vars(self, eventObject=0):
		selection = svlinerselection.get()
		if selection != '':
			linerstr = selection

			targ,form,func,name = linerstr.split('/')
			db = DB.LinerDB(DB_PATH)
			liner_result = db.GetLiner(targ, form, func, name)

			sinfo_vars = liner_result.Vars
			vars = sinfo_vars.split(',')
			linerstr = liner_result.Liner

			self.txtliner.delete(0,END)
			for var in vars:
				if var == "LOCAL_IP":
					if svlocalip.get() != '':
						linerstr = linerstr.replace(var,svlocalip.get())
				if var == "LOCAL_PORT":
					if svlocalport.get() != '':
						linerstr = linerstr.replace(var,svlocalport.get())
				if var == "REMOTE_IP":
					if svremoteip.get() != '':
						linerstr = linerstr.replace(var,svremoteip.get())
				if var == "REMOTE_PORT":
					if svremoteport.get() != '':
						linerstr = linerstr.replace(var,svremoteport.get())
				if var == "URL":
					if svurl.get() != '':
						linerstr = linerstr.replace(var,svurl.get())
				if var == "COMMAND":
					if svcommand.get() != '':
						linerstr = linerstr.replace(var,svcommand.get())
				if var == "FILE_PATH":
					if svfilepath.get() != '':
						linerstr = linerstr.replace(var,svfilepath.get())
				if var == "USERNAME":
					if svusername.get() != '':
						linerstr = linerstr.replace(var,svusername.get())
				if var == "PASSWORD":
					if svpassword.get() != '':
						linerstr = linerstr.replace(var,svpassword.get())

			self.txtliner.insert(END,linerstr)

	def populate_os_list(self,selection=None):
		global DB_PATH

		db = DB.LinerDB(DB_PATH)
		os_list = db.GetAllOSTypes()

		self.cbostype['values'] = os_list
		if selection:
			if selection in os_list:
				self.cbostype.set(selection)
			else:
				self.cbostype.set('')
		else:
			self.cbostype.set('')

	def populate_function_list(self,selection=None):
		global DB_PATH

		ostype = self.cbostype.get()
		formattype = self.cbformattype.get()

		if formattype == 'all':
			formattype = None

		db = DB.LinerDB(DB_PATH)
		function_list = db.GetFunctionTypesFiltered(ostype, formattype)

		function_list.insert(0, "all")

		self.cbfiltertype['values'] = function_list
		if selection:
			if selection in function_list:
				self.cbfiltertype.set(selection)
			else:
				self.cbfiltertype.set('all')
		else:
			self.cbfiltertype.set('all')

	def populate_format_list(self,selection=None):
		global DB_PATH
		ostype = self.cbostype.get()
		functiontype = self.cbfiltertype.get()

		if functiontype == 'all':
			functiontype = None

		db = DB.LinerDB(DB_PATH)
		format_list = db.GetFormatTypesFiltered(ostype, functiontype)

		format_list.insert(0, "all")


		self.cbformattype['values'] = format_list
		self.cbformattype.set('')

		if selection:
			if selection in format_list:
				self.cbformattype.set(selection)
			else:
				self.cbformattype.set('all')
		else:
			self.cbformattype.set('all')

		self.populate_liner_list()


	def populate_liner_list(self):
		self.linerlist.delete(0,END)
		ostype = self.cbostype.get()
		formattype = self.cbformattype.get()
		functiontype = self.cbfiltertype.get()

		if formattype == 'all':
			formattype = None

		if functiontype == 'all':
			functiontype = None

		if ostype == '':
			liners = ["Select OS"]
		else:
			query = DB.Query()
			query.TargetOS = ostype
			query.Format = formattype
			query.Function = functiontype

			db = DB.LinerDB(DB_PATH)
			liner_list = db.QueryDB(query)
			liners = []
			for liner in liner_list:
				liners.append("%s/%s/%s/%s" %(liner.TargetOS,liner.Format,liner.Function,liner.Name))


		self.linerlist.insert(END, *liners)
		self.txtliner.delete(0,END)

	def refresh_lists(self):
		global OS_TYPES
		global FILTER_TYPES
		global FORMAT_TYPES

		ostype = self.cbostype.get()
		formattype = self.cbformattype.get()
		filtertype = self.cbfiltertype.get()

		self.populate_os_list(ostype)
		self.populate_format_list(formattype)
		self.populate_function_list(filtertype)
		self.populate_liner_list()

	# MainWin TODO:
		# update ip after config


class ConfigWin:
	def __init__(self, master):
		global IFACE
		global DB_PATH
		global LOCAL_IP

		with open('%s/config.json' %PROGRAM_DIR) as config_file:
			CONFIG_DATA = json.load(config_file)
			DB_PATH = CONFIG_DATA['dbpath']

			if DB_PATH == 'db.sqlite3': #default (fixes path at first run)
				DB_PATH ='%s/db.sqlite3' %PROGRAM_DIR
				CONFIG_DATA['dbpath']= DB_PATH
				with open('%s/config.json' %PROGRAM_DIR, 'w') as outfile:
					json.dump(CONFIG_DATA, outfile)

			try:
				IFACE = CONFIG_DATA['iface']
				ni.ifaddresses(IFACE)
				LOCAL_IP =  ni.ifaddresses(IFACE)[ni.AF_INET][0]['addr']
			except:
				LOCAL_IP = "127.0.0.1"
				svlocalip.set(LOCAL_IP)


		self.master = master

		self.master.wm_attributes('-type', 'dialog')
		self.master.wm_attributes("-topmost", 1)
		self.master.title("One-Z Settings")
		self.master.lift()

		self.cfgframe = Frame(self.master)
		self.cfgframe.grid(row=0,column=0,sticky=NSEW)

		self.lblIface = Label(self.cfgframe,text="Interface for IPs:")
		self.lblIface.grid(row=0,column=0,padx=5, pady=5)

		IFACES = os.listdir('/sys/class/net/')
		self.cbIface = ttk.Combobox(self.cfgframe,state='readonly',values=IFACES)
		self.cbIface.set(IFACE)
		self.cbIface.grid(row=0,column=1,padx=5, pady=5)


		self.lblDB = Label(self.cfgframe,text="SQLite DB Path:")
		self.lblDB.grid(row=1,column=0,padx=5, pady=5 )

		self.txtDBpath = Entry(self.cfgframe,textvariable=svDBpath)
		self.txtDBpath.grid(row=1,column=1,padx=5, pady=5, sticky=EW)
		self.txtDBpath.insert(END, DB_PATH)

		self.btnDone = Button(self.cfgframe, text="Done", command=self.ConfigDone)
		self.btnDone.grid(row = 2, column = 0,padx=5, pady=5, sticky=SW)

		self.btnQuit = Button(self.cfgframe, text="Quit", command=self.Quit)
		self.btnQuit.grid(row = 2, column = 1,padx=5, pady=5, sticky=SE)
		self.master.lift()

	def ConfigDone(self):
		global IFACE
		global LOCAL_IP
		global CONFIG_DATA
		global PROGRAM_DIR
		global DB_PATH

		with open('%s/config.json' %PROGRAM_DIR) as config_file:
			CONFIG_DATA = json.load(config_file)

		# get default iface for local ip
		try:
			IFACE = self.cbIface.get()
			ni.ifaddresses(IFACE)
			LOCAL_IP =  ni.ifaddresses(IFACE)[ni.AF_INET][0]['addr']
			svlocalip.set(LOCAL_IP)
		except:
			pass


		CONFIG_DATA['iface'] = IFACE

		DB_PATH = str(svDBpath.get())
		CONFIG_DATA['dbpath'] = DB_PATH


		# save config file
		with open('%s/config.json' %PROGRAM_DIR, 'w') as outfile:
			json.dump(CONFIG_DATA, outfile)

		self.master.withdraw()

	def Show(self):
		self.master.geometry("+{}+{}".format(self.master.master.winfo_x()+150, self.master.master.winfo_y()+200))
		self.master.deiconify()
		self.master.focus_set()
		self.master.lift()

	def Quit(self):
		exit()


class AddLinerWin:
	def __init__(self, master):
		self.master = master
		self.master.title("One-Z Add Liner")

		global DB_PATH

		TMP_OS_TYPES = []
		TMP_FORMAT_TYPES = []
		TMP_FUNCTION_TYPES = []
		VAR_TYPES = ["LOCAL_IP","LOCAL_PORT","REMOTE_IP","REMOTE_PORT","URL","COMMAND","FILE_PATH","USERNAME","PASSWORD"]

		db = DB.LinerDB(DB_PATH)
		TMP_OS_TYPES = db.GetAllOSTypes()
		TMP_FORMAT_TYPES = db.GetAllFormatTypes()
		TMP_FUNCTION_TYPES = db.GetAllFunctionTypes()

		# self.addLinerWin.wm_attributes('-type', 'splash')
		self.master.wm_attributes("-topmost", 1)

		self.cbostypes = ttk.Combobox(self.master,state='readonly',values=TMP_OS_TYPES,textvariable=svLinerTarget)
		self.cbostypes.grid(row=1,column=2,padx=5,pady=5,sticky=W)

		self.cbformattypes = ttk.Combobox(self.master,state='readonly',values=TMP_FORMAT_TYPES,textvariable=svLinerFormat)
		self.cbformattypes.grid(row=2,column=2,padx=5,pady=5,sticky=W)

		self.cbfiltertypes = ttk.Combobox(self.master,state='readonly',values=TMP_FUNCTION_TYPES,textvariable=svLinerFunc)
		self.cbfiltertypes.grid(row=3,column=2,padx=5,pady=5,sticky=W)

		self.cbvartypes = ttk.Combobox(self.master,state='readonly',values=VAR_TYPES)
		self.cbvartypes.grid(row=4,column=2,padx=5,pady=5,sticky=W)
		self.cbvartypes.bind("<<ComboboxSelected>>", self.addVarToEntryList)

		self.lblLinerName = Label(self.master,text="Liner Name:")
		self.lblLinerName.grid(row=0,column=0,padx=5,pady=5)
		self.txtLinerName = Entry(self.master,textvariable=svLinerName)
		self.txtLinerName.grid(row=0,column=1,padx=5,pady=5,sticky=W)
		self.txtLinerName.delete(0, END)

		self.lblLinerTarget = Label(self.master,text="Target OS:")
		self.lblLinerTarget.grid(row=1,column=0,padx=5,pady=5)
		self.txtLinerTarget = Entry(self.master,textvariable=svLinerTarget)
		self.txtLinerTarget.grid(row=1,column=1,padx=5,pady=5,sticky=W)
		self.txtLinerTarget.delete(0, END)

		self.lblLinerFormat = Label(self.master,text="Format:")
		self.lblLinerFormat.grid(row=2,column=0,padx=5,pady=5)
		self.txtLinerFormat = Entry(self.master,textvariable=svLinerFormat)
		self.txtLinerFormat.grid(row=2,column=1,padx=5,pady=5,sticky=W)
		self.txtLinerFormat.delete(0, END)

		self.lblLinerFunc = Label(self.master,text="Function:")
		self.lblLinerFunc.grid(row=3,column=0,padx=5,pady=5)
		self.txtLinerFunc = Entry(self.master,textvariable=svLinerFunc)
		self.txtLinerFunc.grid(row=3,column=1,padx=5,pady=5,sticky=W)
		self.txtLinerFunc.delete(0, END)

		self.lblLinerVars = Label(self.master,text="Variable List:")
		self.lblLinerVars.grid(row=4,column=0,padx=5,pady=5)
		self.txtLinerVars = Entry(self.master,textvariable=svLinerVars)
		self.txtLinerVars.grid(row=4,column=1,padx=5,pady=5,sticky=W)
		self.txtLinerVars.delete(0, END)

		self.lblLinerDesc = Label(self.master,text="Description:")
		self.lblLinerDesc.grid(row=5,column=0,padx=5,pady=5)
		self.txtLinerDesc = Entry(self.master,textvariable=svLinerDesc)
		self.txtLinerDesc.grid(row=5,column=1,padx=5,pady=5,columnspan=4,sticky=EW)
		self.txtLinerDesc.delete(0, END)

		self.lblNewLiner = Label(self.master,text="Liner:")
		self.lblNewLiner.grid(row=6,column=0,padx=5,pady=5)
		self.txtNewLiner = Entry(self.master,width=50,textvariable=svNewLiner)
		self.txtNewLiner.grid(row=6,column=1,padx=5,pady=5,columnspan=4,sticky=EW)
		self.txtNewLiner.delete(0, END)

		self.btnAdd = Button(self.master, text="Add", command=self.AddLinerGo)
		self.btnAdd.grid(row = 11, column = 2,padx=5,pady=5,sticky=E)

		self.btnCancel = Button(self.master, text="Cancel", command=self.Hide)
		self.btnCancel.grid(row = 11, column = 0,padx=5,pady=5,sticky=W)

	def Show(self,refreshfunc):
		self.refresh_lists = refreshfunc
		self.master.geometry("+{}+{}".format(self.master.master.winfo_x()+50, self.master.master.winfo_y()+50))
		self.master.deiconify()
		self.master.focus_set()
		self.master.lift()

	def Hide(self):
		self.master.withdraw()

	def AddLinerGo(self):
		global DB_PATH
		idnum = randint(10000000, 99999999)
		name = svLinerName.get()
		desc= svLinerDesc.get()
		target = svLinerTarget.get()
		form = svLinerFormat.get()
		function = svLinerFunc.get()
		liner = svNewLiner.get()
		var = svLinerVars.get()

		txtvars = var.split(',')
		goodVars = ["LOCAL_IP","LOCAL_PORT","REMOTE_IP","REMOTE_PORT","URL","COMMAND","FILE_PATH","USERNAME","PASSWORD"]
		varsOK = True
		for curvar in txtvars:
			if curvar not in goodVars:
				varsOK = False


		if name == '' or desc == '' or target == '' or format == '' or function == '' or liner == '':
			messagebox.showerror("One-Z Error", "All fields are required. (only Variables can be empty)",parent=self.master)
		elif varsOK == False and var !='':
			messagebox.showerror("One-Z Error", "Undefined Variable. must be (LOCAL_IP,LOCAL_PORT,REMOTE_IP,REMOTE_PORT,URL,COMMAND,FILE_PATH,USERNAME,PASSWORD)",parent=self.master)
		else:
			db = DB.LinerDB(DB_PATH)

			#check if exsists
			try:
				result = db.GetLiner(target,form,function,name)
			except:
				result = None
			if result:
				messagebox.showerror("One-Z Error", "%s/%s/%s already exsists in the database." %(target,form,name),parent=self.master)
				return

			query = DB.Query()
			query.KeyNum = idnum
			query.Description = desc
			query.Name = name
			query.Format = form
			query.Function = function
			query.TargetOS = target
			query.Liner = liner
			query.Vars = var

			db.AddLiner(query)

			self.Hide()
			self.refresh_lists()

	def addVarToEntryList(self,object):
		global svLinerVars
		cur_var = self.cbvartypes.get()
		if cur_var:
			tmp = "%s,%s" %(svLinerVars.get(),cur_var)
			tmp = tmp.lstrip(',').rstrip(',').strip()
			svLinerVars.set(tmp)



class EditLinerWin:
	def __init__(self, master):

		self.master = master
		self.master.title("One-Z Edit Liner")

		global DB_PATH
		TMP_OS_TYPES = []
		TMP_FORMAT_TYPES = []
		TMP_FUNCTION_TYPES = []
		VAR_TYPES = ["LOCAL_IP","LOCAL_PORT","REMOTE_IP","REMOTE_PORT","URL","COMMAND","FILE_PATH","USERNAME","PASSWORD"]

		db = DB.LinerDB(DB_PATH)
		TMP_OS_TYPES = db.GetAllOSTypes()
		TMP_FORMAT_TYPES = db.GetAllFormatTypes()
		TMP_FUNCTION_TYPES = db.GetAllFunctionTypes()

		self.editLinerWin = self.master
		# self.editLinerWin.wm_attributes('-type', 'splash')
		self.editLinerWin.wm_attributes("-topmost", 1)

		self.cbostypes = ttk.Combobox(self.editLinerWin,state='readonly',values=TMP_OS_TYPES,textvariable=svLinerTarget)
		self.cbostypes.grid(row=1,column=2,padx=5,pady=5,sticky=W)

		self.cbformattypes = ttk.Combobox(self.editLinerWin,state='readonly',values=TMP_FORMAT_TYPES,textvariable=svLinerFormat)
		self.cbformattypes.grid(row=2,column=2,padx=5,pady=5,sticky=W)

		self.cbfiltertypes = ttk.Combobox(self.editLinerWin,state='readonly',values=TMP_FUNCTION_TYPES,textvariable=svLinerFunc)
		self.cbfiltertypes.grid(row=3,column=2,padx=5,pady=5,sticky=W)

		self.cbvartypes = ttk.Combobox(self.editLinerWin,state='readonly',values=VAR_TYPES)
		self.cbvartypes.grid(row=4,column=2,padx=5,pady=5,sticky=W)
		self.cbvartypes.bind("<<ComboboxSelected>>", self.editVarToEntryList)


		self.lblLinerName = Label(self.editLinerWin,text="Liner Name:")
		self.lblLinerName.grid(row=0,column=0,padx=5,pady=5)
		self.txtLinerName = Entry(self.editLinerWin,textvariable=svLinerName)
		self.txtLinerName.grid(row=0,column=1,padx=5,pady=5,sticky=W)


		self.lblLinerTarget = Label(self.editLinerWin,text="Target OS:")
		self.lblLinerTarget.grid(row=1,column=0,padx=5,pady=5)
		self.txtLinerTarget = Entry(self.editLinerWin,textvariable=svLinerTarget)
		self.txtLinerTarget.grid(row=1,column=1,padx=5,pady=5,sticky=W)

		self.lblLinerFormat = Label(self.editLinerWin,text="Format:")
		self.lblLinerFormat.grid(row=2,column=0,padx=5,pady=5)
		self.txtLinerFormat = Entry(self.editLinerWin,textvariable=svLinerFormat)
		self.txtLinerFormat.grid(row=2,column=1,padx=5,pady=5,sticky=W)

		self.lblLinerFunc = Label(self.editLinerWin,text="Function:")
		self.lblLinerFunc.grid(row=3,column=0,padx=5,pady=5)
		self.txtLinerFunc = Entry(self.editLinerWin,textvariable=svLinerFunc)
		self.txtLinerFunc.grid(row=3,column=1,padx=5,pady=5,sticky=W)

		self.lblLinerVars = Label(self.editLinerWin,text="Variable List:")
		self.lblLinerVars.grid(row=4,column=0,padx=5,pady=5)
		self.txtLinerVars = Entry(self.editLinerWin,textvariable=svLinerVars)
		self.txtLinerVars.grid(row=4,column=1,padx=5,pady=5,sticky=W)

		self.lblLinerDesc = Label(self.editLinerWin,text="Description:")
		self.lblLinerDesc.grid(row=5,column=0,padx=5,pady=5)
		self.txtLinerDesc = Entry(self.editLinerWin,textvariable=svLinerDesc)
		self.txtLinerDesc.grid(row=5,column=1,padx=5,pady=5,columnspan=4,sticky=EW)

		self.lblNewLiner = Label(self.editLinerWin,text="Liner:")
		self.lblNewLiner.grid(row=6,column=0,padx=5,pady=5)
		self.txtNewLiner = Entry(self.editLinerWin,textvariable=svNewLiner)
		self.txtNewLiner.grid(row=6,column=1,padx=5,pady=5,columnspan=4,sticky=EW)

		self.btnSave = Button(self.editLinerWin, text="Save", command=self.EditLinerGo)
		self.btnSave.grid(row = 11, column = 2,padx=5,pady=5,sticky=E)

		self.btnCancel = Button(self.editLinerWin, text="Cancel", command=self.Hide)
		self.btnCancel.grid(row = 11, column = 0,padx=5,pady=5,sticky=W)

	def editVarToEntryList(self,object):
		cur_var = self.cbvartypes.get()
		if cur_var:
			tmp = "%s,%s" %(svLinerVars.get(),cur_var)
			tmp = tmp.lstrip(',').rstrip(',').strip()
			svLinerVars.set(tmp)

	def Show(self,refreshfunc):
		self.refresh_lists = refreshfunc
		self.master.geometry("+{}+{}".format(self.master.master.winfo_x()+50, self.master.master.winfo_y()+50))
		self.LoadLiner()

	def Hide(self):
		self.master.withdraw()

	def LoadLiner(self,event=0):
		selection = svlinerselection.get()
		if selection != '':

			linerstr = selection
			targ,form,function,name = linerstr.split('/')

			db = DB.LinerDB(DB_PATH)

			try:
				result = db.GetLiner(targ,form,function,name)
			except:
				result = None

			if not result:
				return

			self.txtLinerName.delete(0, END)
			self.txtLinerName.insert(END, result.Name)
			self.txtNewLiner.delete(0, END)
			self.txtNewLiner.insert(END, result.Liner)
			self.txtLinerDesc.delete(0, END)
			self.txtLinerDesc.insert(END, result.Description)
			self.txtLinerVars.delete(0, END)
			self.txtLinerVars.insert(END, result.Vars)
			self.txtLinerFunc.delete(0, END)
			self.txtLinerFunc.insert(END, result.Function)
			self.txtLinerFormat.delete(0, END)
			self.txtLinerFormat.insert(END, result.Format)
			self.txtLinerTarget.delete(0, END)
			self.txtLinerTarget.insert(END, result.TargetOS)

			self.master.deiconify()
			self.master.focus_set()
			self.master.lift()
		else:
			self.master.withdraw()
			messagebox.showerror("One-Z Error","Select a liner to edit.",parent=self.master.master)



	def EditLinerGo(self):
		global DB_PATH

		selection = svlinerselection.get()
		starg,sform,sfunction,sname = selection.split('/')

		idnum = randint(10000000, 99999999)
		name = svLinerName.get()
		desc= svLinerDesc.get()
		target = svLinerTarget.get()
		form = svLinerFormat.get()
		function = svLinerFunc.get()
		liner = svNewLiner.get()
		var = svLinerVars.get()

		txtvars = var.split(',')
		goodVars = ["LOCAL_IP","LOCAL_PORT","REMOTE_IP","REMOTE_PORT","URL","COMMAND","FILE_PATH","USERNAME","PASSWORD"]
		varsOK = True
		for curvar in txtvars:
			if curvar not in goodVars:
				varsOK = False


		if name == '' or desc == '' or target == '' or format == '' or function == '' or liner == '':
			messagebox.showerror("One-Z Error", "All fields are required. (only Variables can be empty)",parent=self.master)
		elif varsOK == False and var !='':
			messagebox.showerror("One-Z Error", "Undefined Variable. must be (LOCAL_IP,LOCAL_PORT,REMOTE_IP,REMOTE_PORT,URL,COMMAND,FILE_PATH,USERNAME,PASSWORD)",parent=self.master)
		else:
			db = DB.LinerDB(DB_PATH)
			db.RemoveLiner(starg,sform,sfunction,sname)

			query = DB.Query()
			query.KeyNum = idnum
			query.Description = desc
			query.Name = name
			query.Format = form
			query.Function = function
			query.TargetOS = target
			query.Liner = liner
			query.Vars = var

			db.AddLiner(query)
			self.refresh_lists()
			self.Hide()


class LinerRemove:
	def __init__(self, master):
		self.master = master

	def RemoveGo(self,refreshfunc):
		global DB_PATH

		selection = svlinerselection.get()
		if selection != '':
			linerstr = selection #"%s/%s/%s" %(ostype,formattype,selection)
			choice = messagebox.askokcancel("One-Z Are you sure","Are you sure you want to remove %s" %linerstr,parent=self.master)
			if choice == True:
				targ,form,func,name = linerstr.split('/')

				db = DB.LinerDB(DB_PATH)
				db.RemoveLiner(targ,form,func,name)

				refreshfunc()

		else:
			messagebox.showerror("One-Z Error","Select a liner to remove.",parent=self.master)

################################################################################
def main():
	app = TrayIcon(root)
	root.mainloop()

def testfunc(e):
	print("blah")


root = Tk()
# root.bind("<FocusOut>",testfunc)
svlocalip = StringVar()
svremoteip = StringVar()
svlocalport = StringVar()
svremoteport = StringVar()
svurl = StringVar()
svcommand = StringVar()
svfilepath = StringVar()
svusername = StringVar()
svpassword = StringVar()
svlinerselection = StringVar()
svliner = StringVar()
svDBpath = StringVar()
svLinerName = StringVar()
svLinerTarget =StringVar()
svLinerFormat = StringVar()
svLinerFunc = StringVar()
svNewLiner = StringVar()
svLinerDesc = StringVar()
svLinerVars = StringVar()

if __name__ == '__main__':
	main()
