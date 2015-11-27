import lastpass, os

mqtt_broker = 'pellet.cave.kevinross.name'

lpusername = os.environ.get('LPUSERNAME', '')
lppassword = os.environ.get('LPPASSWORD', '')

if not lpusername or not lppassword:
	import lpcreds
	lpusername = lpcreds.username
	lppassword = lpcreds.password

class creds(object):
	vault = lastpass.Vault.open_remote(lpusername, lppassword)
	@classmethod
	def get(cls, *args, **kwargs):
		k = list(kwargs.keys())[0]
		v = kwargs[k]
		if callable(v):
			l = filter(lambda x: v(getattr(x, k)), cls.vault.accounts)
		else:
			l = filter(lambda x: getattr(x, k) == v, cls.vault.accounts)
		l = list(l)
		if l:
			return l[0].username, l[0].password
		else:
			return None, None
