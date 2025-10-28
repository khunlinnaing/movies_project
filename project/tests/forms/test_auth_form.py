from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase
from project.collectForms.login_form import LoginForm
class LoginFormTest(TestCase):
    """
    Tests for the custom LoginForm inherited from AuthenticationForm.
    """

    def setUp(self):
        # Instantiate the form for testing
        self.form = LoginForm()

    def test_form_inheritance(self):
        """Verify the form correctly inherits from AuthenticationForm."""
        self.assertTrue(issubclass(LoginForm, AuthenticationForm))

    def test_username_field_properties(self):
        """Test the customizations applied to the username field."""
        
        # 1. Check Field Type and Required Status
        username_field = self.form.fields['username']
        self.assertIsInstance(username_field, forms.CharField, "Username field should be CharField.")
        self.assertTrue(username_field.required, "Username field should be required.")
        
        # 2. Check Label and Widget
        self.assertEqual(username_field.label, "Account or Email", "Username label is incorrect.")
        self.assertIsInstance(username_field.widget, forms.TextInput, "Username widget should be TextInput.")

        # 3. Check Widget Attributes (CSS Class and Placeholder)
        widget_attrs = username_field.widget.attrs
        self.assertEqual(widget_attrs.get('class'), 'form-control', "Username widget missing 'form-control' class.")
        self.assertEqual(widget_attrs.get('placeholder'), 'Enter your Account or Email ', "Username widget placeholder is incorrect.")

    def test_password_field_properties(self):
        """Test the customizations applied to the password field."""
        
        # 1. Check Field Type and Required Status
        password_field = self.form.fields['password']
        self.assertIsInstance(password_field, forms.CharField, "Password field should be CharField.")
        self.assertTrue(password_field.required, "Password field should be required.")
        
        # 2. Check Label and Widget
        self.assertEqual(password_field.label, "Password", "Password label is incorrect.")
        self.assertIsInstance(password_field.widget, forms.PasswordInput, "Password widget should be PasswordInput.")

        # 3. Check Widget Attributes (CSS Class and Placeholder)
        widget_attrs = password_field.widget.attrs
        self.assertEqual(widget_attrs.get('class'), 'form-control', "Password widget missing 'form-control' class.")
        self.assertEqual(widget_attrs.get('placeholder'), 'Enter your password', "Password widget placeholder is incorrect.")
        
    def test_form_validation_missing_data(self):
        """Test form invalidity when required fields are missing."""
        
        # Empty data submission
        form = LoginForm(data={})
        self.assertFalse(form.is_valid(), "Form should be invalid when data is missing.")
        
        # Check specific errors (AuthenticationForm adds a specific error for missing fields)
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
