#!/bin/bash

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


# call the script which handles `flask db {init|migrate|upgrade}´
if [[ -f "$(dirname ${0})/dbreinit.sh" ]]; then
    . $(dirname ${0})/dbreinit.sh ${DB_TARGET}

    mysql -v -u ${DB_USER} -p${DB_PW} -h ${DB_HOST} -P ${DB_PORT} -e "INSERT INTO `veximtest`.`domains` (`domain_id`, `domain`) VALUES ('0', 'site')"
    mysql -v -u ${DB_USER} -p${DB_PW} -h ${DB_HOST} -P ${DB_PORT} -e "INSERT INTO `${DB_TARGET}`.`users` (`user_id`, `domain_id`, `localpart`, `username`, `crypt`, `admin`, `role`) VALUES ('0', '43', 'siteadmin', 'siteadmin', ${SITEADMIN_CRYPT}, 1, 192)"
else
    echo "$(dirname ${0})/dbreinit.sh does not exist"
fi

