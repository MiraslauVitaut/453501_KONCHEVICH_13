# РиэлтерПлюс — Лабораторная работа №5 (Django)

**Вариант 13 — Риэлтерское агентство**

## Технологии
- Python 3.12, Django 5.x
- SQLite (локально) / PostgreSQL (продакшн)
- Bootstrap 5, Chart.js
- Django REST Framework

## Быстрый старт

```bash
# Клонировать репозиторий
git clone <repo_url> && cd realty_agency

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Наполнить базу данными
python manage.py seed_data

# Запустить сервер
python manage.py runserver
```

Открыть в браузере: http://127.0.0.1:8000

## Тестовые пользователи

| Роль | Логин | Пароль |
|------|-------|--------|
| Суперюзер | admin | admin123 |
| Сотрудник | ivanova_a | emp123 |
| Клиент | kovalev_i | client123 |

## Запуск тестов

```bash
python manage.py test properties users -v 2
# или через pytest:
pip install pytest-django pytest-cov
pytest --cov=properties --cov=users --cov-report=term-missing
```

## Docker

```bash
# Собрать и запустить
docker-compose up --build

# Остановить
docker-compose down
```

## Структура проекта

```
realty_agency/
├── realty_agency/      # Настройки Django
├── users/              # Кастомная модель пользователя, авторизация
├── properties/         # Основное приложение (недвижимость, сделки, клиенты)
│   ├── models.py       # Модели: Property, Deal, Client, Employee, Owner...
│   ├── views.py        # CRUD-представления
│   ├── forms.py        # Формы с валидацией
│   ├── admin.py        # Настройка панели администратора
│   ├── tests.py        # 67 тестов (models, forms, views, auth, CRUD)
│   └── multitasking_views.py  # Доп. задание: Threading, Multiprocessing, Asyncio
├── api/                # REST API (DRF)
├── templates/          # HTML-шаблоны
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Выполненные требования

- [x] Модели с OneToOneField, ForeignKey, ManyToManyField
- [x] CRUD-операции для всех ключевых моделей
- [x] Панель администратора с фильтрацией и встроенным редактированием
- [x] Авторизация и аутентификация (login/register/logout/profile)
- [x] Разграничение прав: Superuser / Employee / Client / Аноним
- [x] ≥10 объектов недвижимости в базе
- [x] 2 внешних API: Open Exchange Rates (курс валют) + wttr.in (погода)
- [x] Регулярные выражения в URL (re_path)
- [x] Статистические показатели + сортировка/поиск
- [x] Диаграммы и графики (Chart.js): статус, тип, города, категории, динамика
- [x] Временная зона, даты в формате DD/MM/YYYY
- [x] Формат телефона +375 (29) XXX-XX-XX
- [x] Возрастное ограничение 18+
- [x] Логирование с уровнями (настраивается через LOG_LEVEL)
- [x] Валидация форм (сервер + HTML5 client-side)
- [x] REST API с ограничением для неавторизованных
- [x] 67 тестов (покрытие >80%)
- [x] Dockerfile + docker-compose
- [x] Общие страницы: Главная, О компании, Новости, Словарь, Контакты, Отзывы, Вакансии, Промокоды, Политика конфид.
- [x] Дополнительное задание: Threading, Multiprocessing, Asyncio (/multitasking/)
