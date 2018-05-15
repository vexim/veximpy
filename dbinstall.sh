#!/bin/bash

if [[ -z "${1}" ]]; then
    SQL_SCHEMA="veximtest"
else
    SQL_SCHEMA="${1}"
fi

echo "Password for the siteadmin user:"
stty -echo
read SITEADMIN_PW
stty echo

# call the script which handles `flask db {init|migrate|upgrade}´
if [[ -f "$(dirname ${0})/dbreinit.sh" ]]; then
    . $(dirname ${0})/dbreinit.sh ${DB_TARGET}
    python3 app/models/siteadminadd.py ${SITEADMIN_PW}
else
    echo "$(dirname ${0})/dbreinit.sh does not exist"
fi

exit

