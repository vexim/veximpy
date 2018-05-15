#!/bin/bash
MODELS="$(dirname ${0})/app/models/models.py"
MODELS_ORIG="$(dirname ${0})/app/models/models_orig.py"

if [[ -z "${1}" ]]; then
    SQL_SCHEMA="veximtest"
else
    SQL_SCHEMA="${1}"
fi

echo "${SQL_SCHEMA} will be used as target DB"

sed "s/###targetdb###/${SQL_SCHEMA}/" ${MODELS_ORIG} > ${MODELS}

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
