Create or upgrade a new database.
This script does some magic on setting the name for the database (set the variable inside the file) and adds missing imports to the versions file of alembic/flask-migrate.
It calls `flask db init`, `flask db migrate` and `flask db upgrade`.

bash ./dbreinit.sh

Reverse engeneering of an existing database

```
echo "mysql passwd: "; stty -echo; read PW; stty echo; flask-sqlacodegen --flask --schema maildb_vexim2 mysql://marco69:${PW}@127.0.0.1/maildb_vexim2 | sed "s/maildb\_vexim2\.//"
```
