#!/usr/bin/python
''' Admin Tool for veximpy

Command line utility.
'''

__author__ = 'Markus Gschwendt'
__copyright__ = 'See the file README.md for further information'
__license__ = 'See the file LICENSE for further information'

import click
from app.models.siteadminadd import create_siteadmin
@click.command()
@click.option('-p', '--password', prompt='New siteadmin password:', hide_input=True, confirmation_prompt=True,
      help='Sets a new password for the siteadmin user')
@click.option('-s', '--siteinit',
      help='Create site domain and siteadmin account in database.')
def main(password, siteinit):
    if password:
        create_siteadmin(password)
    elif siteinit:
        create_siteadmin(password)
    else:
        print('something went wrong...')


if __name__ == "__main__":
    main()


