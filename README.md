Right now lots of things are untested!
Use this code on your own risk!

# Install & Migration from vexim2

If you get some `Duplicate index` warnings - ignore them.

## Requirements

Debian Bookworm for `sqlalchemy` >=1.4.

## Install Python3 environment

Create and cd to a directory where you want to install veximpy

Eg: `mkdir -p ~/projects/veximpy; cd ~/projects/veximpy`

Get the code `git clone git@gitlab.com:runout/veximpy.git`

Call `bash setup/pysetup.sh`

This creates a virtual environment under `venv` and modified templates for nginx and uwsgi under `doc`

If a domain/server name is provided as first parameter it will be used for the nginx template. 

You have to **edit the DB credentials** and set **SECRET\_KEY** in `instance/config.py`.

In `wsgi.py` set **os.environ['FLASK_CONFIG'] = 'production'**

## Install a new vexim DB

Create a DB and a DB user. (DB must exist!). Make sure there is no `migrations/` directory.

Shell-Example to create DB `veximtest` and DB user `vximpy`. Additionally (optional) we create a DB `veximtest_test` for `pytest`:

```
echo "CREATE USER 'veximpy'@localhost IDENTIFIED BY '<STRONG_PASSWORD>';" | mysql
echo "CREATE DATABASE veximtest;" | mysql
echo "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, EVENT, TRIGGER ON veximtest.* TO 'veximpy'@localhost;" | mysql
echo "CREATE DATABASE veximtest_test;" | mysql
echo "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, EVENT, TRIGGER ON veximtest_test.* TO 'veximpy'@localhost;" | mysql
echo "FLUSH PRIVILGES;" | mysql
```

Then simply call: `bash setup/dbinstall.sh <targetDBname>`

This will create tables in the DB <targetDBname>.

Call `python3 admin.py --siteinit` to create dataase records for the `site` domain and the `siteadmin` user. You will be prompted to provide the password or you can provide it after the password option.


If \<targetDBname\> is ommited, 'veximtest' will be used as target DB.

## Migrate an existing vexim2 DB

Migration should be done to a new DB. (in-place-migration is not reccomended due to potentional data loss)

Make sure there is no `migrations/` directory.

Create a dump from your original vexim DB.

Eg: `mysqldump -u <username> -p -h <dbhost> --default-character-set=utf8 --single-transaction=TRUE --routines --events "<vexim2db>" > dump.sql`

Create a DB user for the new DB. Replace 10.0.0.% with the host or network where the veximpy application resides.

```
echo "CREATE USER '<username>'@'10.0.0.%' IDENTIFIED BY '<password>';" | mysql
echo "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, EVENT, TRIGGER ON '<targetDBname>'.* TO '<username>'@'10.0.0.%';" | mysql
```

Then call (with 3 parameters):

`bash dbmigration-mysql.sh <dumpfile.sql> <originDBname> <targetDBname>`

You will be prompted for a target DB host, port, user and password.
It will call the `bash dbreinit.sh <targetDBname>` script in the end.

More information can be found inside the `dbreinit.sh` script file.
Even an example for creating a dump from your original vexim DB.

## NGINX, UWSGI

Install nginx and uwsgi

`apt install nginx-full uwsgi uwsgi-plugin-python3`

Sample files can be found under the `doc` directory.

Make sure you have certificates for the domain(s)

Review, edit and copy these files to `/etc/nginx/sites-available` and `/etc/uwsgi/apps-available`. Set appropriate symlinks in the \*-enabled directories and restart nginx/uwsgi.

## Configuration

See `instance/config.py` for DB variables.

See `app/config/settings.py` for defaults and other variables.

# Logo per Domain

Under `app/static/ressources` create a directory for every domain in your database with the Logo as SVG. The filename must be `logo.svg`

Eg: `app/static/ressources/example.com/logo.svg`

# Reset the siteadmin password

Call `python3 admin.py --password` to change password for the `siteadmin` user. You will be prompted to provide the password or you can provide it after the password option.

# Automated tests

If you want to run tests, create an additional DB `veximtest_test`! Tests destroy all data, create there own data and truncate all tables in the end! The test DB is configured in `instance/config.py`

`pytest -v` will run all configured tests.

See the `app/tests` directory and `app/lib/tests.py`.

# Internal Notes:

Create or upgrade a new database: `bash ./dbreinit.sh`.
This script does some magic on setting the name for the database (set the variable inside the file) and adds missing imports to the versions file of alembic/flask-migrate.
It calls `flask db init`, `flask db migrate` and `flask db upgrade`.

## Reverse engeneering of an existing database

```
echo "mysql user: "; read USER; echo "mysql passwd: "; stty -echo; read PW; stty echo; flask-sqlacodegen --flask --schema maildb_vexim2 mysql://${USER}:${PW}@127.0.0.1/maildb_vexim2 | sed "s/maildb\_vexim2\.//"
```

# License
For a copy of the License see the file COPYING.

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


