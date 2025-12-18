"""Тесты для синхронизации групп и организаций"""

import datetime

import django.contrib.auth.models
import django.test
import django.utils.timezone

import organizations.models
import users.models


class GroupSyncTestCase(django.test.TestCase):
    """Тесты синхронизации групп"""

    def setUp(self):
        """Создание тестовых данных"""
        # Создаем куратора
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

        # Создаем администратора
        self.admin = django.contrib.auth.models.User.objects.create_user(
            username="admin1",
            email="admin1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.admin,
            role="administrator",
            middle_name="Админович",
        )

        # Создаем учебное заведение
        self.institution = organizations.models.Institution.objects.create(
            name="Тестовое учебное заведение",
            short_name="ТУЗ",
            information="Описание тестового заведения",
            admin=self.admin,
        )

    def test_create_group_syncs_auth_group(self):
        """Тест: создание organizations.models.Group синхронизирует Django auth Group"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
            course=1,
        )

        # Проверяем, что Django auth Group создан
        self.assertIsNotNone(group.auth_group)
        self.assertEqual(group.auth_group.name, "Группа 1")

        # Проверяем, что GroupLeader создан
        self.assertTrue(
            users.models.GroupLeader.objects.filter(
                group=group.auth_group,
                curator=self.curator,
            ).exists(),
        )

    def test_update_group_name_syncs_auth_group(self):
        """Тест: обновление названия группы синхронизирует Django auth Group"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
        )

        original_auth_group = group.auth_group

        # Обновляем название
        group.name = "Группа 2"
        group.save()

        # Проверяем, что auth_group обновлен
        original_auth_group.refresh_from_db()
        self.assertEqual(original_auth_group.name, "Группа 2")
        self.assertEqual(group.auth_group.id, original_auth_group.id)

    def test_update_group_curator_syncs_group_leader(self):
        """Тест: обновление куратора синхронизирует GroupLeader"""
        # Создаем второго куратора
        curator2 = django.contrib.auth.models.User.objects.create_user(
            username="curator2",
            email="curator2@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=curator2,
            role="куратор",
            middle_name="Второй",
        )

        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
        )

        # Обновляем куратора
        group.curator = curator2
        group.save()

        # Проверяем, что GroupLeader обновлен
        group_leader = users.models.GroupLeader.objects.get(
            group=group.auth_group,
        )
        self.assertEqual(group_leader.curator, curator2)

    def test_delete_group_deletes_auth_group(self):
        """Тест: удаление группы удаляет связанный Django auth Group"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
        )

        auth_group_id = group.auth_group.id

        # Удаляем группу
        group.delete()

        # Проверяем, что Django auth Group удален
        self.assertFalse(
            django.contrib.auth.models.Group.objects.filter(
                id=auth_group_id,
            ).exists(),
        )

        # Проверяем, что GroupLeader удален
        self.assertFalse(
            users.models.GroupLeader.objects.filter(
                group_id=auth_group_id,
            ).exists(),
        )

    def test_group_students_property(self):
        """Тест: свойство students возвращает студентов группы"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
        )

        # Создаем студентов
        student1 = django.contrib.auth.models.User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="testpass123",
            first_name="Иван",
            last_name="Иванов",
        )
        users.models.Profile.objects.create(
            user=student1,
            role="ученик",
            middle_name="Иванович",
        )
        student1.groups.add(group.auth_group)

        student2 = django.contrib.auth.models.User.objects.create_user(
            username="student2",
            email="student2@test.com",
            password="testpass123",
            first_name="Петр",
            last_name="Петров",
        )
        users.models.Profile.objects.create(
            user=student2,
            role="ученик",
            middle_name="Петрович",
        )
        student2.groups.add(group.auth_group)

        # Создаем не-студента (куратора в группе)
        self.curator.groups.add(group.auth_group)

        # Проверяем свойство students
        students = list(group.students)
        self.assertEqual(len(students), 2)
        student_profiles = [s.user for s in students]
        self.assertIn(student1, student_profiles)
        self.assertIn(student2, student_profiles)
        self.assertNotIn(self.curator, student_profiles)

    def test_group_students_empty_when_no_auth_group(self):
        """Тест: свойство students возвращает пустой queryset если нет auth_group"""
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
        )
        # Удаляем auth_group вручную (не должно происходить в реальности)
        group.auth_group = None
        group.save()

        students = list(group.students)
        self.assertEqual(len(students), 0)


