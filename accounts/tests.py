from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


class AuthenticationFlowTests(TestCase):
    password = "A-secure-test-password-123"

    def create_user(self, email, role, **extra_fields):
        return User.objects.create_user(
            email=email,
            password=self.password,
            role=role,
            **extra_fields,
        )

    def test_admin_login_redirects_to_admin_dashboard(self):
        self.create_user("admin@example.com", "admin")

        response = self.client.post(
            reverse("login"),
            {"email": "admin@example.com", "password": self.password},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:admin_dashboard"))
        self.assertContains(response, "You have been logged in successfully.")

    def test_employee_login_redirects_to_employee_dashboard(self):
        self.create_user("employee@example.com", "employee")

        response = self.client.post(
            reverse("login"),
            {"email": "employee@example.com", "password": self.password},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:employee_dashboard"))
        self.assertContains(response, "You have been logged in successfully.")

    def test_employee_login_replaces_existing_admin_session(self):
        admin = self.create_user("admin@example.com", "admin")
        self.create_user("employee@example.com", "employee")
        self.client.force_login(admin)

        response = self.client.post(
            reverse("login"),
            {"email": "employee@example.com", "password": self.password},
        )

        self.assertRedirects(response, reverse("dashboard:employee_dashboard"))
        self.assertEqual(
            self.client.session["_auth_user_id"],
            str(User.objects.get(email="employee@example.com").pk),
        )

    def test_authenticated_user_can_open_login_form_to_switch_accounts(self):
        admin = self.create_user("admin@example.com", "admin")
        self.client.force_login(admin)

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome Back!")

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            reverse("login"),
            {"email": "missing@example.com", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email address or password.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_cannot_log_in(self):
        self.create_user("inactive@example.com", "employee", is_active=False)

        response = self.client.post(
            reverse("login"),
            {"email": "inactive@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email address or password.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_role_without_dashboard_is_not_logged_in(self):
        self.create_user("manager@example.com", "manager")

        response = self.client.post(
            reverse("login"),
            {"email": "manager@example.com", "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "does not have access to a dashboard")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_views_enforce_roles(self):
        admin = self.create_user("admin@example.com", "admin")
        self.client.force_login(admin)

        self.assertEqual(
            self.client.get(reverse("dashboard:admin_dashboard")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("dashboard:employee_dashboard")).status_code,
            403,
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard:employee_dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard:employee_dashboard')}",
        )

    def test_logout_requires_post_and_clears_session(self):
        employee = self.create_user("employee@example.com", "employee")
        self.client.force_login(employee)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

        response = self.client.post(reverse("logout"), follow=True)

        self.assertRedirects(response, reverse("login"))
        self.assertContains(response, "You have been logged out successfully.")
        self.assertNotIn("_auth_user_id", self.client.session)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_password_reset_sends_link_for_active_user(self):
        self.create_user("employee@example.com", "employee")

        response = self.client.post(
            reverse("password_reset"),
            {"email": "employee@example.com"},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_password_reset_does_not_reveal_unknown_email(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "missing@example.com"},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)
