from http import HTTPStatus

from django.test import RequestFactory, TestCase, Client, override_settings
from web.views import about, index


class TestViews(TestCase):
    @override_settings(
        STORAGE_DESTINATION="testing"
   )
    def setUp(self):
        self.client = Client()

    # def test_index_happy_path(self):
    #     # Create a request object
    #     response = self.client.get("/")
    #     self.assertEqual(response.status_code, 200)

    # def test_about_happy_path(self):
    #     # Create a request object
    #     response = self.client.get("/about")
    #     self.assertEqual(response.status_code, 200)


class RobotsTxtTests(TestCase):
    @override_settings(
        STORAGE_DESTINATION="testing"
   )
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)
