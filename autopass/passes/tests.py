__all__ = ()

import os
import tempfile
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from passes.models import Pass


class GroupsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.group1 = Group.objects.create(name="security")
        self.group2 = Group.objects.create(name="admin")

    def test_groups_view_lists_all_groups(self):
        response = self.client.get(reverse("passes:groups"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("groups", response.context)
        self.assertEqual(len(response.context["groups"]), 2)


class DownloadAllGroupPassesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(name="security")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.user.groups.add(self.group)

    @patch("card_maker.card_maker.ImageEditor")
    @patch("shutil.make_archive")
    def test_download_all_group_passes(self, mock_archive, mock_editor):
        mock_instance = MagicMock()
        mock_editor.return_value = mock_instance

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            Pass.objects.create(
                user=self.user,
                status="Verify",
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
