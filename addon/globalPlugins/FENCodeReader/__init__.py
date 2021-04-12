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
from ._gui import *

confspec = {
	"phoneticMethod":"boolean(default=False)",
	"clipboard":"boolean(default=False)",
	"showWindow":"boolean(default=False)"
	}
config.conf.spec["FENReader"]=confspec

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	scriptCategory = "FEN reader"

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if hasattr(settingsDialogs, 'SettingsPanel'):
			NVDASettingsDialog.categoryClasses.append(FENReaderPanel)
		else:
			self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
			#TRANSLATORS: The configuration option in NVDA Preferences menu
			self.FENReaderSettingsItem = self.prefsMenu.Append(wx.ID_ANY, u"FEN reader...", _("FEN reader settings"))
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onFENReaderMenu, self.FENReaderSettingsItem)
		fen.phoneticMethod = config.conf["FENReader"]["phoneticMethod"]

	def onFENReaderMenu(self, evt):
		# Compatibility with older versions of NVDA
		gui.mainFrame._popupSettingsDialog(FENReaderSettings)

	def terminate(self):
		try:
			if hasattr(settingsDialogs, 'SettingsPanel'):
				NVDASettingsDialog.categoryClasses.remove(FENReaderPanel)
			else:
				self.prefsMenu.RemoveItem(self.FENReaderSettingsItem)
		except:
			pass

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
			
	def describeBoard(self):
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
				if config.conf["FENReader"]["clipboard"]:
					if not api.copyToClip(description) and versionInfo.version_year < 2019:
						win32clipboard.OpenClipboard()
						win32clipboard.EmptyClipboard()
						win32clipboard.SetClipboardText(description)
						win32clipboard.CloseClipboard()
						if not config.conf["FENReader"]["showWindow"]: ui.message(_("Copied to clipboard"))
					else:
						if not config.conf["FENReader"]["showWindow"]: ui.message(_("Copied to clipboard"))
				if config.conf["FENReader"]["showWindow"]:
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

	__gestures = {
	"kb:NVDA+Control+F8": "describeBoard"
	}
