from authentication.test import BaseTestCase

import tempfile
from django.core.files.storage import FileSystemStorage
from PIL import Image


def generate_image_for_testing():
    # Create an empty temporary image for testing
    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file)
    return tmp_file


class TestUserPassportFeature(BaseTestCase):

    def test_un_logged_in_user_can_not_upload_picture(self):
        """
        Tests that un logged_in user can not upload a passport photo into the system
        """
        tmp_file = generate_image_for_testing()
        response = self.client.post(self.user_passport_url,
                                    data={'passport': tmp_file})

        self.assertEqual(403, response.status_code)

    def test_logged_in_user_can_upload_passport_to_the_system(self):
        self.perform_request('post', url=self.registration_url, data=self.user)

        res = self.perform_request('post', url=self.login_url, data={
                                                                "email": "shiko@gmail.com",
                                                                "password": "Nice19407#"})

        tmp_file = generate_image_for_testing()
        token = res.json().get('token')
        response = self.client.post(self.user_passport_url,
                                    data={'passport': tmp_file},
                                    HTTP_AUTHORIZATION=f"Token {token}")

        self.assertEqual(200, response.status_code)
        self.assertIn('success', response.data)

        # Finally Delete the uploaded photo from the file system
        fs = FileSystemStorage()
        fs.delete(response.json().get('success').get('uploaded_file_url').split('/')[-1])