class GroupLeaderSyncTestCase(django.test.TestCase):
    """Тесты синхронизации через GroupLeader"""

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

    def test_create_group_leader_syncs_org_group(self):
        """Тест: создание GroupLeader синхронизирует organizations.models.Group"""
        # Создаем Django auth Group напрямую
        auth_group = django.contrib.auth.models.Group.objects.create(
            name="Группа из GroupLeader",
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
        self.assertEqual(org_group.name, "Группа из GroupLeader")
        self.assertEqual(org_group.curator, self.curator)

    def test_create_group_leader_updates_existing_org_group(self):
        """Тест: создание GroupLeader обновляет существующий organizations.models.Group"""
        # Создаем organizations.models.Group без auth_group
        org_group = organizations.models.Group.objects.create(
            name="Существующая группа",
            curator=self.curator,
        )

        # Создаем Django auth Group
        auth_group = django.contrib.auth.models.Group.objects.create(
            name="Существующая группа",
        )

        # Создаем GroupLeader
        users.models.GroupLeader.objects.create(
            group=auth_group,
            curator=self.curator,
        )

        # Проверяем, что organizations.models.Group связан с auth_group
        org_group.refresh_from_db()
        self.assertEqual(org_group.auth_group, auth_group)


class InstitutionTestCase(django.test.TestCase):
    """Тесты для учебных заведений"""

    def setUp(self):
        """Создание тестовых данных"""
        self.admin = django.contrib.auth.models.User.objects.create_user(
            username="admin1",
            email="admin1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.admin,
            role="administrator",
            middle_name="Админович",
        )

    def test_institution_str(self):
        """Тест: строковое представление Institution"""
        institution = organizations.models.Institution.objects.create(
            name="Тестовое учебное заведение",
            short_name="ТУЗ",
            information="Описание",
            admin=self.admin,
        )

        self.assertEqual(str(institution), "ТУЗ")

    def test_group_str_with_institution(self):
        """Тест: строковое представление Group с institution"""
        institution = organizations.models.Institution.objects.create(
            name="Тестовое учебное заведение",
            short_name="ТУЗ",
            information="Описание",
            admin=self.admin,
        )

        curator = django.contrib.auth.models.User.objects.create_user(
            username="curator1",
            email="curator1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=curator,
            role="куратор",
            middle_name="Тестович",
        )

        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=curator,
            institution=institution,
        )

        self.assertIn("Группа 1", str(group))
        self.assertIn("ТУЗ", str(group))

    def test_group_str_without_institution(self):
        """Тест: строковое представление Group без institution"""
        curator = django.contrib.auth.models.User.objects.create_user(
            username="curator1",
            email="curator1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=curator,
            role="куратор",
            middle_name="Тестович",
        )

        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=curator,
        )

        self.assertIn("Группа 1", str(group))
        self.assertIn("Без организации", str(group))


class IntegrationTestCase(django.test.TestCase):
    """Интеграционные тесты синхронизации"""

    def setUp(self):
        """Создание тестовых данных"""
        self.admin = django.contrib.auth.models.User.objects.create_user(
            username="admin1",
            email="admin1@test.com",
            password="testpass123",
        )
        users.models.Profile.objects.create(
            user=self.admin,
            role="administrator",
            middle_name="Админович",
        )

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

        self.institution = organizations.models.Institution.objects.create(
            name="Тестовое учебное заведение",
            short_name="ТУЗ",
            information="Описание",
            admin=self.admin,
        )

    def test_full_sync_workflow(self):
        """Тест: полный цикл синхронизации"""
        # 1. Создаем группу через organizations
        group = organizations.models.Group.objects.create(
            name="Группа 1",
            curator=self.curator,
            institution=self.institution,
            course=1,
        )

        # Проверяем синхронизацию
        self.assertIsNotNone(group.auth_group)
        self.assertTrue(
            users.models.GroupLeader.objects.filter(
                group=group.auth_group,
                curator=self.curator,
            ).exists(),
        )

        # 2. Добавляем студентов
        student = django.contrib.auth.models.User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="testpass123",
            first_name="Иван",
            last_name="Иванов",
        )
        users.models.Profile.objects.create(
            user=student,
            role="ученик",
            middle_name="Иванович",
        )
        student.groups.add(group.auth_group)

        # Проверяем доступность студентов через organizations Group
        self.assertEqual(group.students.count(), 1)
        self.assertEqual(group.students.first().user, student)

        # 3. Обновляем группу
        group.name = "Группа 2"
        group.save()

        # Проверяем синхронизацию названия
        group.auth_group.refresh_from_db()
        self.assertEqual(group.auth_group.name, "Группа 2")

        # 4. Удаляем группу
        auth_group_id = group.auth_group.id
        group.delete()

        # Проверяем каскадное удаление
        self.assertFalse(
            django.contrib.auth.models.Group.objects.filter(
                id=auth_group_id,
            ).exists(),
        )
        self.assertFalse(
            users.models.GroupLeader.objects.filter(
                group_id=auth_group_id,
            ).exists(),
        )

