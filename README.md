# Auto pass

[![CI Status](https://github.com/lavvenn/autopass/workflows/django/badge.svg)](https://github.com/lavvenn/autopass/actions)


## description

A very convenient pass creation system

### Code style

[![flake8](https://img.shields.io/badge/flake8-purple?style=for-the-badge&logoColor=white)](https://pypi.org/project/flake8/)
[![black](https://img.shields.io/badge/black-black?style=for-the-badge&logoColor=white)](https://pypi.org/project/black/)
[![pymarkdownlnt](https://img.shields.io/badge/pymarkdownlnt-orange?style=for-the-badge&logoColor=white)](https://pypi.org/project/pymarkdownlnt/)
[![djhtml](https://img.shields.io/badge/djhtml-blue?style=for-the-badge&logoColor=white)](https://pypi.org/project/djhtml/)
[![sort-requirements](https://img.shields.io/badge/sort_requirements-green?style=for-the-badge&logoColor=white)](https://pypi.org/project/sort-requirements/)

### Core

[![Python](https://img.shields.io/badge/Python-3.11-gold?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Git](https://img.shields.io/badge/git-scm?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![Django](https://img.shields.io/badge/Django-5.2-gold?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)

## Clone repo

``` bash
git clone https://gitlab.crja72.ru/django/2025/autumn/course/projects/team-9.git
cd team-9
```

### Create and activate virualenv

```  bash
python3 -m venv .venv
source .venv/bin/activate  
```

### Install requirements

```bash
# prod requirements
pip install -r requirements/prod.txt  
# test requirements
pip install -r requirements/test.txt  
# develop requirements
pip install -r requirements/develop.txt  
# lints requirements
pip install -r requirements/lints.txt
```

### Create **.env**

```bash
cp template.env .env
```

### Other presets

```bash
cd lyceum 
python3 manage.py migrate
python3 manage.py collectstatic
```

### Create admin acc

```bash
python manage.py createsuperuser
# fill in the details
```

### fixtures

#### dump data

```bash
cd lyceum
python3 manage.py dumpdata catalog > fixtures/data.json
```

#### load data

```bash
cd lyceum
python3 manage.py loaddata fixtures/data.json
```

### Run server

```fenced-code-language
cd lyceum  
python3 manage.py runserver  
```

### Data base

![data base ER diogram](schema.png)

### http://localhost:8000/
