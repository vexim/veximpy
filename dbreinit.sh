#!/bin/bash

SQL_SCHEMA="veximtest"


cp -a app/models/dbclasses.py app/models/dbclasses.py.`date +%Y%m%d-%H%M`.bak
sed -i "s/maildb\_vexim2/${SQL_SCHEMA}/" app/models/dbclasses.py
sed -i "s/^db\s=\sSQLAlchemy/#db = SQLAlchemy/" app/models/dbclasses.py

. activate
if [[ ! -d "migrations" ]]; then
    echo -e "\n\n####################\nflask db upgrade\n"
    flask db init
fi

echo -e "\n\n####################\nflask db migrate\n"
flask db migrate
grep -l -s -L 'from sqlalchemy.schema import FetchedValue' migrations/versions/*.py | \
    xargs sed -i 's/^import\ssqlalchemy\sas\ssa/import sqlalchemy as sa\nfrom sqlalchemy.schema import FetchedValue/'

echo -e "\n\n####################\nflask db upgrade\n"
flask db upgrade
