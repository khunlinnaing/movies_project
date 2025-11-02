from django.test import TestCase
from django.contrib.auth.models import User
from project.collectForms.signup_forms import SignupForm
from project.models import UserInfo
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

def get_test_image_file(name='test.png'):
    """Create a simple in-memory PNG image"""
    img = Image.new('RGB', (100, 100), color='red')
    byte_arr = BytesIO()
    img.save(byte_arr, format='PNG')
    byte_arr.seek(0)
    return SimpleUploadedFile(name, byte_arr.read(), content_type='image/png')


class SignupFormTest(TestCase):
    def setUp(self):
        # Existing user to test unique email validation
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='StrongPass123'
        )

    def test_valid_signup_form_creates_user_and_userinfo(self):
        """Form with valid data should create User and linked UserInfo."""
        image = get_test_image_file()

        form_data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'newuser@example.com',
            'phone': '123456789',
            'address': '123 Main Street',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form_files = {'profile': image}

        form = SignupForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'newuser@example.com')

        # Check UserInfo
        userinfo = UserInfo.objects.get(user=user)
        self.assertEqual(userinfo.phone, '123456789')
        self.assertEqual(userinfo.address, '123 Main Street')
        self.assertTrue(userinfo.profile.name.endswith('test.png'))

    def test_email_must_be_unique(self):
        """Form should raise validation error if email already exists."""
        form_data = {
            'username': 'anotheruser',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'existing@example.com',  # duplicate email
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(
            form.errors['email'][0],
            "A user with this email already exists."
        )

    def test_password_mismatch(self):
        """Form should be invalid if passwords do not match."""
        form_data = {
            'username': 'user123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'user123@example.com',
            'password1': 'StrongPass123',
            'password2': 'WrongPass123',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_optional_fields_can_be_blank(self):
        """Phone, address, and profile can be left blank."""
        form_data = {
            'username': 'optionaluser',
            'first_name': 'Opt',
            'last_name': 'User',
            'email': 'optional@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        userinfo = UserInfo.objects.get(user=user)
        self.assertEqual(userinfo.phone, '')        # blank CharField returns ''
        self.assertEqual(userinfo.address, '')      # blank CharField returns ''
        self.assertFalse(userinfo.profile)          # blank ImageField evaluates False
