Right now lots of things are untested!
Use this code on your own risk!

# Install & Upgrade

If you get some `Duplicate index` warnings - ignore them.

## Install Python3 environment

Call `bash pysetup.sh`

This creates a virtual environment under `venv` and modified templates for nginx and uwsgi under `doc`

If a domain/server name is provided as first parameter it will be used for the nginx template. 

You have to edit the file `instance/config.py`.

## Install a new vexim DB
Create a DB and a DB user.

Then simply call:

`bash dbinstall.sh <targetDBname>`

This will create tables in the DB <targetDBname>.

If \<targetDBname\> is ommited, 'veximtest' will be used.

This script will copy `app/models/models_orig.py` with the \<targetDBname\> as DB to `app/models/models.py`

Create the siteadmin Domain with `mysql -u <user> -p -h <host> -p <port> -e "INSERT INTO `domains` (`domain_id`, `domain`) VALUES ('1', 'site')"`

Create the siteadmin User with `mysql -u <user> -p -h <host> -p <port> -e "INSERT INTO `users` (`domain_id`, `localpart`, `username`, `crypt`) VALUES ('1', 'siteadmin', 'siteadmin', '<PASSWORDHASH>')"`

## Upgrade an existing vexim2 DB
Migration will be done to a new DB. (in-place-migration is not supported)

Create a dump from your original vexim DB.

Create a DB user for the new DB.

Then call (with 3 parameters):

`bash dbmigration-mysql.sh <dumpfile.sql> <originDBname> <targetDBname>`

You will be prompted for a target DB host, port, user and password.
It will call the `bash dbreinit.sh <targetDBname>` script in the end.

More information can be found inside this script file.
Even an example for creating a dump from your original vexim DB.

## NGINX, UWSGI

Sample files can be found under the `doc` directory.

Make sure you have certificates for the domain(s)

Review, edit and copy these files to `/etc/nginx/sites-available` and `/etc/uwsgi/apps-available`. Set appropriate symlinks in the *-enabled directories and restart nginx/uwsgi.

# Logo per Domain

Under `app/static/ressources` create a directory for every domain in your database with the Logo as SVG. The filename must be `logo.svg`

Eg: `app/static/ressources/example.com/logo.svg`

# Automated tests

See the `app/tests` directory.

# Internal Notes:

Create or upgrade a new database.
This script does some magic on setting the name for the database (set the variable inside the file) and adds missing imports to the versions file of alembic/flask-migrate.
It calls `flask db init`, `flask db migrate` and `flask db upgrade`.

bash ./dbreinit.sh

Reverse engeneering of an existing database

```
echo "mysql user: "; read USER; echo "mysql passwd: "; stty -echo; read PW; stty echo; flask-sqlacodegen --flask --schema maildb_vexim2 mysql://${USER}:${PW}@127.0.0.1/maildb_vexim2 | sed "s/maildb\_vexim2\.//"
```

# License
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.


