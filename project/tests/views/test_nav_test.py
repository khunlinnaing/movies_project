from django.test import TestCase, RequestFactory
from django.template import Context
from django.urls import reverse, resolve
from project.templatetags.nav_tags import url_name_in  # adjust path

class UrlNameInTagTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_url_name_in_matches(self):
        """Returns True if the current url_name is in the provided names."""
        url = reverse('website:index-view')
        request = self.factory.get(url)

        # Attach resolver_match manually
        request.resolver_match = resolve(url)

        context = Context({'request': request})

        result = url_name_in(context, 'index-view', 'login-view-get')
        self.assertTrue(result)

    def test_url_name_in_not_matches(self):
        """Returns False if the current url_name is not in the provided names."""
        url = reverse('website:index-view')
        request = self.factory.get(url)
        request.resolver_match = resolve(url)

        context = Context({'request': request})
        result = url_name_in(context, 'login-view-get', 'signup-view')
        self.assertFalse(result)

    def test_url_name_in_missing_request(self):
        """Returns False if the request is missing from context."""
        context = Context({})
        result = url_name_in(context, 'index-view')
        self.assertFalse(result)

    def test_url_name_in_missing_resolver_match(self):
        """Returns False if request.resolver_match is missing or None."""
        class DummyRequest:
            resolver_match = None

        context = Context({'request': DummyRequest()})
        result = url_name_in(context, 'index-view')
        self.assertFalse(result)
