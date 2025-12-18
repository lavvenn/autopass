"""Тесты для синхронизации групп через users"""

import django.contrib.auth.models
import django.test

import organizations.models
import users.models
import users.utils


class UserGroupSyncTestCase(django.test.TestCase):
    """Тесты синхронизации групп через users"""

    def setUp(self):
        """Создание тестовых данных"""
        self.curator = django.contrib.auth.models.User.objects.create_user(
            username="curator1",
            email="curator1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.curator,
            role="куратор",
            middle_name="Тестович",
        )

    def test_create_student_adds_to_group(self):
        """Тест: создание студента добавляет его в группу"""
        # Создаем группу через organizations
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
        )

        # Создаем студента через utils
        token = users.utils.create_student(
            "Иванов",
            "Иван",
            "Иванович",
            group_id=group.auth_group.id,
        )

        # Проверяем, что студент создан и добавлен в группу
        student = django.contrib.auth.models.User.objects.get(username=token)
        self.assertIn(group.auth_group, student.groups.all())
        self.assertEqual(student.profile.role, "ученик")
        self.assertEqual(student.first_name, "Иван")
        self.assertEqual(student.last_name, "Иванов")
        self.assertEqual(student.profile.middle_name, "Иванович")

    def test_group_leader_creates_org_group(self):
        """Тест: создание GroupLeader создает organizations.models.Group"""
        # Создаем Django auth Group напрямую
        auth_group = django.contrib.auth.models.Group.objects.create(
            name="Новая группа",
        )

        # Создаем GroupLeader
        group_leader = users.models.GroupLeader.objects.create(
            group=auth_group,
            curator=self.curator,
        )

        # Проверяем, что organizations.models.Group создан
        self.assertTrue(
            organizations.models.Group.objects.filter(
                auth_group=auth_group,
            ).exists(),
        )

        org_group = organizations.models.Group.objects.get(auth_group=auth_group)
        self.assertEqual(org_group.name, "Новая группа")
        self.assertEqual(org_group.curator, self.curator)
        self.assertEqual(org_group.course, 1)

    def test_group_leader_updates_existing_org_group(self):
        """Тест: GroupLeader обновляет существующий organizations.models.Group"""
        # Создаем organizations.models.Group без auth_group
        org_group = organizations.models.Group.objects.create(
            name="Существующая группа",
            curator=self.curator,
        )

        # Создаем Django auth Group с таким же именем
        auth_group = django.contrib.auth.models.Group.objects.create(
            name="Существующая группа",
        )

        # Создаем GroupLeader
        users.models.GroupLeader.objects.create(
            group=auth_group,
            curator=self.curator,
        )

        # Проверяем, что organizations.models.Group связан
        org_group.refresh_from_db()
        self.assertEqual(org_group.auth_group, auth_group)

    def test_multiple_students_in_group(self):
        """Тест: несколько студентов в одной группе"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
        )

        # Создаем нескольких студентов
        token1 = users.utils.create_student(
            "Иванов",
            "Иван",
            "Иванович",
            group_id=group.auth_group.id,
        )
        token2 = users.utils.create_student(
            "Петров",
            "Петр",
            "Петрович",
            group_id=group.auth_group.id,
        )
        token3 = users.utils.create_student(
            "Сидоров",
            "Сидор",
            group_id=group.auth_group.id,
        )

        # Проверяем, что все студенты в группе
        students = group.students
        self.assertEqual(students.count(), 3)

        student_usernames = [s.user.username for s in students]
        self.assertIn(token1, student_usernames)
        self.assertIn(token2, student_usernames)
        self.assertIn(token3, student_usernames)

    def test_student_token_format(self):
        """Тест: формат токена студента"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
        )

        token = users.utils.create_student(
            "Иванов",
            "Иван",
            "Иванович",
            group_id=group.auth_group.id,
        )

        # Токен должен быть в формате: {group_id:04d}-{первая буква фамилии}{hex}
        self.assertTrue(token.startswith(f"{group.auth_group.id:04d}-"))
        # Первая буква фамилии "И" должна быть преобразована
        self.assertIn("-", token)


class ProfileTestCase(django.test.TestCase):
    """Тесты для Profile"""

    def setUp(self):
        """Создание тестовых данных"""
        self.user = django.contrib.auth.models.User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123",
        )

    def test_create_profile(self):
        """Тест: создание профиля"""
        profile = users.models.Profile.objects.create(
            user=self.user,
            role="ученик",
            middle_name="Тестович",
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, "ученик")
        self.assertEqual(profile.middle_name, "Тестович")
        self.assertEqual(profile.attempts_count, 0)
        self.assertIsNone(profile.attempts_time)

    def test_profile_one_to_one_with_user(self):
        """Тест: Profile имеет OneToOne связь с User"""
        profile = users.models.Profile.objects.create(
            user=self.user,
            role="ученик",
            middle_name="Тестович",
        )

        # Проверяем обратную связь
        self.assertEqual(self.user.profile, profile)


class GroupLeaderTestCase(django.test.TestCase):
    """Тесты для GroupLeader"""

    def setUp(self):
        """Создание тестовых данных"""
        self.curator = django.contrib.auth.models.User.objects.create_user(
            username="curator1",
            email="curator1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.curator,
            role="куратор",
            middle_name="Тестович",
        )

        self.auth_group = django.contrib.auth.models.Group.objects.create(
            name="Группа 1",
        )

    def test_create_group_leader(self):
        """Тест: создание GroupLeader"""
        group_leader = users.models.GroupLeader.objects.create(
            group=self.auth_group,
            curator=self.curator,
        )

        self.assertEqual(group_leader.group, self.auth_group)
        self.assertEqual(group_leader.curator, self.curator)
        self.assertIsNotNone(group_leader.created_at)

    def test_group_leader_one_to_one_with_group(self):
        """Тест: GroupLeader имеет OneToOne связь с Group"""
        group_leader = users.models.GroupLeader.objects.create(
            group=self.auth_group,
            curator=self.curator,
        )

        # Проверяем обратную связь
        self.assertEqual(self.auth_group.leader, group_leader)

    def test_group_leader_related_name(self):
        """Тест: related_name для GroupLeader"""
        group_leader = users.models.GroupLeader.objects.create(
            group=self.auth_group,
            curator=self.curator,
        )

        # Проверяем, что куратор может получить свои группы через led_groups
        self.assertIn(group_leader, self.curator.led_groups.all())

