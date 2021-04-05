# -*- coding: UTF-8 -*-

# FEN (Forsyth-Edwards Notation) decoder
# Javi Dominguez <fjavids@gmail.com>
# October 2015

import addonHandler
import re

addonHandler.initTranslation()

notationLanguage = 0
notations = (
(_("English"), "KQRBNPkqrbnp"),
(_("Spanish"), "RDTACPrdtacp"),
(_("French"), "RDTFCPrdtfcp")
)
phoneticColumnNames = {
"A": _("Alpha"),
"B": _("Bravo"),
"C": _("Charlie"),
"D": _("Delta"),
"E": _("Echo"),
"F": _("Foxtrot"),
"G": _("Golf"),
"H": _("Hotel")
}

class piece():
	def __init__(self, sign, singleName, pluralName):
		self.sign = sign
		self.singleName = singleName
		self.pluralName = pluralName
		self.squares = []
	def getSquares(self):
		if not self.squares:
			return("")
		l = len(self.squares)
		if l== 1:
			return (_("%s at %s.\n") %(self.singleName, self.squares[0]))
		self.squares.sort()
		list = _("%s at %s") %(self.pluralName, self.squares[0])
		for i in range (1, l-1):
			list = "%s, %s" %(list, self.squares[i])
		list = _("%s and %s.\n") %(list, self.squares[-1])
		return(list)
		
def decode(fenCode, signs="KQRBNPkqrbnp"):
	pieces = [
	piece(signs[0], _("White King"), _("White kings")),
	piece(signs[1], _("White Queen"), _("White queens")),
	piece(signs[2], _("White rook"), _("White rooks")),
	piece(signs[3], _("White bishop"), _("White bishops")),
	piece(signs[4], _("White knight"), _("White knights")),
	piece(signs[5], _("White pown"), _("White powns")),
	piece(signs[6], _("Black King"), _("Black kings")),
	piece(signs[7], _("Black Queen"), _("Black queens")),
	piece(signs[8], _("Black rook"), _("Black rooks")),
	piece(signs[9], _("Black bishop"), _("Black bishops")),
	piece(signs[10], _("Black knight"), _("Black knights")),
	piece(signs[11], _("Black pown"), _("Black powns")) ]
	column = ("A","B","C","D","E","F","G","H")
	rows = fenCode.split()[0].split("/")
	if len(rows) != 8:
		return("")
	for r in range (0, 8):
		if len(rows[r]) > 8:
			return("")
		c = 0
		skip = 0
		while c<8 and c<len(rows[r]):
			try:
				skip = skip + int(rows[r][c])-1
			except:
				p = 0
				searching = True
				while p<len(pieces) and searching:
					if rows[r][c] == pieces[p].sign:
						try:
							pieces[p].squares.append("%s%d" %(column[c+skip], 8-r))
							searching = False
						except:
							# column out of range indicates bad FEN code
							return("")
					p = p+1
				if searching:
					return("")
			c = c+1
		if c+skip != 8:
			return("")
	board = ""
	for p in pieces:
		board = board+p.getSquares()
	try:
		gameTurn = fenCode.split()[1]
		if gameTurn.upper() == "W":
			board = _("%s\nWhite plays") % board
		elif gameTurn.upper() == "B":
			board = _("%s\nBlack plays") % board
	except:
		pass
	if True: # Config value phonetic method
		for c in "ABCDEFGH":
			for r in "12345678":
				board = re.sub(c+r, phoneticColumnNames[c]+r, board)
	return(board)
	