"""
Тесты для риэлтерского агентства (Вариант 13).
Запуск: cd realty_agency && python manage.py test properties users -v 2
"""
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from properties.models import (
    PropertyCategory, Owner, Employee, Client, Property,
    Deal, PropertyTag, Review, Article, PromoCode,
)
from properties.forms import ReviewForm, ClientForm, PropertyFilterForm

User = get_user_model()


def make_admin():
    u, created = User.objects.get_or_create(username='t_admin', defaults=dict(
        first_name='Admin', last_name='Test', role='admin',
        birth_date=date(1985, 1, 1), is_staff=True, is_superuser=True,
    ))
    if created:
        u.set_password('pass123')
        u.save()
    return u


def make_emp_user():
    u, created = User.objects.get_or_create(username='t_emp', defaults=dict(
        first_name='Emp', last_name='Test', role='employee',
        birth_date=date(1990, 5, 10), phone='+375 (29) 111-11-11',
    ))
    if created:
        u.set_password('pass123')
        u.save()
    return u


def make_client_user():
    u, created = User.objects.get_or_create(username='t_client', defaults=dict(
        first_name='Client', last_name='Test', role='client',
        birth_date=date(1995, 3, 20),
    ))
    if created:
        u.set_password('pass123')
        u.save()
    return u


def make_category(name='Квартира'):
    return PropertyCategory.objects.get_or_create(name=name, defaults={'description': name})[0]


def make_owner():
    return Owner.objects.get_or_create(
        last_name='Тестов', first_name='Владелец', defaults=dict(
            phone='+375 (29) 500-00-01', address='ул. Тест, 1', email='own@t.by',
        )
    )[0]


def make_employee(user):
    return Employee.objects.get_or_create(user=user, defaults=dict(
        position='Агент', department='Продажи',
        hire_date=date(2020, 1, 1), salary=Decimal('1200.00'),
    ))[0]


def make_property(category=None, owner=None, agent=None,
                  status='available', transaction_type='sale', price=100000):
    return Property.objects.create(
        title=f'Объект #{Property.objects.count()+1}',
        category=category or make_category(),
        owner=owner or make_owner(),
        agent=agent,
        transaction_type=transaction_type, status=status,
        price=Decimal(str(price)), area=60.0, rooms=2,
        address='ул. Тестовая, 1', city='Минск',
        description='Тестовое описание объекта недвижимости.',
        is_published=True,
    )


def make_client_record(user=None):
    return Client.objects.get_or_create(
        last_name='Клиентов', first_name='Тест', defaults=dict(
            user=user, phone='+375 (29) 222-22-22',
            email='cr@t.by', address='ул. Клиентская, 5',
        )
    )[0]


# ─── Модели ─────────────────────────────────────

class PropertyCategoryTest(TestCase):
    def test_str(self):
        cat = PropertyCategory(name='Квартира')
        self.assertEqual(str(cat), 'Квартира')


class OwnerModelTest(TestCase):
    def test_full_name(self):
        o = Owner(last_name='Иванов', first_name='Иван', middle_name='Иванович')
        self.assertEqual(o.full_name, 'Иванов Иван Иванович')

    def test_full_name_no_middle(self):
        o = Owner(last_name='Иванов', first_name='Иван')
        self.assertNotIn('  ', o.full_name)


class PropertyModelTest(TestCase):
    def setUp(self):
        self.prop = make_property(price=100000)

    def test_price_per_sqm(self):
        self.assertAlmostEqual(self.prop.price_per_sqm, 1666.67, delta=1)

    def test_price_per_sqm_zero_area(self):
        self.prop.area = 0
        self.assertEqual(self.prop.price_per_sqm, 0)

    def test_default_status(self):
        self.assertEqual(self.prop.status, 'available')

    def test_views_count_default(self):
        self.assertEqual(self.prop.views_count, 0)

    def test_is_published_default(self):
        self.assertTrue(self.prop.is_published)

    def test_str_contains_price(self):
        self.assertIn('100000', str(self.prop))


class DealModelTest(TestCase):
    def test_get_profit(self):
        deal = Deal(commission=Decimal('5000'))
        self.assertEqual(deal.get_profit(), Decimal('5000'))

    def test_deal_str(self):
        prop = make_property()
        cl = make_client_record()
        deal = Deal.objects.create(
            property=prop, client=cl,
            deal_type='sale', status='pending',
            amount=Decimal('100000'), commission=Decimal('3000'),
            contract_date=date.today(),
        )
        self.assertIn(str(deal.pk), str(deal))


class PromoCodeModelTest(TestCase):
    def test_is_current_active(self):
        today = date.today()
        p = PromoCode(code='T1', discount_percent=10,
                      valid_from=today, valid_to=today+timedelta(days=10), is_active=True)
        self.assertTrue(p.is_current)

    def test_is_current_expired(self):
        p = PromoCode(code='T2', discount_percent=10,
                      valid_from=date(2020,1,1), valid_to=date(2020,12,31), is_active=True)
        self.assertFalse(p.is_current)

    def test_is_current_inactive(self):
        today = date.today()
        p = PromoCode(code='T3', discount_percent=5,
                      valid_from=today, valid_to=today+timedelta(days=10), is_active=False)
        self.assertFalse(p.is_current)


