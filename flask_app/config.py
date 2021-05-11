from mongoengine import connect
import os
#DEFAULT_CONNECTION_NAME = connect('final_project')

MONGODB_SETTINGS = {'db':'final_project', 'alias':'default'}

# Stores all configuration values
SECRET_KEY = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'
MONGODB_HOST = os.getenv("MONGODB_HOST")
