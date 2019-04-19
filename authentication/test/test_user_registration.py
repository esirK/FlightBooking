from authentication.test import BaseTestCase, User


class TestUserRegistration(BaseTestCase):
    def test_new_user_can_register(self):
        count = User.objects.count()
        response = self.perform_request('post', url=self.registration_url, data=self.data)
        self.assertEqual(count+1, User.objects.count())
        self.assertEqual(201, response.status_code)

    def test_user_email_is_unique(self):
        """
        Test that an email can not be used more than once.
        """
        self.client.post(self.registration_url,
                                    data=self.data)
        count = User.objects.count()
        response = self.perform_request('post', url=self.registration_url, data=self.data)

        self.assertEqual(response.json().get('errors').get('email')[0],
                         'user with this email address already exists.')
        self.assertEqual(count, User.objects.count())
        self.assertEqual(400, response.status_code)

    def test_only_valid_emails_are_allowed(self):
        """
        Tests that a user can not register using an invalid email.
        """
        data = dict(self.data)
        data.update({'email': "fakemail.com"})
        response = self.perform_request('post', url=self.registration_url, data=data)

        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json().get('errors').get('email')[0],
                         'Enter a valid email address.')

    def test_password_validation(self):
        """
        Tests to ensure that strong passwords are required during registration.
        """
        data = dict(self.data)
        data.update({'password': "esirkin"})
        response = self.perform_request('post', url=self.registration_url, data=data)
        self.assertEqual(response.json().get('errors')[0],
                         "This password is too short."
                         " It must contain at least 8 characters.")

        data.update({'password': "esirkings"})
        response = self.perform_request('post', url=self.registration_url, data=data)

        self.assertEqual(response.json().get('errors')[0],
                         "This password must contain at least one special character")
        self.assertEqual(400, response.status_code)

    def test_first_name_is_a_required_field(self):
        """
        Ensures a user supplies their first_name during registration
        """
        data = dict(self.data)
        data.pop('first_name')
        response = self.perform_request('post', url=self.registration_url, data=data)

        self.assertEqual(response.json().get('errors').get('first_name')[0],
                         'This field is required.')
        self.assertEqual(400, response.status_code)

    def test_last_name_is_a_required_field(self):
        """
        Ensures a user supplies their last_name during registration
        """
        data = dict(self.data)
        data.pop('last_name')
        response = self.perform_request('post', url=self.registration_url, data=data)

        self.assertEqual(response.json().get('errors').get('last_name')[0],
                         'This field is required.')
        self.assertEqual(400, response.status_code)
