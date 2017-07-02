import httplib2
import os
from oauth2client import client
from oauth2client import tools 
from oauth2client.file import Storage
import argparse



try:
    import argparse as argp
    parser = argp.ArgumentParser(parents=[tools.argparser])
    flags, extras = parser.parse_known_args(None)
except ImportError:
    flags = None

SCOPES = "https://www.googleapis.com/auth/drive"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'RPi Security'

def get_credentials():
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.nakedirs(credential_dir)
	credential_path = os.path.join(credential_dir, 'drive-python-quickstart.json')
	
	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		print ("Stored credentials to :" + credential_path)
	return credentials

