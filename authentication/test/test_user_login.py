from authentication.test import BaseTestCase, User


class TestUserLogin(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.data = {
            "email": "esirkings@gmail.com",
            "password": "Nice19407#",
        }

    def test_un_registered_user_can_not_login(self):
        """
        Tests that un registered user can not be logged into the system
        """
        response = self.client.post(self.login_url,
                                    data=self.data)
        self.assertEqual(response.json().get('errors').get('error')[0],
                         "Invalid credentials Were Provided")
        self.assertEqual(400, response.status_code)

    def test_registered_user_can_login_to_the_system(self):
        self.client.post(self.registration_url,
                         data=self.user)
        response = self.perform_request('post', self.login_url, data={"email": "shiko@gmail.com",
                                        "password": "Nice19407#"})

        self.assertEqual(200, response.status_code)
        self.assertIn('token', response.data)
