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

if [ ! -f "${1}" ]; then
    echo "file ${1} does not exist"
    exit
fi

CNT_ORIGIN=$(grep -o "${2}" ${1} | wc -l)
CNT_TARGET=$(grep -o "${3}" ${1} | wc -l)

if [[ ${CNT_ORIGIN} -eq 0 ]] && [[ ${CNT_TARGET} -eq 0 ]]; then
    echo "wether original DB ${2} nor target DB ${3} found in file ${1}"
    exit
fi

if [[ ${CNT_ORIGIN} -gt 0 ]]; then
    sed -i "s/${2}/${3}/" ${1}
fi

echo "create and import to target database ${3}"
echo "the user must exist and have create access to the target DB ${3}"
echo "mysql host: [127.0.0.1]"
read HOST
echo "mysql port [3306]: "
read PORT
echo "mysql user: "
read USER
echo "mysql passwd: "
stty -echo
read PW
stty echo

if [[ -z ${HOST} ]]; then
    HOST="127.0.0.1"
fi

if [[ -z ${PORT} ]]; then
    PORT="3306"
fi
echo "mysql -u ${USER} -pXXXXXXXXXX -h ${HOST} -P ${PORT}"

# create and populate mysqldb
mysql -v -u ${USER} -p${PW} -h ${HOST} -P ${PORT} -e "CREATE DATABASE IF NOT EXISTS ${3}"
if [[ $? -eq 0 ]]; then
    mysql -v -u ${USER} -p${PW} -h ${HOST} -P ${PORT} ${3} < ${1}
fi
if [[ $? -ne 0 ]]; then
    echo "Abort after MySQL error"
    exit
fi

# call the script which handles `flask db {init|migrate|upgrade}´
if [[ -f "$(dirname ${0})/dbreinit.sh" ]]; then
    bash $(dirname ${0})/dbreinit.sh ${3}
else
    echo "$(dirname ${0})/dbreinit.sh does not exist"
fi
