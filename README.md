# Install & Upgrade

If you get some `Duplicate index` warnings - ignore them.
## Install a new vexim DB
Create a DB and a DB user.

Then simply call:

`bash dbreinit.sh <targetDBname>`

This will create tables in the DB <targetDBname>.
If \<targetDBname\> is ommited, 'veximdbtest' will be used.
This script will copy `app/models/models_orig.py` with the \<targetDBname\> as DB to `app/models/models.py`

## Upgrade an existing vexim2 DB
Migration will be done to a new DB. (in-place-migration is not supported)

Create a DB user for the new DB.

Then call (with 3 parameters):

`bash dbmigration-mysql.sh <dumpfile.sql> <originDBname> <targetDBname>`

You will be prompted for a target DB host, port, user and password.
It will call the `bash dbreinit.sh <targetDBname>` script in the end.
More information can be found inside this script file.

# Internal Notes:

Create or upgrade a new database.
This script does some magic on setting the name for the database (set the variable inside the file) and adds missing imports to the versions file of alembic/flask-migrate.
It calls `flask db init`, `flask db migrate` and `flask db upgrade`.

bash ./dbreinit.sh

Reverse engeneering of an existing database

```
echo "mysql passwd: "; stty -echo; read PW; stty echo; flask-sqlacodegen --flask --schema maildb_vexim2 mysql://marco69:${PW}@127.0.0.1/maildb_vexim2 | sed "s/maildb\_vexim2\.//"
```
