__all__ = ("create_pdf", "get_file")
import secrets

import django.contrib.auth.models
import django.db
from django.template.loader import render_to_string
import pandas

import users.models


def create_student(*args, group_id=0):
    while True:
        try:
            token = (
                f"{group_id:04d}-{ord(args[0][0].lower()) - ord('а')}"
                f"{secrets.token_hex(3)}"
            )
            user = django.contrib.auth.models.User.objects.create_user(
                username=token,
                password=token,
                first_name=args[1],
                last_name=args[0],
            )
            middle_name = "-"
            if len(args) == 3:
                middle_name = args[2]

            users.models.ProfileStudent.objects.create(
                user=user,
                middle_name=middle_name,
            )
            group, created = django.contrib.auth.models.Group.objects.get_or_create(
                id=group_id,
            )
            user.groups.add(group)
            break
        except django.db.IntegrityError:
            pass


def read_file(file_path, delimiter=","):
    if file_path.endswith((".xls", ".xlsx")):
        return pandas.read_excel(file_path)

    if file_path.endswith(".ods"):
        return pandas.read_excel(file_path, engine="odf")

    if file_path.endswith(".csv"):
        return pandas.read_csv(file_path, delimiter=delimiter)

    raise ValueError("Unsupported file format")


def get_file(file_path, group_name=None, delimiter=","):
    file = read_file(file_path, delimiter=delimiter)
    if len(file.lines) >= 200 or len(file.columns) >= 30:
        raise ValueError("Привышен лимит учеников")

    fio_columns = [col for col in file.columns if "фио" in col.lower()]
    if fio_columns:
        for fio in file[fio_columns[0]].tolist():
            if len(fio.split()) not in [2, 3]:
                raise ValueError("Не все ФИО соответствуют стандарту")

        group_obj, created = django.contrib.auth.models.Group.objects.get_or_create(
            name=group_name,
        )
        group_id = group_obj.id
        for fio in file[fio_columns[0]].tolist():
            if len(fio_list := fio.split()) not in [2, 3]:
                raise ValueError("Не все ФИО соответствуют стандарту")

            create_student(*fio_list, group_id=group_id)
    else:
        surname_col = None
        name_col = None
        middle_col = None

        for col in file.columns:
            if "фамилия" in col.lower():
                surname_col = col
                break

        for col in file.columns:
            if "имя" in col.lower():
                name_col = col
                break

        for col in file.columns:
            if "отчество" in col.lower():
                middle_col = col
                break

        if surname_col and name_col and middle_col:
            group_obj, created = django.contrib.auth.models.Group.objects.get_or_create(
                name=group_name,
            )
            group_id = group_obj.id
            for _, row in file.iterrows():
                last_name = str(row[surname_col]).strip()
                first_name = str(row[name_col]).strip()
                middle_name = str(row[middle_col]).strip()
                create_student(
                    last_name,
                    first_name,
                    middle_name,
                    group_id=group_id,
                )


def create_pdf(group_name):
    group = django.contrib.auth.models.Group.objects.get(name=group_name)
    users = group.user_set.all()
    return render_to_string(
        "pdf/group_codes.html",
        {
            "group": group,
            "users": users,
        },
    )
