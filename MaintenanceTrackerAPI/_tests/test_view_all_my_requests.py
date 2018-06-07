from MaintenanceTrackerAPI._tests import BaseTestCase, db
from MaintenanceTrackerAPI.api.v1 import api_v1
from MaintenanceTrackerAPI.api.v1.auth import Login
from MaintenanceTrackerAPI.api.v1.exceptions import UserTransactionError
from MaintenanceTrackerAPI.api.v1.models.user_model import User
from MaintenanceTrackerAPI.api.v1.users import SingleUserAllRequests


class ViewMyRequestsTestCase(BaseTestCase):
    def login(self, data: dict):
        """
        Helper function for logging in a user.
        :param data: A dictionary containing data necessary for logging in
        :return: response object
        """
        try:
            User('viewrequests@consumer.com', 'password.Pa55word',
                 'What is your favourite company?', 'Company')
            User('viewrequests@admin.com', 'password.Pa55word',
                 'What is your favourite company?', 'Company',
                 'Administrator')
        except UserTransactionError:
            pass

        response = self.client.post(api_v1.url_for(Login), data=str(data),
                                    content_type='application/json')
        response_dict = eval(response.data.decode('UTF-8'))
        access_token = response_dict.get('access_token', None)
        return access_token

    def get_requests(self, logged_in: bool = True, admin=False,
                     admin_views_all: bool = False):
        """
        Helper function for making a request via the server.
        :param admin: What user role should be used
        :param logged_in: Whether a user should be logged in or not
        :return: response object
        """

        if admin:
            email = 'viewrequests@admin.com'
        else:
            email = 'viewrequests@consumer.com'

        if admin_views_all:
            email = 'viewrequests@admin.com'

        access_token = self.login(dict(email=email,
                                       password='password.Pa55word'))
        if admin_views_all:
            email = 'viewrequests@consumer.com'
        user_id = db.get_user_by_email(email)['user_id']
        if logged_in:
            return self.client.get(api_v1.url_for(SingleUserAllRequests,
                                                  user_id=user_id),
                                   content_type='application/json',
                                   headers={
                                       'ACCESS_TOKEN':
                                           access_token})
        else:
            return self.client.get(api_v1.url_for(SingleUserAllRequests,
                                                  user_id=user_id),
                                   content_type='application/json')

    def test_get_my_requests_requires_login(self):
        """
        Test that this route requires login
        :return:
        """
        response = self.get_requests(False)
        self.assert401(response)

    def test_get_my_requests_consumer_pass(self):
        """
        Test that a consumer can view their requests
        :return:
        """
        response = self.get_requests()
        self.assertIn(b'requests', response.data)
        self.assert200(response.data)

    def test_get_my_requests_admin_fail(self):
        """
        Test that Administrators do not have requests
        :return:
        """
        response = self.get_requests(admin=True)
        self.assertIn(b'Administrators do not have requests', response.data)

    def test_admin_gets_consumers_requests(self):
        """
        Test that an Administrator can view other consumer's requests
        :return:
        """
        response = self.get_requests(admin_views_all=True)
        self.assert200(response)
        self.assertIn(b'requests', response.data)
