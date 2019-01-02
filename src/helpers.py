def removeWhitespace(string):
	string = string.strip().translate( { ord(c):None for c in '\n\t\r' } )

	return string

def removeWikipediaReferences(string):
	string = re.sub(r"\[.*\]","", string)

	return string