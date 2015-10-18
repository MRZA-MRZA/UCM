#!/usr/bin/env python3

import sys, os
import configparser
import shutil
from gi.repository import Gtk, GObject

class Cache:
	def __init__(self, path):
		try:
			CacheFile = open(path + "/cache.ini", "r")
		except:
			self.CacheItems = None
			return
		try:
			parser = configparser.RawConfigParser()
			parser.readfp(CacheFile)
			self.CacheItems = parser.items("Cache")
			CacheFile.close()	
		except:
			self.CacheItems = None
	
	def GetItems(self):
		return self.CacheItems
	
	def GetFileName(self, cfilename):
		for item in self.CacheItems:
			if item[0].swapcase()+".uxx" == cfilename:
				return item[1]
		return None

class CacheView(Gtk.TreeView):
	def __init__(self):
		Gtk.TreeView.__init__(self)
		self.CacheListModel = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
		self.set_model(self.CacheListModel)

		CacheColumn0 = Gtk.TreeViewColumn("Cache filename", Gtk.CellRendererText(), text = 0)
		CacheColumn0.set_sort_column_id(0)
		CacheColumn0.set_resizable(True)
		self.append_column(CacheColumn0)

		CacheColumn1 = Gtk.TreeViewColumn("Filename", Gtk.CellRendererText(), text = 1)
		CacheColumn1.set_sort_column_id(1)
		CacheColumn1.set_resizable(True)
		self.append_column(CacheColumn1)
		self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

	def add_row(self, string1, string2):
		self.CacheListModel.append((string1, string2))

	def clear(self):
		self.CacheListModel.clear()

	def get_cselected(self):
		retval = []
		for im in self.get_selection().get_selected_rows()[1]:
			retval.append(self.CacheListModel.get_value(self.CacheListModel.get_iter(im), 0))
		return retval


