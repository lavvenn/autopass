__all__ = []
import os
import tempfile

import django.contrib.auth.models as auth_models
import django.shortcuts
import django.test

import users.models


class SignUpViewTests(django.test.TestCase):
    def test_get_returns_200(self):
        response = django.test.Client().get(django.shortcuts.reverse("users:signup"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_creates_user(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        django.test.Client().post(
            django.shortcuts.reverse("users:signup"),
            data,
        )
        self.assertEqual(
            auth_models.User.objects.filter(username="testuser").count(),
            1,
        )


class ActivateUserViewTests(django.test.TestCase):
    def setUp(self):
        self.user = auth_models.User.objects.create_user(
            username="testuser",
            password="testpass123",
            is_active=False,
        )
        users.models.Profile.objects.create(user=self.user, role="куратор")

    def test_get_returns_404_for_invalid_user(self):
        response = django.test.Client().get(
            django.shortcuts.reverse(
                "users:activate",
                kwargs={"username": "nonexistent"},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_get_activates_user_within_12_hours(self):
        django.test.Client().get(
            django.shortcuts.reverse("users:activate", kwargs={"username": "testuser"}),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class UploadAvatarPageViewTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.student_user = auth_models.User.objects.create_user(
            username="student",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.student_user,
            role="ученик",
            middle_name="",
        )

    def test_get_returns_200_for_student(self):
        self.client.login(username="student", password="testpass123")
        response = self.client.get(django.shortcuts.reverse("users:profile"))
        self.assertEqual(response.status_code, 200)

    def test_get_returns_404_for_curator(self):
        curator_user = auth_models.User.objects.create_user(
            username="curator",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=curator_user,
            role="куратор",
            middle_name="",
        )
        self.client.login(username="curator", password="testpass123")
        response = self.client.get(django.shortcuts.reverse("users:profile"))
        self.assertEqual(response.status_code, 404)


class UploadAvatarApiViewTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.student_user = auth_models.User.objects.create_user(
            username="student",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.student_user,
            role="ученик",
            middle_name="",
        )

    def test_post_returns_404_for_curator(self):
        curator_user = auth_models.User.objects.create_user(
            username="curator",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=curator_user,
            role="куратор",
            middle_name="",
        )
        self.client.login(username="curator", password="testpass123")
        response = self.client.post(django.shortcuts.reverse("users:upload-avatar-api"))
        self.assertEqual(response.status_code, 404)

    def test_post_returns_400_without_file(self):
        self.client.login(username="student", password="testpass123")
        response = self.client.post(django.shortcuts.reverse("users:upload-avatar-api"))
        self.assertEqual(response.status_code, 400)


class UploadStudentsViewTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.curator_user = auth_models.User.objects.create_user(
            username="curator",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.curator_user,
            role="куратор",
            middle_name="",
        )

    def test_get_returns_200_for_curator(self):
        self.client.login(username="curator", password="testpass123")
        response = self.client.get(django.shortcuts.reverse("users:upload-students"))
        self.assertEqual(response.status_code, 200)

    def test_post_redirects_on_success(self):
        self.client.login(username="curator", password="testpass123")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("ФИО\nИванов Иван Иванович")
            temp_path = f.name

        try:
            with open(temp_path, "rb") as file:
                response = self.client.post(
                    django.shortcuts.reverse("users:upload-students"),
                    {"group_name": "TestGroup", "file": file, "delimiter": ","},
                )

            self.assertEqual(response.status_code, 200)
        finally:
            os.unlink(temp_path)


class UploadResultViewTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.curator_user = auth_models.User.objects.create_user(
            username="curator",
            password="testpass123",
        )
        self.group = auth_models.Group.objects.create(name="TestGroup")
        users.models.Profile.objects.create(
            user=self.curator_user,
            role="куратор",
            middle_name="",
        )
        users.models.GroupLeader.objects.create(
            group=self.group,
            curator=self.curator_user,
        )

    def test_get_returns_200_for_group_leader(self):
        self.client.login(username="curator", password="testpass123")
        response = self.client.get(
            django.shortcuts.reverse(
                "users:upload-result",
                kwargs={"group_name": "TestGroup"},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_get_returns_404_for_non_leader(self):
        other_curator = auth_models.User.objects.create_user(
            username="other",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=other_curator,
            role="куратор",
            middle_name="",
        )
        self.client.login(username="other", password="testpass123")
        response = self.client.get(
            django.shortcuts.reverse(
                "users:upload-result",
                kwargs={"group_name": "TestGroup"},
            ),
        )
        self.assertEqual(response.status_code, 404)


class ResetStudentsViewTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.curator_user = auth_models.User.objects.create_user(
            username="curator",
            password="testpass123",
        )
        self.student_user = auth_models.User.objects.create_user(
            username="0001-a0b1c2",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.curator_user,
            role="куратор",
            middle_name="",
        )
        users.models.Profile.objects.create(
            user=self.student_user,
            role="ученик",
            middle_name="Иванович",
        )
        self.group = auth_models.Group.objects.create(name="TestGroup")
        users.models.GroupLeader.objects.create(
            group=self.group,
            curator=self.curator_user,
        )
        self.student_user.groups.add(self.group)

    def test_get_returns_200_for_curator(self):
        self.client.login(username="curator", password="testpass123")
        response = self.client.get(django.shortcuts.reverse("users:reset"))
        self.assertEqual(response.status_code, 200)

    def test_post_resets_student_token(self):
        self.client.login(username="curator", password="testpass123")
        self.client.post(
            django.shortcuts.reverse("users:reset"),
            {"token": "0001-a0b1c2"},
        )
        self.assertEqual(
            auth_models.User.objects.filter(username="0001-a0b1c2").count(),
            0,
        )
