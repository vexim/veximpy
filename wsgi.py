# wsgi.py

import os
import sys

path = '/home/marco69/projects/veximpy'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_CONFIG'] = 'production'
os.environ['FLASK_CONFIG'] = 'development'

from run import app as application
