# -*- coding: UTF-8 -*-
"""
NVDA Addon to translate from FEN code (Forsyth-Edwards Notation) to human friendly description

This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright  (c) 2015-2021 Javi Dominguez <fjavids@gmail.com>
"""

import addonHandler
import api
import wx
import gui
import ui

addonHandler.initTranslation()

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

