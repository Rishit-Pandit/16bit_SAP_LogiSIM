# Helper Functions
def ArrayContains(arr, obj):
	'''
	arr: the array to check
	obj: the object to find
	'''
	contained = False
	for i in  arr:
		if i == obj:
			contained = True
			return True
		else:
			pass
	return contained


def dec_to_hex16(a):
	'''
	a: the integer in decimal
	'''
	if a < 0:
		a = (1 << 16) + a

	b = hex(a)[2:]
	return str(b.zfill(4))


def is_int(a):
	'''
	a: the data to check
	'''
	try:
		int(a)
		return True
	except:
		return False