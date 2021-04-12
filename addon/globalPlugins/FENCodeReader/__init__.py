# -*- coding: UTF-8 -*-
"""
NVDA Addon to translate from FEN code (Forsyth-Edwards Notation) to human friendly description

This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright  (c) 2015-2021 Javi Dominguez <fjavids@gmail.com>
"""

import globalPluginHandler
import addonHandler
import api
import languageHandler
import config
import ui
import textInfos
import versionInfo
if versionInfo.version_year < 2019:
	import win32clipboard
from time import sleep
from threading import Thread
from . import fen
from .gui import *

confspec = {
	"phoneticMethod":"boolean(default=False)",
	"showDialog":"boolean(default=True)"
	}
config.conf.spec["FENReader"]=confspec

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	scriptCategory = "FEN Reader"

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		fen.phoneticMethod = config.conf["FENReader"]["phoneticMethod"]

	def getRawText(self):
		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except :
			info=None
		if not info or info.isCollapsed:
			try:
				return True, api.getClipData()
			except OSError:
				return False, None
		else:
			return False, info.text
			
	def describeBoard(self, copyToClipboard=False):
		fromClipboard, rawText = self.getRawText()
		if rawText:
			# Search a valid code into selected text
			description = None
			c = 0
			l = len(rawText)
			timeForSearching = Thread(target=sleep, args=(0.3,))
			timeForSearching.start()
			while not description and c < l-16:
				if not timeForSearching.isAlive():
					ui.message(_("Too much text has been selected"))
					return
				# First use english notation by default
				description = fen.decode(rawText[c:], fen.notations["en"])
				if not description:
					# Also use the notation for the local language
					localLanguage = languageHandler.getLanguage()[:2]
					if localLanguage in fen.notations and localLanguage != "en":
						description = fen.decode(rawText[c:], fen.notations[localLanguage])
				c = c+1
			if description:
				if copyToClipboard:
					if not api.copyToClip(description) and versionInfo.version_year < 2019:
						win32clipboard.OpenClipboard()
						win32clipboard.EmptyClipboard()
						win32clipboard.SetClipboardText(description)
						win32clipboard.CloseClipboard()
						ui.message(_("Copied to clipboard"))
					else:
						ui.message(_("Copied to clipboard"))
				if config.conf["FENReader"]["showDialog"]:
					dialog = DialogMsg(gui.mainFrame, _("Fen Reader"), description)
					gui.mainFrame.prePopup()
					dialog.Show()
				else:
					ui.message(description)
			else:
				if fromClipboard:
					ui.message(_("There is not selected text"))
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
	
	__gestures = {
	"kb:NVDA+Control+F8": "describeBoard",
	"kb:NVDA+Shift+F8": "copyToClipboard"
	}