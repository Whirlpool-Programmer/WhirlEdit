import os
import subprocess
import shutil
import tkinter
import zipfile
import tempfile
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.font as tkfont
from wday import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkcode import CodeEditor

openedfolders = []
nothing = [0,0]

def fullscreen(*args):
	if nothing[1] == 0:
		thisroot.wm_attributes("-fullscreen",1)
		nothing[1] = 1
	else:
		thisroot.wm_attributes("-fullscreen",0)
		nothing[1] = 0

def set_syntax(lang):
	note[curnote2()].config(language=lang)

def togglesidepane():
	global nothing
	if nothing[0] == 0:
		splitter.forget(leftFrame)
		nothing[0] = 1
	else:
		splitter.add(leftFrame, before = root,width=200)
		nothing[0] = 0

def update(*args):
	fdir = "/".join(openedfiles[curnote2()].split("/")[:-1])
	if fdir in openedfolders:
		pass
	else:
		framed.add(fdir)
		openedfolders.append(fdir)

class PathView(object):
	def add(self,path):
		abspath = os.path.abspath(path)
		self.insert_node('', abspath, abspath)
		self.tree.bind('<<TreeviewOpen>>', self.open_node)
	def __init__(self, master, paths):
		frame = tk.Frame(master)
		self.tree = ttk.Treeview(frame)
		self.nodes = dict()
		ysb = ttk.Scrollbar(frame, orient='vertical', command=self.tree.yview)
		xsb = ttk.Scrollbar(frame, orient='horizontal', command=self.tree.xview)
		xsb.pack(side=BOTTOM,fill=X)
		self.tree.configure(xscroll=xsb.set)
		self.tree.configure(yscroll=ysb.set)
		self.tree.heading('#0', text='FOLDERS', anchor='w')
		ysb.pack(side=RIGHT,fill=Y)
		self.tree.pack(fill=BOTH,expand=1)
		frame.pack(fill=BOTH,expand=1)
		for path in paths:
			abspath = os.path.abspath(path)
			self.insert_node('', abspath, abspath)
			self.tree.bind('<<TreeviewOpen>>', self.open_node)
	def insert_node(self, parent, text, abspath):
		node = self.tree.insert(parent, 'end', text=text, open=False)
		if os.path.isdir(abspath):
			self.nodes[node] = abspath
			self.tree.insert(node, 'end')
	def open_node(self, event):
		node = self.tree.focus()
		abspath = self.nodes.pop(node, None)
		if abspath:
			self.tree.delete(self.tree.get_children(node))
			for p in os.listdir(abspath):
				self.insert_node(node, p, os.path.join(abspath, p))

highlight = {
			"Ada"         : [".adb",".ads"],
			"Bash"        : [],#new
			"Batch"       : [".cmd",".bat"],#new
			"BrainFuck"   : [".b",".bf"],
			"C"           : [".c",".h"],
			"CMake"       : [],#new
			"CoffeeScript": [],#new
			"CSS"         : [".css"],
			"C#"          : [".cs",".csx"],
			"C++"         : [".cc",".cpp",".cxx",".c++",".hh",".hpp",".hxx",".h++"],
			"Dart"        : [".dart"],
			"Delphi"      : [".dpr"],
			"Dockerfile"  : [],#new
			"Fortran"     : [".f"],#new
			"Go"          : [".go"],
			"Groovy"      : [".groovy",".gvy",".gradle",".jenkinsfile"],#new
			"Haskell"     : [".hs",".lhs"],
			"HTML"        : [".htm",".html"],
			"Java"        : [".java",".jar",".class"],
			"JavaScript"  : [".js",".cjs",".mjs"],
			"JSON"        : [".json"],#new
			"Kotlin"      : [".kt",".kts",".ktm"],
			"Lisp"        : [".lsp"],
			"Lua"         : [".lua"],
			"MATLAB"      : [".m",".p",".mex",".mat",".fig",".mlx",".mlapp",".mltbx"],
			"MakeFile"    : [".make",".makefile"],#new
			"NASM"        : [".asm"],#new
			"Objective-C" : [".mm"],
			"Perl"        : [".plx",".pl",".pm",".xs",".t",".pod"],
			"PHP"         : [".php",".phar",".phtml",".pht",".phps"],
			"Powershell"  : [".ps1"],#new
			"Python"      : [".py",".pyi",".pyc",".pyd",".pyo",".pyw",".pyz"],
			"R"           : [".r",".rdata",".rds",".rda"],
			"Ruby"        : [".rb"],
			"Swift"       : [".swift"],
			"SQL"         : [".sql"],
			"Tcl"         : [".tcl",".tbc"],
			"TypeScript"  : [".ts",".tsx"],
			"Vim"         : [".vim"],#new
			"YAML"        : [".yaml",".yml"],#new
			}

