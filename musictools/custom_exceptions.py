class SongNotFound(Exception):
	def __init__(self, message, dErrorArg):
		Exception.__init__(self, message, dErrorArg)

