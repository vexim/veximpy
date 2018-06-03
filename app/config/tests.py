# app/config/tests.py

settings = {
    'TEST_USER_SITEADMIN': 'siteadmin',
    'TEST_PW_SITEADMIN': 'TEST-password_1657-siteadmin',
    'TEST_DOMAINTYPE_SITEADMIN': 'local',

    'TEST_2_DOMAINID': 2,
    'TEST_2_DOMAINNAME': '02.example.com',
    'TEST_2_USER_POSTMASTER': 'postmaster',
    'TEST_2_PW_POSTMASTER': 'TEST-password_2-postmaster',
    'TEST_2_USER_USER': 'user1',
    'TEST_2_PW_USER': 'TEST-password_2-user',
    'TEST_2_DOMAINTYPE': 'local',

    'TEST_3_DOMAINID': 3,
    'TEST_3_DOMAINNAME': '03.example.com',
    'TEST_3_USER_POSTMASTER': 'postmaster',
    'TEST_3_PW_POSTMASTER': 'TEST-password_3-postmaster',
    'TEST_3_USER_USER': 'user1',
    'TEST_3_PW_USER': 'TEST-password_3-user',
    'TEST_3_DOMAINALIASID': 1,
    'TEST_3_DOMAINALIASNAME': 'a01.example.com',
    'TEST_3_DOMAINTYPE': 'local',

    'TEST_4_DOMAINRELAYID': 4,
    'TEST_4_DOMAINRELAYNAME': 'r01.example.com',
    'TEST_4_DOMAINTYPE': 'relay',
}

responses = {
    '302': '',
    '404': '> 404 Error <',
}