class UserModelTest(TestCase):
    def test_is_employee(self):
        u = User(username='e', role='employee')
        self.assertTrue(u.is_employee())

    def test_is_client(self):
        u = User(username='c', role='client')
        self.assertTrue(u.is_client())

    def test_str_shows_role(self):
        u = User(username='t', first_name='А', last_name='Б', role='client')
        self.assertIn('Клиент', str(u))


# ─── Формы ─────────────────────────────────────

class ReviewFormTest(TestCase):
    def test_valid(self):
        f = ReviewForm({'name': 'Тест', 'rating': 5, 'text': 'Отличное агентство, всем рекомендую!'})
        self.assertTrue(f.is_valid())

    def test_short_text(self):
        f = ReviewForm({'name': 'Тест', 'rating': 4, 'text': 'Коротко'})
        self.assertFalse(f.is_valid())
        self.assertIn('text', f.errors)

    def test_missing_rating(self):
        f = ReviewForm({'name': 'Тест', 'text': 'Достаточно длинный текст отзыва.'})
        self.assertFalse(f.is_valid())


class ClientFormTest(TestCase):
    VALID = {'first_name': 'Иван', 'last_name': 'Иванов',
             'phone': '+375 (29) 123-45-67', 'email': 'i@t.by', 'address': 'ул. 1'}

    def test_valid(self):
        self.assertTrue(ClientForm(self.VALID).is_valid())

    def test_invalid_phone(self):
        data = {**self.VALID, 'phone': '80291234567'}
        f = ClientForm(data)
        self.assertFalse(f.is_valid())
        self.assertIn('phone', f.errors)

    def test_missing_last_name(self):
        data = {**self.VALID}
        del data['last_name']
        self.assertFalse(ClientForm(data).is_valid())


class PropertyFilterFormTest(TestCase):
    def test_empty_valid(self):
        self.assertTrue(PropertyFilterForm({}).is_valid())

    def test_with_filters(self):
        f = PropertyFilterForm({'search': 'кв', 'price_min': '50000',
                                'price_max': '150000', 'transaction_type': 'sale'})
        self.assertTrue(f.is_valid())


# ─── Представления — публичные ─────────────────

class PublicViewsTest(TestCase):
    def setUp(self):
        self.tc = TestClient()
        self.prop = make_property()

    def _get200(self, url):
        self.assertEqual(self.tc.get(url).status_code, 200)

    def test_home(self):           self._get200(reverse('properties:home'))
    def test_list(self):           self._get200(reverse('properties:list'))
    def test_detail(self):         self._get200(reverse('properties:detail', args=[self.prop.pk]))
    def test_about(self):          self._get200(reverse('properties:about'))
    def test_news(self):           self._get200(reverse('properties:news'))
    def test_glossary(self):       self._get200(reverse('properties:glossary'))
    def test_contacts(self):       self._get200(reverse('properties:contacts'))
    def test_privacy(self):        self._get200(reverse('properties:privacy'))
    def test_vacancies(self):      self._get200(reverse('properties:vacancies'))
    def test_reviews(self):        self._get200(reverse('properties:reviews'))
    def test_promos(self):         self._get200(reverse('properties:promos'))

    def test_detail_increments_views(self):
        before = self.prop.views_count
        self.tc.get(reverse('properties:detail', args=[self.prop.pk]))
        self.prop.refresh_from_db()
        self.assertEqual(self.prop.views_count, before + 1)

    def test_news_detail_404_unpublished(self):
        a = Article.objects.create(title='X', summary='s', content='c', is_published=False)
        self.assertEqual(self.tc.get(reverse('properties:news_detail', args=[a.pk])).status_code, 404)

    def test_list_search(self):
        self._get200(reverse('properties:list') + '?search=Объект')

    def test_list_filter_type(self):
        self._get200(reverse('properties:list') + '?transaction_type=sale')


# ─── Представления — авторизованные ─────────────

class AuthViewsTest(TestCase):
    def setUp(self):
        self.tc = TestClient()
        self.admin = make_admin()
        self.emp_user = make_emp_user()
        self.emp = make_employee(self.emp_user)
        self.prop = make_property(agent=self.emp)
        self.client_rec = make_client_record()

    def test_create_requires_login(self):
        r = self.tc.get(reverse('properties:create'))
        self.assertEqual(r.status_code, 302)

    def test_create_as_employee(self):
        self.tc.login(username='t_emp', password='pass123')
        self.assertEqual(self.tc.get(reverse('properties:create')).status_code, 200)

    def test_create_as_client_redirects(self):
        make_client_user()
        self.tc.login(username='t_client', password='pass123')
        r = self.tc.get(reverse('properties:create'))
        self.assertEqual(r.status_code, 302)

    def test_statistics_requires_login(self):
        r = self.tc.get(reverse('properties:statistics'))
        self.assertEqual(r.status_code, 302)

    def test_statistics_as_admin(self):
        self.tc.login(username='t_admin', password='pass123')
        self.assertEqual(self.tc.get(reverse('properties:statistics')).status_code, 200)

    def test_delete_as_admin(self):
        self.tc.login(username='t_admin', password='pass123')
        p2 = make_property()
        self.tc.post(reverse('properties:delete', args=[p2.pk]))
        self.assertFalse(Property.objects.filter(pk=p2.pk).exists())

    def test_client_list_as_employee(self):
        self.tc.login(username='t_emp', password='pass123')
        self.assertEqual(self.tc.get(reverse('properties:client_list')).status_code, 200)


