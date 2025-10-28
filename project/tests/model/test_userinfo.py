from django.test import TestCase
from django.contrib.auth.models import User
from project.models import UserInfo   # Change 'project' to your app name


class UserInfoModelAndSignalTest(TestCase):
    def setUp(self):
        # Create a new user (signal auto-creates UserInfo)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='12345'
        )

    def test_userinfo_auto_created(self):
        """Test that UserInfo is automatically created when User is created"""
        self.assertTrue(hasattr(self.user, 'info'))
        self.assertIsInstance(self.user.info, UserInfo)
        self.assertEqual(self.user.info.user, self.user)

    def test_userinfo_str_method(self):
        """Test __str__ method of UserInfo"""
        self.assertEqual(str(self.user.info), "testuser's Info")

    def test_userinfo_not_duplicated_on_save(self):
        """Test that saving the same user again does not create duplicate UserInfo"""
        count_before = UserInfo.objects.count()
        self.user.first_name = 'Updated'
        self.user.save()  # Trigger signal
        count_after = UserInfo.objects.count()
        self.assertEqual(count_before, count_after)

    def test_userinfo_recreated_if_deleted(self):
        """Test the except UserInfo.DoesNotExist block in the signal"""
        # Delete the UserInfo to simulate missing profile
        self.user.info.delete()
        self.assertFalse(UserInfo.objects.filter(user=self.user).exists())

        # Save the user again → signal should recreate UserInfo
        self.user.save()

        recreated_info = UserInfo.objects.filter(user=self.user).first()
        self.assertIsNotNone(recreated_info)
        self.assertEqual(recreated_info.user, self.user)

    def test_userinfo_update_fields(self):
        """Test updating fields of UserInfo"""
        info = self.user.info
        info.phone = '09123456789'
        info.address = 'Yangon, Myanmar'
        info.save()

        updated_info = UserInfo.objects.get(user=self.user)
        self.assertEqual(updated_info.phone, '09123456789')
        self.assertEqual(updated_info.address, 'Yangon, Myanmar')
