#!/bin/bash
# This file is part of veximpy

# BASE_DIR should be one level above this script
BASE_DIR="$(realpath $(dirname ${0})/..)"

MIGRATIONS_DIR="${BASE_DIR}/migrations"
INSTANCE_CONFIG="${BASE_DIR}/instance/config.py"
DBREINIT_SH="${BASE_DIR}/setup/dbreinit.sh"

if [[ -d "${MIGRATIONS_DIR}" ]]; then
    echo "Directory 'migrations' exists. If you really want to install a new DB remove it: \`rm -r ${MIGRATIONS_DIR}\`"
    exit
fi

if [[ ! -f "${INSTANCE_CONFIG}" ]]; then
    echo "Config file is missing: ${INSTANCE_CONFIG}"
fi

if [[ ! -f "${DBREINIT_SH}" ]]; then
    echo "${DBREINIT_SH} does not exist"
fi



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
cd ${BASE_DIR} 
. activate
. ${DBREINIT_SH} ${DB_TARGET}
python3 app/models/siteadminadd.py ${SITEADMIN_PW}

exit

