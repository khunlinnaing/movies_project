from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages


class LoginViewTests(TestCase):

    def setUp(self):
        # ✅ Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123'
        )

        # ✅ Define URLs
        self.login_url = reverse('website:login-view-post')
        self.login_get_url = reverse('website:login-view-get')
        self.index_url = reverse('website:index-view')
        self.index_template = 'base/body.html'

    # ----------------------------
    # ✅ SUCCESS CASES
    # ----------------------------

    def test_login_with_username_success(self):
        """
        User can log in successfully using their username.
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'securepassword123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.index_template)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_with_email_success(self):
        """
        User can log in successfully using their email.
        (Requires EmailOrUsernameBackend)
        """
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'securepassword123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.index_template)
        self.assertTrue(response.context['user'].is_authenticated)

    # ----------------------------
    # ❌ FAILURE CASES
    # ----------------------------

    def test_login_invalid_credentials(self):
        """
        Invalid credentials should not authenticate the user.
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow=True)

        # Should redirect back to login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_invalid_form(self):
        """
        Empty POST data should trigger form validation errors.
        """
        response = self.client.post(self.login_url, {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertFalse(response.context['user'].is_authenticated)

    # ----------------------------
    # 🚦 REDIRECTS
    # ----------------------------

    def test_get_request_redirects_to_login_get(self):
        """
        GET request to login_view_post should redirect properly.
        """
        response = self.client.get(self.login_url, follow=True)
        self.assertRedirects(response, self.login_get_url)

    # ----------------------------
    # 💬 MESSAGES (for coverage)
    # ----------------------------

    def test_invalid_login_sets_error_message_and_redirects(self):
        """
        When invalid credentials are used, an error message should appear
        and redirect back to login page.
        (Covers messages.error + redirect lines)
        """
        response = self.client.post(self.login_url, {
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow=False)
        print(response)
        # ✅ Should redirect to login-view-get
        self.assertRedirects(response, self.login_get_url)

        # ✅ Check messages
        messages = list(get_messages(response.wsgi_request))
        print(messages)
        self.assertTrue(messages)
        self.assertEqual(str(messages[0]), "Invalid username/email or password.")
        self.assertEqual(messages[0].level_tag, 'error')
