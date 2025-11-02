from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from project.models import Category
from project.collectForms.categories_forms import CategoryForm

class CategoryViewPermissionTest(TestCase):

    def setUp(self):
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass'
        )
        # Sample category
        self.category = Category.objects.create(name='Sample Category')

        # Create sample categories for pagination test (25 items)
        for i in range(25):
            Category.objects.create(name=f"Category {i+1}")

        # URL for category view
        self.url = reverse('website:category-view')

        # Login URL for redirect checks
        self.login_url = reverse('website:login-view-get')
        

        # URLs
        self.create_url = reverse('website:create-category-view')
        self.edit_url = reverse('website:edit-category-view', kwargs={'pk': self.category.pk})
        self.delete_url = reverse('website:delete-category-view', kwargs={'pk': self.category.pk})
        self.list_url = reverse('website:category-view')
        

    def test_superuser_can_access_category_view(self):
        """Superuser can access category view and see paginated categories."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/category/lists.html')
        self.assertIn('category_objects', response.context)

        page_obj = response.context['category_objects']
        self.assertTrue(hasattr(page_obj, 'object_list'))
        self.assertEqual(len(page_obj.object_list), 10)  # 10 per page
        self.assertEqual(page_obj.paginator.num_pages, 3)  # 25 items → 3 pages

    def test_regular_user_cannot_access_category_view(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))


    def test_superuser_second_page_pagination(self):
        """Superuser can access second page with correct pagination."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.url, {'page': 2})
        self.assertEqual(response.status_code, 200)

        page_obj = response.context['category_objects']
        self.assertEqual(page_obj.number, 2)
        self.assertEqual(len(page_obj.object_list), 10)

    def test_superuser_last_page_pagination(self):
        """Superuser can access last page with remaining items."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.url, {'page': 3})
        self.assertEqual(response.status_code, 200)

        page_obj = response.context['category_objects']
        self.assertEqual(page_obj.number, 3)
        self.assertEqual(len(page_obj.object_list), 6)  # remaining items


    # ----------------- Create Category Tests -----------------
    def test_superuser_can_create_category(self):
        self.client.login(username='admin', password='adminpass')
        data = {'name': 'New Category'}
        response = self.client.post(self.create_url, data, follow=True)

        # Check redirect
        self.assertRedirects(response, self.list_url)

        # Check success message
        messages = list(response.context['messages'])
        self.assertTrue(any('Create category is success' in str(m) for m in messages))

        # Check category exists
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_superuser_get_create_category_form(self):
        """Superuser GET request renders the empty category form."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/category/add.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CategoryForm)

    def test_regular_user_cannot_create_category(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # redirect to login

    def test_anonymous_user_redirected_on_create(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))




class EditCategoryViewTest(TestCase):

    def setUp(self):
        # Superuser
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        # Regular user
        self.regular_user = User.objects.create_user(
            username='user', email='user@example.com', password='userpass'
        )
        # Sample category
        self.category = Category.objects.create(name='Sample Category')

        # URLs
        self.edit_url = reverse('website:edit-category-view', kwargs={'pk': self.category.pk})
        self.invalid_url = reverse('website:edit-category-view', kwargs={'pk': 999})  # non-existent

    # ----------------- GET request -----------------
    def test_superuser_get_edit_category_form(self):
        """GET renders form with instance for superuser."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/category/edit.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CategoryForm)
        self.assertEqual(response.context['form'].instance, self.category)

    # ----------------- POST valid -----------------
    def test_superuser_post_valid_edit(self):
        """POST valid data updates category, redirects, and shows message."""
        self.client.login(username='admin', password='adminpass')
        data = {'name': 'Updated Category'}
        response = self.client.post(self.edit_url, data, follow=True)

        self.assertRedirects(response, reverse('website:category-view'))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Update is success' in str(m) for m in messages))

    # ----------------- POST invalid -----------------
    def test_superuser_post_invalid_edit(self):
        """POST invalid data re-renders form with errors."""
        self.client.login(username='admin', password='adminpass')
        data = {'name': ''}  # invalid
        response = self.client.post(self.edit_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/category/edit.html')
        form = response.context['form']
        self.assertIsInstance(form, CategoryForm)
        self.assertTrue(form.errors)

    # ----------------- Category does not exist -----------------
    def test_edit_nonexistent_category(self):
        """Editing non-existent category shows error and redirects."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.invalid_url, {'name': 'Test'}, follow=True)

        self.assertRedirects(response, reverse('website:category-view'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Category id is not found.' in str(m) for m in messages))

    # ----------------- Exception handling -----------------
    def test_edit_category_exception(self):
        """Simulate general exception in edit view."""
        self.client.login(username='admin', password='adminpass')

        # Monkeypatch Category.objects.get to raise Exception
        original_get = Category.objects.get
        Category.objects.get = lambda *args, **kwargs: 1/0  # force exception

        response = self.client.post(self.edit_url, {'name': 'Test'}, follow=True)
        self.assertRedirects(response, reverse('website:category-view'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Server error' in str(m) for m in messages))

        # Restore original method
        Category.objects.get = original_get

    # ----------------- Permission tests -----------------
    def test_regular_user_cannot_access_edit(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        from django.conf import settings
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_anonymous_user_redirected_on_edit(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        from django.conf import settings
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))




class DeleteCategoryViewTest(TestCase):

    def setUp(self):
        # Superuser
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        # Regular user
        self.regular_user = User.objects.create_user(
            username='user', email='user@example.com', password='userpass'
        )
        # Sample category
        self.category = Category.objects.create(name='Sample Category')

        # URLs
        self.delete_url = reverse('website:delete-category-view', kwargs={'pk': self.category.pk})
        self.invalid_delete_url = reverse('website:delete-category-view', kwargs={'pk': 999})

    # ----------------- Superuser delete -----------------
    def test_superuser_can_delete_category(self):
        """Superuser can delete category successfully."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.delete_url, follow=True)

        self.assertRedirects(response, reverse('website:category-view'))
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Delete is success' in str(m) for m in messages))

    # ----------------- Category does not exist -----------------
    def test_delete_nonexistent_category(self):
        """Deleting a non-existent category shows error message."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.invalid_delete_url, follow=True)

        self.assertRedirects(response, reverse('website:category-view'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Server error' in str(m) or 'Category id is not found.' in str(m) for m in messages))
    
    # ----------------- Permission tests -----------------
    def test_regular_user_cannot_delete_category(self):
        """Regular user cannot delete category and is redirected."""
        self.client.login(username='user', password='userpass')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        from django.conf import settings
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_anonymous_user_redirected_on_delete(self):
        """Anonymous users are redirected to login."""
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        from django.conf import settings
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    # ----------------- Exception handling -----------------
    def test_delete_category_exception(self):
        """Simulate general exception and check server error message."""
        self.client.login(username='admin', password='adminpass')

        # Monkeypatch Category.objects.get to raise Exception
        original_get = Category.objects.get
        Category.objects.get = lambda *args, **kwargs: 1/0  # force exception

        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, reverse('website:category-view'))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Server error' in str(m) for m in messages))

        # Restore original method
        Category.objects.get = original_get