filepath = ""

def identify(extension):
	for y in highlight.keys():
		for z in highlight[y]:
			if extension == z:
				return y

try:
	configs = open("runner.whirldata","r+")
except FileNotFoundError:
	configs = open("runner.whirldata", "x")

datafile = open("runner.whirldata").read()

if datafile.isspace():
	isConf = False
else:
	isConf = True

def runnerConf(thisType):
	print(thisType)
	cmds = read(datafile)
	command = cmds[thisType][1]
	command = command.replace("$file",'"'+filepath+'"')
	base = filepath.split("/")[-1]
	base = base[:base.find(".")]
	command = command.replace("$base",base.replace(" ","_"))
	command = command.replace("$dir",'"'+"/".join(filepath.split("/")[:-1])+'"')
	subprocess.call("start cmd /k {}".format(command), shell = True)

def getConfs():
	confs = []
	cmds = read(datafile)
	for i in cmds.keys():
		confs.append(i)
	return confs

colors = []
extension = {}

def curnote2(*args):
	variable = notebook.select()
	if notebook.select().replace('.!panedwindow.!frame2.!notebook.!frame','') == "":
		variable = 0
	else:
		variable = int(notebook.select().replace('.!panedwindow.!frame2.!notebook.!frame',''))
		if variable == 0:
			pass
		else:
			variable = int(variable) -1
	return variable

class AutocompleteEntry(ttk.Entry):
	"""
	Subclass of tkinter.Entry that features autocompletion.
	To enable autocompletion use set_completion_list(list) to define 
	a list of possible strings to hit.
	To cycle through hits use down and up arrow keys.
	"""

	def set_completion_list(self, completion_list):
		self._completion_list = completion_list
		self._hits = []
		self._hit_index = 0
		self.position = 0
		self.bind('<KeyRelease>', self.handle_keyrelease)               

	def autocomplete(self, delta=0):
		"""autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
		if delta: # need to delete selection otherwise we would fix the current position
			self.delete(self.position, tkinter.END)
		else: # set position to end so selection starts where textentry ended
			self.position = len(self.get())
		# collect hits
		_hits = []
		for element in self._completion_list:
			if element.startswith(self.get().lower()):
				_hits.append(element)
		# if we have a new hit list, keep this in mind
		if _hits != self._hits:
			self._hit_index = 0
			self._hits=_hits
		# only allow cycling if we are in a known hit list
		if _hits == self._hits and self._hits:
			self._hit_index = (self._hit_index + delta) % len(self._hits)
		# now finally perform the auto completion
		if self._hits:
			self.delete(0,tkinter.END)
			self.insert(0,self._hits[self._hit_index])
			self.select_range(self.position,tkinter.END)
						
	def handle_keyrelease(self, event):
		"""event handler for the keyrelease event on this widget"""
		if event.keysym == "BackSpace":
			self.delete(self.index(tkinter.INSERT), tkinter.END) 
			self.position = self.index(tkinter.END)
		if event.keysym == "Left":
			if self.position < self.index(tkinter.END): # delete the selection
				self.delete(self.position, tkinter.END)
			else:
				self.position = self.position-1 # delete one character
				self.delete(self.position, tkinter.END)
		if event.keysym == "Right":
			self.position = self.index(tkinter.END) # go to end (no selection)
		if event.keysym == "Down":
			self.autocomplete(1) # cycle to next hit
		if event.keysym == "Up":
			self.autocomplete(-1) # cycle to previous hit
		# perform normal autocomplete if event is a single key or an umlaut
		if len(event.keysym) == 1:# or event.keysym in tkinter_umlauts:
			self.autocomplete()

class CustomText(Text):
	def __init__(self, *args, **kwargs):
		"""A text widget that report on internal widget commands"""
		Text.__init__(self, *args, **kwargs)

		# create a proxy for the underlying widget
		self._orig = self._w + "_orig"
		self.tk.call("rename", self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)

	def _proxy(self, command, *args):
		cmd = (self._orig, command) + args
		result = self.tk.call(cmd)
		if command in ("insert", "delete", "replace"):
			self.event_generate("<<TextModified>>")
		return result

def newrunner():
	global conf
	def done():
		print(entry.get())
		thisconf = ""
		configs.writelines(datafile+'\n{}::["{}"::"{}"]'.format(name.get(),extension[curnote()],entry.get()))
		print(thisconf)
		conf.quit()
	def switchFunction():
		if gui.get():
			switch.config(text='Console')
		#else:
			#switch.config(text='No Console')
	def helpwindow():
		a = tk.Toplevel(conf)
		a.wm_attributes("-topmost",1)
		a.resizable(False,False)
		a.iconbitmap(r"favicon.v3.ico")
		a.title("Help")
		helpvartxt = """
