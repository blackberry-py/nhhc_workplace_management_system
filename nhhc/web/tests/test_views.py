from http import HTTPStatus

from django.test import RequestFactory, TestCase
from web.views import about, index


class TestViews(TestCase):
    def test_index_happy_path(self):
        # Create a request object
        request = RequestFactory().get("/")
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_about_happy_path(self):
        # Create a request object
        request = RequestFactory().get("/")
        response = about(request)
        self.assertEqual(response.status_code, 200)

    def test_index_edge_case_no_client_ip(self):
        # Create a request object with no client IP
        request = RequestFactory().get("/")
        response = index(request)
        # Add assertions for the expected behavior when client IP is None

    def test_index_edge_case_private_ip(self):
        # Create a request object with a private client IP
        request = RequestFactory().get("/")
        response = index(request)
        # Add assertions for the expected behavior when client IP is private

    def test_about_edge_case(self):
        # Create a request object
        request = RequestFactory().get("/")
        response = about(request)
        # Add assertions for any edge cases specific to the about function


class RobotsTxtTests(TestCase):
    def test_get(self):
        response = self.client.get("/robots.txt")

        assert response.status_code == HTTPStatus.OK
        assert response["content-type"] == "text/plain"
        assert response.content.startswith(b"User-Agent: *\n")

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
