# -*- coding: UTF-8 -*-

# NVDA Addon to translate from FEN code (Forsyth-Edwards Notation) to human friendly description
# Javi Dominguez <fjavids@gmail.com>
# V 1.0 October 2015

import globalPluginHandler
import addonHandler
import api
import ui
import textInfos
import win32clipboard
from time import sleep
from threading import Thread
import fen

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	scriptCategory = "FEN Reader"
	
	def getSelection(self):
		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except :
			info=None
		if not info or info.isCollapsed:
			return(None)
		else:
			return(info.text)
			
	def describeBoard(self, copyToClipboard=False):
		selectedText = self.getSelection()
		if selectedText:
			# Search a valid code into selected text
			description = None
			c = 0
			l = len(selectedText)
			timeForSearching = Thread(target=sleep, args=(0.2,))
			timeForSearching.start()
			while not description and c < l-16:
				if not timeForSearching.isAlive():
					ui.message(_("Too much text has been selected"))
					return()
				description = fen.decode(selectedText[c:], fen.notations[fen.notationLanguage][1])
				c = c+1
			if description:
				if copyToClipboard:
					win32clipboard.OpenClipboard()
					win32clipboard.EmptyClipboard()
					win32clipboard.SetClipboardText(description)
					win32clipboard.CloseClipboard()
					ui.message(_("Copied to clipboard"))
				ui.message(description)
			else:
				ui.message(_("Selected text doesn't contains a valid FEN code"))
		else:
			ui.message(_("There is not selected text"))
			
	def script_describeBoard(self, gesture):
		self.describeBoard()
	# Translators: Message presented in input help mode.
	script_describeBoard.__doc__ = _("if selected text contains a valid FEN code, describes the chess game position")

	def script_copyToClipboard(self, gesture):
		self.describeBoard(True)
	# Translators: Message presented in input help mode.
	script_copyToClipboard.__doc__ = _("if selected text contains a valid FEN code, describes the chess game position and copy it to clipboard")
	
	def script_changeNotationLanguage(self, gesture):
		fen.notationLanguage = fen.notationLanguage+1
		if fen.notationLanguage >= len(fen.notations):
			fen.notationLanguage = 0
		ui.message(fen.notations[fen.notationLanguage][0])
	# Translators: Message presented in input help mode.
	script_changeNotationLanguage.__doc__ = _("Changes chess notation language")
	
	__gestures = {
	"kb:NVDA+Control+F8": "describeBoard",
	"kb:NVDA+Shift+F8": "copyToClipboard",
	"kb:NVDA+Control+Shift+F8": "changeNotationLanguage"
	}