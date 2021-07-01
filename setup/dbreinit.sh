#!/bin/bash
# This file is part of veximpy

. activate
if [[ ! -d "migrations" ]]; then
    echo -e "\n\n####################\nflask db upgrade\n"
    flask db init
fi

echo -e "\n\n####################\nflask db migrate\n"
flask db migrate
# need additional import in version file before doing the upgrade
# see https://github.com/miguelgrinberg/Flask-Migrate/issues/195
grep -l -s -L 'from sqlalchemy.schema import FetchedValue' migrations/versions/*.py | \
    xargs sed -i 's/^import\ssqlalchemy\sas\ssa/import sqlalchemy as sa\nfrom sqlalchemy.schema import FetchedValue/'

echo -e "\n\n####################\nflask db upgrade\n"
flask db upgrade
