from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, Feedback, Show


class ShowModelTests(TestCase):
    def test_slug_is_auto_generated(self):
        show = Show.objects.create(
            title="Test Show", description="A show for testing.", poster_url="https://example.com/p.jpg"
        )
        self.assertEqual(show.slug, "test-show")

    def test_cast_list_splits_on_comma(self):
        show = Show.objects.create(
            title="Cast Test",
            description="desc",
            poster_url="https://example.com/p.jpg",
            cast="Alice, Bob,  Carol",
        )
        self.assertEqual(show.cast_list, ["Alice", "Bob", "Carol"])


class PageLoadTests(TestCase):
    def setUp(self):
        Show.objects.create(
            title="Sample Show",
            description="desc",
            poster_url="https://example.com/p.jpg",
            trending=True,
            featured=True,
            top10_rank=1,
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sample Show")

    def test_home_page_loads_with_empty_catalog(self):
        Show.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_static_pages_load(self):
        for name in ["about", "contact", "form", "register", "login", "my_list"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f"{name} did not return 200")


class ContactFormTests(TestCase):
    def test_valid_submission_creates_message(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "phone": "",
                "subject": "General Inquiry",
                "message": "Hello there",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_missing_fields_does_not_create_message(self):
        response = self.client.post(reverse("contact"), {"name": "", "email": "", "subject": "", "message": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)


class FeedbackFormTests(TestCase):
    def test_valid_submission_creates_feedback(self):
        response = self.client.post(
            reverse("form"),
            {
                "fullName": "Test User",
                "email": "test@example.com",
                "feedbackType": "suggestion",
                "rating": "4",
                "category": "User Interface",
                "message": "Looks great",
                "consent": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Feedback.objects.count(), 1)


class RegisterViewTests(TestCase):
    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane@example.com",
                "phone": "",
                "password": "SuperSecret123",
                "confirmPassword": "SuperSecret123",
                "gender": "female",
                "month": "",
                "day": "",
                "year": "",
                "country": "India",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="jane@example.com").first()
        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, "profile"))

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "jane2@example.com",
                "password": "SuperSecret123",
                "confirmPassword": "DifferentPass123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="jane2@example.com").exists())


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user@example.com", password="TestPass123")

    def test_valid_login_redirects_home(self):
        response = self.client.post(
            reverse("login"), {"username": "user@example.com", "password": "TestPass123"}
        )
        self.assertRedirects(response, reverse("home"))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("login"), {"username": "user@example.com", "password": "WrongPass"}
        )
        self.assertEqual(response.status_code, 200)
