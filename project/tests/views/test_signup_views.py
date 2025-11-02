from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

class SignupViewTest(TestCase):
    def setUp(self):
        self.url = reverse('website:signup-view')  # adjust to your URL name
        self.login_url = reverse('website:login-view-get')

    def test_get_signup_page(self):
        """Test GET request renders signup form page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertIn('form', response.context)

    def test_post_valid_signup_creates_user_and_redirects(self):
        """Test valid POST creates a new user and redirects to login page."""
        test_image = SimpleUploadedFile("test.jpg", b"profile", content_type="image/jpeg")

        data = {
            'username': 'newuser',
            'first_name': "a",
            'last_name': "b",
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'phone': '09776827',
            'address': 'yangon'
            # include other required fields from your SignupForm if needed
        }

        response = self.client.post(self.url, {**data, 'profile_pic': test_image}, follow=True)
 
        # ✅ Debug form validation if user creation failed
        # if hasattr(response, "context") and response.context and "form" in response.context:
        #     form = response.context["form"]
        #     if form.errors:
        #         print("🔍 FORM ERRORS:", form.errors)

        # ✅ Assert user created
        self.assertTrue(
            User.objects.filter(username='newuser').exists(),
            "❌ User not created. Check if SignupForm.save() actually creates a User."
        )

        # ✅ Check redirect to login page
        self.assertRedirects(response, self.login_url)

        messages = list(response.context.get('messages', []))
        self.assertTrue(
            any("Account created successfully" in str(m) for m in messages),
            "Success message not found after signup redirect."
        )

    def test_get_signup_page_renders_form(self):
        """Test GET request to signup page renders the form correctly."""
        response = self.client.get(self.url)  # GET request

        # status code 200 OK
        self.assertEqual(response.status_code, 200)

        # check template used
        self.assertTemplateUsed(response, 'auth/register.html')

        # check form is in context
        self.assertIn('form', response.context)

        # optionally, check form is empty (unbound)
        form = response.context['form']
        self.assertFalse(form.is_bound)

    def test_post_invalid_signup_shows_error(self):
        """Test invalid form returns error message and re-renders form."""
        data = {
            'username': 'baduser',
            'password1': 'abc',  # invalid password (too short / not matching)
            'password2': 'xyz',
        }

        response = self.client.post(self.url, data, follow=True)
        form = response.context.get('form')
        # Form should be re-rendered with errors
        self.assertIsNotNone(form)
        self.assertIn('password2', form.errors)
        self.assertIn("The two password fields didn’t match.", form.errors['password2'])

        # Error message should appear
        messages = list(response.context['messages'])
        self.assertTrue(any("Please correct the errors" in str(m) for m in messages))
