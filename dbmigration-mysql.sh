#!/bin/bash
# this script will migrate your existing vexim2 DB for use with veximpy
# by Markus Gschwendt
#
# usage (parameters have to be in specified order):
#   bash dbmigration.sh <dumpfile.sql> <originDBname> <targetDBname>
# dumpfile.sql will be a dump file from your original DB.
# originDBname is the original DB
# targetDBname is the target DB
#
# create the dump.sql, where "vexim2db" is the name of your original vexim2 DB.
# provide username and hostname. you will be prompted for a password for the given user.
# mysqldump --user=<username> -p --host=<dbhost> --default-character-set=utf8 --single-transaction=TRUE --routines --events "vexim2db"
#

DUMPFILE="${1}"
DB_ORIGIN="${2}"
DB_TARGET="${3}"

if [ ! -f "${DUMPFILE}" ]; then
    echo "file ${DUMPFILE} does not exist"
    exit
fi

if [[ -d "$(dirname ${0})/migrations" ]]; then
    echo "Directory 'migrations' exists. If you really want to install a new DB remove it: \`rm -r migrations\`"
    exit
fi

CNT_ORIGIN=$(grep -o "${DB_ORIGIN}" ${DUMPFILE} | wc -l)
CNT_TARGET=$(grep -o "${DB_TARGET}" ${DUMPFILE} | wc -l)

if [[ ${CNT_ORIGIN} -eq 0 ]] && [[ ${CNT_TARGET} -eq 0 ]]; then
    echo "wether original DB ${DB_ORIGIN} nor target DB ${DB_TARGET} found in file ${DUMPFILE}"
    exit
fi

if [[ ${CNT_ORIGIN} -gt 0 ]]; then
    sed -i "s/${DB_ORIGIN}/${DB_TARGET}/" ${DUMPFILE}
fi

echo "create and import to target database ${DB_TARGET}"
echo "the user must exist and have create access to the target DB ${DB_TARGET}"
echo "mysql host: [127.0.0.1]"
read DB_HOST
echo "mysql port [3306]: "
read DB_PORT
echo "mysql user: "
read DB_USER
echo "mysql passwd: "
stty -echo
read DB_PW
stty echo

if [[ -z ${DB_HOST} ]]; then
    DB_HOST="127.0.0.1"
fi

if [[ -z ${DB_PORT} ]]; then
    DB_PORT="3306"
fi
echo "mysql -u ${DB_USER} -pXXXXXXXXXX -h ${DB_HOST} -P ${DB_PORT}"

# create and populate mysqldb
mysql -v -u ${DB_USER} -p${DB_PW} -h ${DB_HOST} -P ${DB_PORT} -e "CREATE DATABASE IF NOT EXISTS ${DB_TARGET}"
if [[ $? -eq 0 ]]; then
    mysql -v -u ${DB_USER} -p${DB_PW} -h ${DB_HOST} -P ${DB_PORT} ${DB_TARGET} < ${DUMPFILE}
fi
if [[ $? -ne 0 ]]; then
    echo "Abort after MySQL error"
    exit
fi

# call the script which handles `flask db {init|migrate|upgrade}´
if [[ -f "$(dirname ${0})/dbreinit.sh" ]]; then
    . $(dirname ${0})/activate
    . $(dirname ${0})/dbreinit.sh ${DB_TARGET}
    mysql -v -u ${DB_USER} -p${DB_PW} -h ${DB_HOST} -P ${DB_PORT} -e "UPDATE veximtest.users SET role = 64 WHERE admin=1"
    mysql -v -u ${DB_USER} -p${DB_PW} -h ${DB_HOST} -P ${DB_PORT} -e "UPDATE veximtest.users SET role = 192 WHERE user_id=1"
else
    echo "$(dirname ${0})/dbreinit.sh does not exist"
fi