# ─── Авторизация/регистрация ─────────────────────

class UserAuthTest(TestCase):
    def setUp(self):
        self.tc = TestClient()

    def test_register_page_200(self):
        self.assertEqual(self.tc.get(reverse('users:register')).status_code, 200)

    def test_login_page_200(self):
        self.assertEqual(self.tc.get(reverse('users:login')).status_code, 200)

    def test_register_creates_user(self):
        self.tc.post(reverse('users:register'), {
            'username': 'newreg99', 'first_name': 'Новый', 'last_name': 'Рег',
            'email': 'nr@t.by', 'password1': 'SecurePass123!', 'password2': 'SecurePass123!',
        })
        self.assertTrue(User.objects.filter(username='newreg99').exists())

    def test_login_valid(self):
        User.objects.create_user('lgtest', password='TestPass999!',
                                 birth_date=date(1990, 1, 1), role='client')
        r = self.tc.post(reverse('users:login'), {'username': 'lgtest', 'password': 'TestPass999!'})
        self.assertRedirects(r, reverse('properties:home'), fetch_redirect_response=False)

    def test_profile_requires_login(self):
        self.assertEqual(self.tc.get(reverse('users:profile')).status_code, 302)

    def test_profile_authenticated(self):
        make_client_user()
        self.tc.login(username='t_client', password='pass123')
        self.assertEqual(self.tc.get(reverse('users:profile')).status_code, 200)


# ─── Валидация ───────────────────────────────────

class ValidationTest(TestCase):
    def test_phone_valid(self):
        from users.models import validate_phone
        for p in ['+375 (29) 123-45-67', '+375 (33) 987-65-43', '+375 (44) 000-00-00']:
            validate_phone(p)

    def test_phone_invalid(self):
        from users.models import validate_phone
        from django.core.exceptions import ValidationError
        for p in ['80291234567', '+375291234567', '+375 (28) 123-45-67']:
            with self.assertRaises(ValidationError):
                validate_phone(p)

    def test_age_under_18(self):
        from users.models import validate_age_18
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_age_18(date.today() - timedelta(days=365*16))

    def test_age_over_18(self):
        from users.models import validate_age_18
        validate_age_18(date.today() - timedelta(days=365*20))


# ─── CRUD ORM ────────────────────────────────────

class PropertyCRUDTest(TestCase):
    def test_create(self):
        p = make_property()
        self.assertIsNotNone(p.pk)

    def test_read(self):
        p = make_property()
        self.assertEqual(Property.objects.get(pk=p.pk).title, p.title)

    def test_update(self):
        p = make_property()
        p.price = Decimal('200000')
        p.save()
        p.refresh_from_db()
        self.assertEqual(p.price, Decimal('200000'))

    def test_delete(self):
        p = make_property()
        pk = p.pk
        p.delete()
        self.assertFalse(Property.objects.filter(pk=pk).exists())

    def test_filter_city(self):
        make_property()
        self.assertGreater(Property.objects.filter(city='Минск').count(), 0)

    def test_order_by_price(self):
        make_property(price=50000)
        make_property(price=200000)
        props = list(Property.objects.order_by('price'))
        self.assertLessEqual(props[0].price, props[-1].price)


# ─── Связи: 1:1, 1:N, N:N ───────────────────────

class RelationsTest(TestCase):
    def test_employee_onetoone_user(self):
        u = make_emp_user()
        emp = make_employee(u)
        self.assertEqual(emp.user, u)
        self.assertEqual(u.employee_profile, emp)

    def test_property_fk_category(self):
        cat = make_category('Дом')
        p = make_property(category=cat)
        self.assertIn(p, cat.properties.all())

    def test_property_m2m_tags(self):
        p = make_property()
        t1 = PropertyTag.objects.create(name='тег-а')
        t2 = PropertyTag.objects.create(name='тег-б')
        p.tags.set([t1, t2])
        self.assertEqual(p.tags.count(), 2)

    def test_deal_fks(self):
        u = make_emp_user()
        emp = make_employee(u)
        prop = make_property(agent=emp)
        cl = make_client_record()
        deal = Deal.objects.create(
            property=prop, client=cl, agent=emp,
            deal_type='sale', status='pending',
            amount=Decimal('100000'), commission=Decimal('3000'),
            contract_date=date.today(),
        )
        self.assertEqual(deal.property, prop)
        self.assertEqual(deal.client, cl)
        self.assertEqual(deal.agent, emp)
