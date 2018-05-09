# wsgi.py

import os
import sys

path = '/home/marco69/projects/veximpy'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_CONFIG'] = 'production'
#os.environ['SECRET_KEY'] = 'p9Bv<3Eid9%$i01'
#os.environ['SQLALCHEMY_DATABASE_URI'] = 'mysql://your-username:your-password@your-host-address/your-database-name'

from run import app as application
