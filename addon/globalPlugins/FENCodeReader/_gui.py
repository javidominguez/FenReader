# -*- coding: UTF-8 -*-
"""
NVDA Addon to translate from FEN code (Forsyth-Edwards Notation) to human friendly description

This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright  (c) 2015-2021 Javi Dominguez <fjavids@gmail.com>
"""

import addonHandler
import api
import config
import gui
import ui
import wx
from . import fen

# Settings compatibility with older versions of NVDA
from gui import settingsDialogs
try:
	from gui import NVDASettingsDialog
	from gui.settingsDialogs import SettingsPanel
except:
	SettingsPanel = object

addonHandler.initTranslation()

# Class inspired by the DLEChecker addon by antramcs with contributions from HXeBoLaX
class DialogMsg(wx.Dialog):
# Function taken from the add-on emoticons to center the window
	def _calculatePosition(self, width, height):
		w = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
		h = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
		# Centre of the screen
		x = w / 2
		y = h / 2
		# Minus application offset
		x -= (width / 2)
		y -= (height / 2)
		return (x, y)

	def __init__(self, parent, title, message):
		WIDTH = 800
		HEIGHT = 600
		pos = self._calculatePosition(WIDTH, HEIGHT)

		super(DialogMsg, self).__init__(parent, -1, title=title, pos = pos, size = (WIDTH, HEIGHT))

		self.message = message

		panelDialog= wx.Panel(self)

		mainBox= wx.BoxSizer(wx.VERTICAL)
		verticalBox = wx.BoxSizer(wx.VERTICAL)
		horizontalBox = wx.BoxSizer(wx.HORIZONTAL)

		label= wx.StaticText(panelDialog, wx.ID_ANY, label=_("Board:"))
		boardText= wx.TextCtrl(panelDialog, wx.ID_ANY, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL) 

		verticalBox.Add(label, 0, wx.EXPAND)
		verticalBox.Add(boardText, 1, wx.EXPAND | wx.ALL)

		self.readButton = wx.Button(panelDialog, wx.ID_ANY, _("Read position"))
		self.CopyButton = wx.Button(panelDialog, wx.ID_ANY, _("Copy to clipboard"))
		self.exitButton = wx.Button(panelDialog, wx.ID_CANCEL, _("Close"))

		horizontalBox.Add(self.readButton, 0, wx.CENTER)
		horizontalBox.Add(self.CopyButton, 0, wx.CENTER)
		horizontalBox.Add(self.exitButton, 0, wx.CENTER)

		mainBox.Add(verticalBox, 1, wx.EXPAND | wx.ALL)
		mainBox.Add(horizontalBox, 0, wx.CENTER)

		panelDialog.SetSizer(mainBox)

		self.Bind(wx.EVT_BUTTON, self.onRead, self.readButton)
		self.Bind(wx.EVT_BUTTON, self.onCopy, self.CopyButton)
		self.Bind(wx.EVT_BUTTON, self.onClose, id=wx.ID_CANCEL)

		boardText.WriteText(self.message)
		boardText.SetInsertionPoint(0) 

	def onRead(self, event):
		ui.message(self.message)

	def onCopy(self, event):
		api.copyToClip(self.message)
		ui.message(_("Copied to clipboard"))

	def onClose(self, event):
		self.Destroy()
		gui.mainFrame.postPopup()

# Settings GUI compatible with all versions of NVDA

class Settings():
	
	def makeSettings(self, sizer):
		self.phoneticMethodCheckBox=wx.CheckBox(self, wx.NewId(), label=_("Use phonetic alphabet in column names"))
		self.phoneticMethodCheckBox.SetValue(config.conf["FENReader"]["phoneticMethod"])
		sizer.Add(self.phoneticMethodCheckBox,border=10,flag=wx.BOTTOM)
		self.clipboardCheckBox=wx.CheckBox(self, wx.NewId(), label=_("Always copy position to clipboard"))
		self.clipboardCheckBox.SetValue(config.conf["FENReader"]["clipboard"])
		sizer.Add(self.clipboardCheckBox,border=10,flag=wx.BOTTOM)
		self.showWindowCheckBox=wx.CheckBox(self, wx.NewId(), label=_("Show position in a window"))
		self.showWindowCheckBox.SetValue(config.conf["FENReader"]["showWindow"])
		sizer.Add(self.showWindowCheckBox,border=10,flag=wx.BOTTOM)

class FENReaderPanel(SettingsPanel, Settings):
	#TRANSLATORS: Settings panel title
	title=_("FEN reader")

	def makeSettings(self, sizer):
		Settings.makeSettings(self, sizer)

	def onSave(self):
		config.conf["FENReader"]["phoneticMethod"] = self.phoneticMethodCheckBox.GetValue()
		fen.phoneticMethod = self.phoneticMethodCheckBox.GetValue()
		config.conf["FENReader"]["clipboard"] = self.clipboardCheckBox.GetValue()
		config.conf["FENReader"]["showWindow"] = self.showWindowCheckBox.GetValue()

class FENReaderSettings(settingsDialogs.SettingsDialog, Settings):
	#TRANSLATORS: Settings dialog title
	title=_("FEN reader settings")

	def makeSettings(self, sizer):
		Settings.makeSettings(self, sizer)

	def postInit(self):
		self.phoneticMethodCheckBox.SetFocus()

	def onOk(self, evt):
		config.conf["FENReader"]["phoneticMethod"] = self.phoneticMethodCheckBox.GetValue()
		fen.phoneticMethod = self.phoneticMethodCheckBox.GetValue()
		config.conf["FENReader"]["clipboard"] = self.clipboardCheckBox.GetValue()
		config.conf["FENReader"]["showWindow"] = self.showWindowCheckBox.GetValue()
		super(FENReaderSettings, self).onOk(evt)
