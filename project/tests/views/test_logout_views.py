from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.logout_url = reverse('website:index-view')  # redirect target
        self.url = reverse('website:logout-view')

    def test_logout_redirects_to_index(self):
        """Test that logout redirects to index-view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.logout_url)

    def test_user_is_logged_out(self):
        """Test that user session is cleared after logout."""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.url)

        # User should no longer be authenticated
        response = self.client.get(self.logout_url)
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)
