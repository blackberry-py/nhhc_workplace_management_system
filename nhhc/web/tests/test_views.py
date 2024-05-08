from http import HTTPStatus
from django.urls import reverse
from django.test import Client, RequestFactory, TestCase, override_settings
from web.views import AboutUsView, HomePageView


class TestViews(TestCase):
    def setUp(self):
        self.home_request = RequestFactory().get(reverse("homepage"))
        self.homeview = HomePageView()
        self.homeview.setup(self.home_request)
        self.about_request = RequestFactory().get(reverse("about"))
        self.aboutview = AboutUsView()
        self.aboutview.setup(self.about_request)

    def test_get_homepage(self):
        response = HomePageView.as_view()(self.about_request)
        self.assertEqual(response.status_code, 200)

    def test_get_about_page(self):
        response = AboutUsView.as_view()(self.about_request)
        self.assertEqual(response.status_code, 200)


class RobotsTxtTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_post_disallowed(self):
        response = self.client.post("/robots.txt")
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)
