from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
import django.contrib.auth

class LoginViewPostTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123'
        )
        self.url = reverse('website:login-view-post')  # URL for login POST

    def test_valid_login_redirects_to_index(self):
        """POST with valid credentials should log in and redirect to index."""
        data = {'username': 'testuser', 'password': 'StrongPass123'}
        response = self.client.post(self.url, data, follow=True)

        self.assertRedirects(response, reverse('website:index-view'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_invalid_login_shows_error(self):
        """POST with invalid credentials should show error message."""
        data = {'username': 'testuser', 'password': 'WrongPass'}
        response = self.client.post(self.url, data, follow=True)

        self.assertRedirects(response, reverse('website:login-view-get'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid username/email or password.' in str(m) for m in messages))

    def test_non_post_request_redirects_to_login(self):
        """GET request should redirect to login page."""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('website:login-view-get'))

    def test_exception_handling_shows_server_error(self):
        from unittest.mock import patch
        """Simulate exception during authenticate and show server error."""
        with patch('project.views.authenticate', side_effect=Exception("Test exception")):
            data = {'username': 'testuser', 'password': 'StrongPass123'}
            response = self.client.post(self.url, data, follow=True)

            self.assertRedirects(response, reverse('website:login-view-get'))
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any('Server error' in str(m) for m in messages))
    
    def test_wrong_credentials_show_error_message(self):
        """
        If credentials are incorrect, 
        the view should show 'Invalid username/email or password.' 
        and redirect to login page.
        """
        # Valid form data, but wrong password
        data = {'username': 'testuser', 'password': 'WrongPassword'}
        response = self.client.post(self.url, data, follow=True)
        # print(response.reason_phrase)
        # print(response.wsgi_request)
        # ✅ Expect redirect to login page
        self.assertRedirects(response,reverse('website:login-view-get'))

        # # ✅ Expect same error message
        messages = list(get_messages(response.wsgi_request))
        # print(messages)
        self.assertTrue(
            any('Invalid username/email or password.' in str(m) for m in messages),
            "Expected 'Invalid username/email or password.' message not found"
        )
    
    def test_login_with_email(self):
        """User can log in using email instead of username."""
        data = {'username': 'test@example.com', 'password': 'StrongPass123'}  # correct password
        response = self.client.post(self.url, data, follow=True)

        # Should redirect to index view on successful login
        self.assertRedirects(response, reverse('website:index-view'))

        # User should be authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].email, 'test@example.com')
    
    def test_login_with_email_invalid(self):
        """
        Login attempt using an invalid email should fail 
        and show the 'Invalid username/email or password.' message.
        """
        data = {'username': 'test@example2.com', 'password': 'WrongPassword'}  # non-existent email
        response = self.client.post(self.url, data, follow=True)

        # Should redirect back to login page
        self.assertRedirects(response, reverse('website:login-view-get'))

        # Check that error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any('Invalid username/email or password.' in str(m) for m in messages),
            "Expected 'Invalid username/email or password.' message not found"
        )

        # Ensure user is not authenticated
        self.assertFalse(response.context['user'].is_authenticated)