class UCM:
	"""Unreal Cache Manager"""
	ver = "0.4"
	def __init__(self):
		#windows
		self.MainWin = Gtk.Window()
		self.OpenDialog = Gtk.FileChooserDialog("Choose Cache Directory", parent=None, action=Gtk.FileChooserAction.SELECT_FOLDER, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		#menus
		self.MainMenu = Gtk.MenuBar()
		
		self.FileMenuM = Gtk.Menu()
		self.FileMenu = Gtk.MenuItem("File")
		self.OpenMenu = Gtk.MenuItem("Open cache")
		self.ExitMenu = Gtk.MenuItem("Exit")

		self.HelpMenuM = Gtk.Menu()
		self.HelpMenu = Gtk.MenuItem("Help")
		self.HowtoMenu = Gtk.MenuItem("How to use")
		self.AboutMenu = Gtk.MenuItem("About")
		
		#buttons
		self.SaveBtn = Gtk.Button("Save")

		#labels
		self.CacheDirLabel = Gtk.Label("Directory: ")
		self.StatusLbl = Gtk.Label("Status: ")
		self.StatusTxt = Gtk.Label("Ready")

		#entries
		self.CacheDirEntry = Gtk.Entry()
		self.CacheDirEntry.set_text("")
		self.CacheDirEntry.set_editable(False)


		#lists
		self.CacheList = CacheView()
		
		self.DirList = Gtk.FileChooserWidget(Gtk.FileChooserAction.SELECT_FOLDER) #Actually, it doesn't work as SELECT_FOLDER

		#boxes
		self.VBoxMain = Gtk.VBox()
		self.HBoxWork = Gtk.HPaned() #work area
		self.HBoxStatus = Gtk.HBox() #status

		self.VBoxCache = Gtk.VBox()
		self.VBoxDirList = Gtk.VBox()
		
		self.HBoxCacheDir = Gtk.HBox()
		self.CacheSW = Gtk.ScrolledWindow()
		self.CacheSW.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

		#packaging
		self.MainWin.add(self.VBoxMain)
		
		self.VBoxMain.pack_start(self.MainMenu, False, True, 0)
		self.VBoxMain.pack_start(self.HBoxWork, True, True, 0)
		self.VBoxMain.pack_end(self.HBoxStatus, False, True, 0)

		#Bottom
		self.HBoxStatus.pack_start(self.StatusLbl, False, True, 0)
		self.HBoxStatus.pack_start(self.StatusTxt, False, True, 0)
		
		#MainMenu:
		self.MainMenu.append(self.FileMenu)
		self.FileMenu.set_submenu(self.FileMenuM)
		self.FileMenuM.append(self.OpenMenu)
		self.FileMenuM.append(self.ExitMenu)

		self.MainMenu.append(self.HelpMenu)
		self.HelpMenu.set_submenu(self.HelpMenuM)
		self.HelpMenuM.append(self.HowtoMenu)
		self.HelpMenuM.append(self.AboutMenu)

		#Left
		self.HBoxWork.add1(self.VBoxCache)
		self.HBoxWork.add2(self.VBoxDirList)

		self.VBoxCache.pack_start(self.HBoxCacheDir, False, True, 0)
		self.HBoxCacheDir.pack_start(self.CacheDirLabel, False, True, 0)
		self.HBoxCacheDir.pack_start(self.CacheDirEntry, True, True, 0)

		self.VBoxCache.pack_start(self.CacheSW, True, True, 0)
		self.CacheSW.add(self.CacheList)

		#Right
		self.VBoxDirList.pack_start(self.DirList, True, True, 0)
		self.VBoxDirList.pack_end(self.SaveBtn, False, True, 0)

		#signals
		self.MainWin.connect("destroy", Gtk.main_quit)
		self.ExitMenu.connect("activate", Gtk.main_quit)
		self.OpenMenu.connect("activate", self.RunOpenDialog)
		self.AboutMenu.connect("activate", self.RunAboutDialog)
		self.HowtoMenu.connect("activate", self.RunHowtoDialog)
		self.SaveBtn.connect("clicked", self.Export)

		#other
		self.MainWin.set_title("Unreal Cache Manager")
		self.MainWin.set_icon_from_file("UCM.png")

	def RunAboutDialog(self, widget):
		logo = Gtk.Image()
		logo.set_from_file("UCM.png")
		ad = Gtk.AboutDialog()
		ad.set_name("About UCM...")
		ad.set_program_name("Unreal Cache Manager")
		ad.set_version(self.ver)
		ad.set_copyright("This program is Public Domain")
		ad.set_authors(["Marzanna (ponymarzanna@gmail.com)"])
		ad.set_logo(logo.get_pixbuf())
		ad.set_website("http://necrovision.net")
		ad.run()
		ad.hide()

	def RunHowtoDialog(self, widget):
		tvSW = Gtk.ScrolledWindow()
		tvSW.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		tb = Gtk.TextBuffer()
		tb.set_text("""Unreal Cache Manager manual

To start using program Click File -> Open cache, select cache directory. Note: it must contain cache.ini file to work properly.
If cache exists and cache.ini is valid, you will see cache contents on the left side.
You can sort it by clicking column header. Also you can use search by starting type a word.
When you find packages to export, select them, select destination directory on the left and click Save!
If nothing happened, look at the status message at the bottom.""")
		tv = Gtk.TextView()
		tv.set_buffer(tb)
		tv.set_editable(False)
		tvSW.add(tv)
		hd = Gtk.Dialog("Help", self.MainWin, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
		tvSW.show()
		tv.show()
		hd.vbox.pack_start(tvSW, True, True, 0)
		hd.run()
		hd.destroy()

	def RunOpenDialog(self, widget):
		filename = self.CacheDirEntry.get_text()
		self.OpenDialog.set_filename(filename)
		OpenResponse = self.OpenDialog.run()

		if OpenResponse == Gtk.ResponseType.OK:
			self.CacheDirEntry.set_text(self.OpenDialog.get_filename())
			self.Listing(None)
		elif OpenResponse == Gtk.ResponseType.CANCEL:
			pass
		self.OpenDialog.hide()

	def Listing(self, widget):
		self.CCache = Cache(self.CacheDirEntry.get_text())
		ItemsList = self.CCache.GetItems()
		if ItemsList == None:
			self.SetStatus("Error: Can't open cache")
			return
		self.CacheList.clear()
		for items in ItemsList:
			self.CacheList.add_row(items[0].swapcase()+".uxx", items[1])
		self.CachePath = self.CacheDirEntry.get_text()
		self.SetStatus("Cache loaded")

	def SetStatus(self, status_str):
		self.StatusTxt.set_text(status_str)

	def Export(self, widget):
		"""Saving function"""
		cnames = self.CacheList.get_cselected()
		#dname = self.DirList.get_filename()
		dname = self.DirList.get_current_folder()
		try:
			for name in cnames:
				shutil.copy(self.CachePath + "/" + name, dname + "/" + self.CCache.GetFileName(name))
		except:
			self.SetStatus("Error: Save failed")

if __name__ == "__main__":
	pyUCM = UCM()
	pyUCM.MainWin.show_all()
	Gtk.main()
