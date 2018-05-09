# 

from flask import url_for
from app.lib.tests import assert_status_with_message, ViewTestMixin

import pdb

class TestDomain(ViewTestMixin):
    def test_domain(self, db):
        response = self.client.get(url_for('auth.login'))
        #pdb.set_trace()
        #assert response.status_code == 200
        assert_status_with_message(200, response, 'Markus')
