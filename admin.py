#!/usr/bin/python
''' Admin Tool for veximpy

Command line utility.
'''

__author__ = 'Markus Gschwendt'
__copyright__ = 'See the file README.md for further information'
__license__ = 'See the file LICENSE for further information'

import click
import sys, os
from app.app import create_app
from app.models.siteadminadd import create_sitedomain, create_siteadmin, set_siteadminpassword

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

@click.command()
@click.option('-p', '--password', prompt='New siteadmin password', prompt_required=False, hide_input=True, confirmation_prompt=True,
      help='Sets a new password for the siteadmin user.')
@click.option('-s', '--siteinit', prompt='New siteadmin password', prompt_required=False, hide_input=True, confirmation_prompt=True,
      help='Create site domain and siteadmin account in database.')
def main(password, siteinit):
        if siteinit:
            create_sitedomain(app)
            try:
                create_siteadmin(app, siteinit)
            except:
                print('Error during creation of siteadmin.')
        if password:
            try:
                set_siteadminpassword(app, password, None)
                print('New password set.')
            except:
                print('New password not set.')


if __name__ == "__main__":
    main()


