# run.py
# This file is part of veximpy

import os

from app.app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
