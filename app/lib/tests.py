import pytest
from flask import url_for

def assert_status_with_message(status_code=200, response=None, message=None):
    """
    Check to see if a message is contained within a response.

    :param status_code: Status code that defaults to 200
    :type status_code: int
    :param response: Flask response
    :type response: str
    :param message: String to check for
    :type message: str
    :return: None
    """
    assert response.status_code == status_code
    assert message in str(response.data)

def assert_status_with_flashmessage(status_code=200, response=None, client=None, message=None, category='message'):
    """
    Check to see if a flash message is contained within a response.

    :param status_code: Status code that defaults to 200
    :type status_code: int
    :param response: Flask response
    :type response: str
    :param message: String to check for
    :type message: str
    :return: None
    """
    assert response.status_code == status_code

    with client.session_transaction() as session:
        flash_message = dict(session['_flashes']).get(category)
    assert message in flash_message


class ViewTestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(self, identity='admin@local.host', password='password'):
        """
        Login a specific user.

        :return: Flask response
        """
        return login(self.client, identity, password)

    def logout(self):
        """
        Logout a specific user.

        :return: Flask response
        """
        return logout(self.client)


def login(client, username='', password=''):
    """
    Log a specific user in.

    :param client: Flask client
    :param username: The username
    :type username: str
    :param password: The password
    :type password: str
    :return: Flask response
    """
    user = dict(username=username, password=password)

    response = client.post(url_for('auth.login'), data=user, follow_redirects=True)

    return response


def logout(client):
    """
    Log a specific user out.

    :param client: Flask client
    :return: Flask response
    """
    return client.get(url_for('auth.logout'), follow_redirects=True)