Keywords:                               
  $file                                 
  	the file path.                      
  $base                                 
  	the base name of the file.          
  $dir                                  
    the folder where file is located.   
		"""
		b = Label(a,text = helpvartxt,font="Consolas")
		b.pack(side = LEFT)
		a.mainloop()
	conf = tk.Toplevel(root)
	conf.wm_attributes("-topmost",1)
	conf.iconbitmap(r"favicon.v3.ico")
	conf.resizable(False, False)
	conf.title("Configure runner for {} files".format(extension[curnote()]))
	conf.geometry("400x200")
	gui = BooleanVar()
	label = Label(conf,text = "Runner Name", font = "consolas")
	name = ttk.Entry(conf,width = 25, font = "consolas")
	name.place(x = 150, y = 10)
	label.place(x=10,y=16)
	label = Label(conf,text = "Command", font = "consolas")
	label.place(x=10,y=55)
	entry = AutocompleteEntry(conf,width = 25, font = "consolas")
	entry.set_completion_list((u'$file', u'$base', u'$dir', u'/k'))
	entry.place(x=150, y=50)
	entry.insert(0, 'compiler -o $base $file')
	helptxt = Label(conf,text = "Do you need some", font = "consolas")
	helptxt.place(x=60,y=100)
	helpbtn = ttk.Button(conf,text = "Help",command = lambda:helpwindow())
	helpbtn.place(x=220,y=100)
	submit = ttk.Button(conf,text = "Confirm & Create Runner", command = lambda:done())
	submit.place(x=125,y=150)
	conf.mainloop()

def runconf(*args):
	evaled = read(datafile)
	for i in evaled.keys():
		for x in evaled[i][0]:
			if x == extension[curnote2()]:
				thisext = i
	runnerConf(thisext)

thisroot = tk.Tk()
thisroot.iconbitmap(r"favicon.v3.ico")
thisroot.title('WhirlEdit Azure')
windowWidth = 800
windowHeight = 530
screenWidth  = thisroot.winfo_screenwidth()
screenHeight = thisroot.winfo_screenheight()
xCordinate = int((screenWidth/2) - (windowWidth/2))
yCordinate = int((screenHeight/2) - (windowHeight/2))
thisroot.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, xCordinate, yCordinate))
style = ttk.Style(thisroot)

splitter = tk.PanedWindow(thisroot, handlesize=2, orient=tk.HORIZONTAL)
splitter.pack(fill='both', expand=True)

leftFrame = tk.Frame(splitter, bg='#333333')
root = tk.Frame(splitter)
framed = PathView(leftFrame, paths=[])
splitter.add(leftFrame, width=200)
splitter.add(root)
try:
	configdata = read(open('./configure.whirldata').read())
	themefolder = configdata['Themefolder'][0]
	listdir = os.listdir(configdata['Themefolder'][0])
	themeslist = []
	for i in listdir:
		if i.lower().endswith('.whtheme'):
			themeslist.append(i)
	default_theme = configdata['DefaultTheme'][0]
	zipfile.ZipFile(themefolder+'/'+default_theme,'r').extractall(tempfile.gettempdir()+"/whTheme/")
	themefile = tempfile.gettempdir()+"/whTheme/"+read(open(tempfile.gettempdir()+"/whTheme/__init__.whirldata").read())['main'][0]
	themebase = read(open(tempfile.gettempdir()+"/whTheme/__init__.whirldata").read())['name'][0]
	thisroot.tk.call('source', themefile)
	style.theme_use(themebase)
	default_highlight = configdata['DefaultScheme'][0]
except:
	default_highlight = 'azure'

note        = {}
openedfiles = {}
canvas      = {}
scrolly     = {}
scrollx     = {}
var         = 0

def opencmd(*args):
	try:
		if filepath == "":
			cwd = os.getcwd()
		else:
			cwd = "/".join(filepath.split("/")[:-1])
		drive = cwd[:2]
		subprocess.call('start cmd /k cd /d "{}"'.format(cwd), shell=True)
	except:
		subprocess.call('start cmd /k "{}"'.format(openedfiles[curnote2()]), shell=True)

def runfile(*args):
	try:
		cwd = "/".join(filepath.split("/")[:-1])
		drive = cwd[:3]
		subprocess.call('start cmd /k "{}"'.format(openedfiles[curnote2()]), shell=True)
	except:
		subprocess.call('start cmd /k "{}"'.format(openedfiles[curnote2()]), shell=True)

def getpos(*args):
	global pos
	global line
	pos = note[int(curnote())].index("end")
	pos = pos[:-2]
	pos = int(pos)
	pos = pos -1
	print(pos)
	line.set(pos)
def curnote():
	variable = notebook.select()
	if notebook.select().replace('.!panedwindow.!frame2.!notebook.!frame','') == "":
		variable = 0
	else:
		variable = int(notebook.select().replace('.!panedwindow.!frame2.!notebook.!frame',''))
		if variable == 0:
			pass
		else:
			variable = int(variable) -1
	return variable

def deltab(*args):
	try:
		notebook.forget(notebook.select())
	except:
		thisroot.quit()

def saveAsFile(*args):
	global notebook
	global extension
	global filepath
	filepath = asksaveasfilename(defaultextension="",filetypes=[ ("All Files", "*.*"),("Text Files", "*.txt"),("Ada",[".adb",".ads"]),("BrainFuck",[".b",".bf"]),("C",[".c",".h"]),("CSS",[".css"]),("C#",[".cs",".csx"]),("C++",[".cc",".cpp",".cxx",".c++",".hh",".hpp",".hxx",".h++"]),("Dart",[".dart"]),("Delphi",[".dpr"]),("Go",[".go"]),("Haskell",[".hs",".lhs"]),("HTML",[".htm",".html"]),("Java",[".java",".jar",".class"]),("JavaScript",[".js",".cjs",".mjs"]),("Kotlin",[".kt",".kts",".ktm"]),("Lisp",[".lsp"]),("Lua",[".lua"]),("MATLAB",[".m",".p",".mex",".mat",".fig",".mlx",".mlapp",".mltbx",".mlappinstall",".mlpkginstall"]),("Objective-c",[".mm"]),("Perl",[".plx",".pl",".pm",".xs",".t",".pod"]),("php",[".php",".phar",".phtml",".pht",".phps"]),("Python",[".py",".pyi",".pyc",".pyd",".pyo",".pyw",".pyz"]),("R",[".r",".rdata",".rds",".rda"]),("Ruby",[".rb"]),("Swift",[".swift"]),("SQL",[".sql"]),("Tcl",[".tcl",".tbc"]),("TypeScript",[".ts",".tsx"])])
	if not filepath:
		return
	with open(filepath, "w") as output_file:
		extension[curnote()] = "."+filepath.split(".")[-1]
		variable = int(curnote2())
		text = note[variable].get(1.0, tk.END)
		output_file.write(text) 
	notebook.tab(frames[int(curnote2())], text = filepath.split("/")[-1])
	note[curnote2()].config(language=identify(filepath.split("/")[-1]))
	note[curnote2()].update()
	root.update()

def saveFile(*args):
	global notebook
	global extension
	variable = int(curnote2())

	if openedfiles[variable] == "":
		saveAsFile()
	else:
		with open(openedfiles[variable], "w") as output_file:
			extension[curnote()] = "."+openedfiles[variable].split(".")[-1]
			text = note[variable].get(1.0, tk.END)
			output_file.write(text)
			notebook.tab(frames[variable], text = openedfiles[curnote2()].split("/")[-1])

def openFile(*self): 
	#print("a",notebook.select())
	global extension
	global filepath
	if notebook.select() == "":
		newTab()

	variable = curnote2()
	filepath = askopenfilename(defaultextension="*.*", filetypes=[("All Files","*.*"), ("Text","*.txt"),("Ada",[".adb",".ads"]),("BrainFuck",[".b",".bf"]),("C",[".c",".h"]),("CSS",[".css"]),("C#",[".cs",".csx"]),("C++",[".cc",".cpp",".cxx",".c++",".hh",".hpp",".hxx",".h++"]),("Dart",[".dart"]),("Delphi",[".dpr"]),("Go",[".go"]),("Haskell",[".hs",".lhs"]),("HTML",[".htm",".html"]),("Java",[".java",".jar",".class"]),("JavaScript",[".js",".cjs",".mjs"]),("Kotlin",[".kt",".kts",".ktm"]),("Lisp",[".lsp"]),("Lua",[".lua"]),("MATLAB",[".m",".p",".mex",".mat",".fig",".mlx",".mlapp",".mltbx",".mlappinstall",".mlpkginstall"]),("Objective-c",[".mm"]),("Perl",[".plx",".pl",".pm",".xs",".t",".pod"]),("php",[".php",".phar",".phtml",".pht",".phps"]),("Python",[".py",".pyi",".pyc",".pyd",".pyo",".pyw",".pyz"]),("R",[".r",".rdata",".rds",".rda"]),("Ruby",[".rb"]),("Swift",[".swift"]),("SQL",[".sql"]),("Tcl",[".tcl",".tbc"]),("TypeScript",[".ts",".tsx"])]) 
	if filepath == "": 
		filepath = None
	else: 
		extension[curnote()] = "."+filepath.split(".")[-1]
		note[variable].delete(1.0,END) 
		file = open(filepath,"r") 
		note[curnote2()]["language"] = identify(filepath.split("/")[-1])
		note[variable].insert(1.0,file.read()) 
		openedfiles[variable] = filepath
		file.close() 
		notebook.tab(frames[variable], text = filepath.split("/")[-1])
		note[curnote2()].config(language=identify("."+filepath.split(".")[-1]))


def select_all(event):
	note[curnote2()].tag_add(SEL, "1.0", END)
	note[curnote2()].mark_set(INSERT, "1.0")
	note[curnote2()].see(INSERT)

frames = {}

def newTab(*args):
	global var
	global notebook
	frames[var] = ttk.Frame(notebook)
	note[var] = CodeEditor(frames[var],width=40, height=100, language="python",autofocus=True, insertofftime=0, padx=0, pady=0, font = "Consolas", highlighter = default_highlight)
	note[var].pack(fill="both", expand=True)
	font = tkfont.Font(font=note[var]['font'])
	note[var].config(tabs=font.measure('    '))
	openedfiles[var] = ""
	notebook.add(frames[var], text='Untitled')
	extension[curnote()] = ".*"
	note[var].bind("Control-a",select_all)
	var = var + 1

Menubar = Menu(root, activebackground ="#0084FF", activeforeground = "#FFFFFF",bg = "#FFFFFF", fg = "#0084FF" ,font = "consolas")

Filemenu = Menu(root, tearoff = 0)
Filemenu.add_command(label="New",command=newTab)
Filemenu.add_separator()
Filemenu.add_command(label="Open", command=openFile)
Filemenu.add_command(label="Save", command=saveFile)
Filemenu.add_command(label="Save As", command=saveAsFile)
Filemenu.add_separator()
Filemenu.add_command(label="Close", command=deltab)
Filemenu.add_separator()
Filemenu.add_command(label="Exit", command=thisroot.destroy)
Menubar.add_cascade(label="File", menu=Filemenu)

viewMenu = Menu(root,tearoff=0)
viewMenu.add_command(label = "Toggle Side Pane", command = lambda:togglesidepane())
Menubar.add_cascade(label = "View", menu = viewMenu)

toolsMenu = Menu(root,tearoff=0)
confmenu = Menu(root,tearoff=0)
runmenu = Menu(root,tearoff = 0)
runmenu.add_command(label = "Open file from cmd", command = lambda:runfile())
runmenu.add_separator()
runner_command = StringVar()
if isConf:
	for i in getConfs():
		runmenu.add("command",label = i, command = lambda i=i: runnerConf(i))
	runmenu.add_separator()
runmenu.add_command(label= "New Runner",command = lambda:newrunner())
toolsMenu.add_cascade(label = "Runner", menu = runmenu)
toolsMenu.add_command(label = "Open cmd here", command = lambda:opencmd())
Menubar.add_cascade(label="Tools",menu = toolsMenu)

syntaxMenu = Menu(root,tearoff=0)
setSyntaxMenu = Menu(root,tearoff=0)
for i in highlight.keys():
	setSyntaxMenu.add_command(label = i,command = lambda lang=i: set_syntax(lang))
syntaxMenu.add_cascade(label = "Syntax", menu = setSyntaxMenu)
Menubar.add_cascade(label = "Looks",menu = syntaxMenu)

#Helpmenu = Menu(root, tearoff = 0)
#Helpmenu.add_command(label = "Website", command=lambda:webbrowser.open("http://www.github.com/Whirlpool-Programmer/WhirlEdit/"))
#Helpmenu.add_separator()
#Helpmenu.add_command(label = "Changelog", command=None)
#Helpmenu.add_command(label = "About",command = None)
#Menubar.add_cascade(label = "Help", menu=Helpmenu)

root.grid_rowconfigure(0, weight=1) 
root.grid_columnconfigure(0, weight=1) 

line = StringVar()

notebook = ttk.Notebook(root)
notebook.grid(sticky = N + E + S + W)
newTab()

extension[curnote()] = ".*"
notebook.bind("<Double-Button>", newTab)
thisroot.bind("<Control-s>", saveFile)
thisroot.bind("<Control-n>", newTab)
thisroot.bind("<Control-w>", deltab)
thisroot.bind("<Control-o>", openFile)
thisroot.bind("<Control-F5>",runfile)
thisroot.bind("<F5>",runconf)
thisroot.bind("<Control-Shift-T>", opencmd)
thisroot.bind_all("<Key>",update)
thisroot.bind("<F11>",fullscreen)
thisroot.config(menu = Menubar)
thisroot.mainloop()
configs.close()
try:
	shutil.rmtree(tempfile.gettempdir()+'/whTheme')
except:
	pass	
