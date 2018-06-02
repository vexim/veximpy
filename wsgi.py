# wsgi.py

import os
import sys
from instance.config import ENV_FLASK_CONFIG
path = os.path.dirname(sys.argv[0])
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_CONFIG'] = ENV_FLASK_CONFIG

from run import app as application
