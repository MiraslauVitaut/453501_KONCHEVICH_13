"""
Management command to populate database with demo data.
Usage: python manage.py seed_data
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from properties.models import (
    PropertyCategory, Employee, Owner, Client, Property,
    PropertyTag, Deal, Article, CompanyInfo, GlossaryTerm,
    Review, Vacancy, PromoCode
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with demo data for Variant 13 — Realty Agency'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Пропустить если данные уже есть (не перезаписывать)',
        )

    def handle(self, *args, **options):
        # Если данные уже есть — пропускаем seed (сохраняем пользовательские данные)
        if options.get('skip_if_exists'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(username='admin').exists():
                self.stdout.write('✓ База данных уже заполнена — пропускаем seed_data.')
                return

        self.stdout.write('Seeding database...')

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@realty.by', 'admin123', role='admin',
                                          first_name='Администратор', last_name='Системы')
            self.stdout.write('  Created superuser admin / admin123')

        # Employee users
        emp_users_data = [
            ('ivanova_a', 'Анна', 'Иванова', '+375 (29) 123-45-67', '1988-05-12'),
            ('petrov_d', 'Дмитрий', 'Петров', '+375 (33) 234-56-78', '1990-03-22'),
            ('sidorova_e', 'Елена', 'Сидорова', '+375 (44) 345-67-89', '1985-11-08'),
        ]
        emp_users = []
        for username, first, last, phone, bd in emp_users_data:
            u, created = User.objects.get_or_create(username=username, defaults=dict(
                first_name=first, last_name=last, email=f'{username}@realty.by',
                role='employee', phone=phone, birth_date=date.fromisoformat(bd),
                password='pbkdf2_sha256$' + 'x' * 86,
            ))
            if created:
                u.set_password('emp123')
                u.save()
            emp_users.append(u)

        # Client user
        client_user, _ = User.objects.get_or_create(username='kovalev_i', defaults=dict(
            first_name='Игорь', last_name='Ковалёв', email='kovalev@mail.by',
            role='client', phone='+375 (29) 999-88-77', birth_date=date(1992, 7, 15),
        ))
        if _:
            client_user.set_password('client123')
            client_user.save()

        # Company info
        CompanyInfo.objects.get_or_create(defaults=dict(
            name='РиэлтерПлюс', founded_year=2010,
            description='Ведущее риэлтерское агентство Беларуси. Более 14 лет на рынке недвижимости. '
                        'Профессиональные консультации, подбор объектов, юридическое сопровождение сделок.',
            address='г. Минск, ул. Немига, д. 5, офис 301',
            phone='+375 (17) 300-10-20',
            email='info@rielterplus.by',
            inn='190234567', ogrn='1009876543',
            history='2010 — основание компании\n2013 — открытие второго офиса\n'
                    '2017 — 1000-я сделка\n2020 — цифровизация и онлайн-платформа\n2024 — лидер рынка',
        ), name='РиэлтерПлюс')

        # Categories
        cats_data = ['Квартира', 'Дом/Коттедж', 'Коммерческая недвижимость',
                     'Земельный участок', 'Гараж/Паркинг', 'Таунхаус']
        cats = {}
        for c in cats_data:
            obj, _ = PropertyCategory.objects.get_or_create(name=c, defaults={'description': f'Объекты типа: {c}'})
            cats[c] = obj

        # Employees
        positions = ['Агент по недвижимости', 'Старший агент', 'Руководитель отдела']
        employees = []
        for i, u in enumerate(emp_users):
            emp, _ = Employee.objects.get_or_create(user=u, defaults=dict(
                position=positions[i % len(positions)],
                department='Отдел продаж' if i < 2 else 'Отдел аренды',
                hire_date=date(2018 + i, 3, 1),
                salary=1500 + i * 200,
                bio=f'Специалист с {5 + i} летним опытом в сфере недвижимости.',
                is_active=True,
            ))
            employees.append(emp)

        # Owners
        owners_data = [
            ('Жуков', 'Андрей', 'Петрович', '+375 (29) 111-22-33', 'ул. Ленина, 10, Минск'),
            ('Морозова', 'Светлана', 'Васильевна', '+375 (33) 222-33-44', 'ул. Пушкина, 5, Минск'),
            ('Козлов', 'Максим', 'Александрович', '+375 (44) 333-44-55', 'пр. Независимости, 20, Минск'),
            ('Орлова', 'Татьяна', 'Николаевна', '+375 (29) 444-55-66', 'ул. Советская, 3, Брест'),
            ('Новиков', 'Виктор', 'Игоревич', '+375 (33) 555-66-77', 'ул. Гагарина, 7, Гомель'),
        ]
        owners = []
        for ln, fn, mn, phone, addr in owners_data:
            o, _ = Owner.objects.get_or_create(last_name=ln, first_name=fn, defaults=dict(
                middle_name=mn, phone=phone, address=addr, email=f'{ln.lower()}@mail.by'
            ))
            owners.append(o)

        # Clients
        clients_data = [
            ('Захаров', 'Роман', 'Дмитриевич', '+375 (29) 601-22-33', 'roman.z@mail.by'),
            ('Воробьёва', 'Ирина', 'Сергеевна', '+375 (33) 602-33-44', 'irina.v@mail.by'),
            ('Федоров', 'Павел', 'Андреевич', '+375 (44) 603-44-55', 'pavel.f@mail.by'),
            ('Кузнецова', 'Мария', 'Юрьевна', '+375 (29) 604-55-66', 'maria.k@mail.by'),
            ('Попов', 'Алексей', 'Вячеславович', '+375 (33) 605-66-77', 'aleksei.p@mail.by'),
            ('Лебедева', 'Ольга', 'Николаевна', '+375 (44) 606-77-88', 'olga.l@mail.by'),
            ('Смирнов', 'Егор', 'Владимирович', '+375 (29) 607-88-99', 'egor.s@mail.by'),
            ('Тихонова', 'Наталья', 'Ивановна', '+375 (33) 608-99-00', 'natalia.t@mail.by'),
        ]
        clients = []
        for ln, fn, mn, phone, email in clients_data:
            c, _ = Client.objects.get_or_create(last_name=ln, first_name=fn, defaults=dict(
                middle_name=mn, phone=phone, email=email,
                address=f'г. Минск, ул. Тестовая, {random.randint(1,99)}',
                comment='Постоянный клиент',
            ))
            clients.append(c)

        # Link client_user to first client
        if not clients[0].user:
            clients[0].user = client_user
            clients[0].save()

        # Tags
        tag_names = ['новостройка', 'вторичка', 'евроремонт', 'балкон', 'парковка',
                     'рядом метро', 'тихий район', 'срочно', 'торг']
        tags = [PropertyTag.objects.get_or_create(name=t)[0] for t in tag_names]

        # Properties (12 objects)
        properties_data = [
            ('Уютная 2-комнатная квартира в центре', 'Квартира', 'sale', 'available', 95000, 58.5, 2, 4, 9, 'ул. Немига, 12', 'Минск', 'Центральный', 2005, 'Светлая квартира с качественным ремонтом. Раздельные комнаты. Рядом магазины, школа, метро.'),
            ('Просторная 3-комнатная на Юго-Западе', 'Квартира', 'sale', 'available', 120000, 78.0, 3, 7, 16, 'пр. Дзержинского, 45', 'Минск', 'Юго-Западный', 2012, 'Отличная планировка, новый дом. Закрытый двор, детская площадка.'),
            ('1-комнатная квартира-студия', 'Квартира', 'rent', 'available', 550, 35.0, 1, 3, 12, 'ул. Сурганова, 7', 'Минск', 'Советский', 2018, 'Стильная студия с современным ремонтом. Вся техника. Для молодых специалистов.'),
            ('Дом с участком в Дроздах', 'Дом/Коттедж', 'sale', 'available', 380000, 220.0, 5, 2, 2, 'п. Дрозды, ул. Лесная, 3', 'Минск', 'Заводской', 2015, 'Элитный коттедж. 2 этажа, мансарда, гараж на 2 авто, ухоженный участок 15 соток.'),
            ('Офисное помещение в бизнес-центре', 'Коммерческая недвижимость', 'rent', 'available', 1200, 85.0, 1, 5, 10, 'пр. Победителей, 23', 'Минск', 'Фрунзенский', 2010, 'Готовый офис в современном БЦ. Опен-спейс, переговорная, парковка. А-класс.'),
            ('Земельный участок под строительство', 'Земельный участок', 'sale', 'available', 45000, 1200.0, 0, None, None, 'д. Колодищи', 'Минск', 'Центральный', None, 'Ровный участок 12 соток. Коммуникации по границе. 20 минут от МКАД.'),
            ('2-комнатная квартира в Бресте', 'Квартира', 'sale', 'sold', 62000, 52.0, 2, 2, 5, 'ул. Советская, 18', 'Брест', 'Центр', 1998, 'Квартира после ремонта. Новая сантехника, электрика. Тихий двор.'),
            ('Производственное помещение', 'Коммерческая недвижимость', 'rent', 'rented', 800, 150.0, 1, 1, 1, 'ул. Промышленная, 5', 'Минск', 'Партизанский', 2000, 'Склад-производство. Высокие потолки 6м. Ворота для фуры. Охрана.'),
            ('Таунхаус в Сухарево', 'Таунхаус', 'sale', 'available', 195000, 140.0, 4, 1, 3, 'ул. Сухаревская, 12', 'Минск', 'Московский', 2020, 'Новый таунхаус. 3 этажа. Личный двор 2 сотки. Гараж. Чистовая отделка.'),
            ('Гараж в кооперативе', 'Гараж/Паркинг', 'sale', 'available', 8500, 20.0, 0, None, None, 'ГК Рубин, бокс 47', 'Минск', 'Советский', 1995, 'Капитальный гараж. Смотровая яма. Электричество. Удобный въезд.'),
            ('4-комнатная квартира элит-класса', 'Квартира', 'sale', 'reserved', 280000, 120.0, 4, 15, 17, 'пр. Независимости, 78', 'Минск', 'Октябрьский', 2019, 'Пентхаус. Панорамные окна. Два санузла. Дизайнерский ремонт. Кладовая.'),
            ('Дача с домиком', 'Дом/Коттедж', 'sale', 'available', 28000, 45.0, 2, 1, 1, 'СТ Радуга, уч.12', 'Минск', 'Заводской', 1985, 'Добротная дача. Баня, колодец, плодовый сад. 6 соток. Рядом озеро.'),
        ]

        prop_objects = []
        for i, (title, cat_name, t_type, status, price, area, rooms, floor, t_floors, addr, city, district, year, desc) in enumerate(properties_data):
            prop, created = Property.objects.get_or_create(title=title, defaults=dict(
                category=cats[cat_name],
                owner=owners[i % len(owners)],
                agent=employees[i % len(employees)] if employees else None,
                transaction_type=t_type, status=status, price=price, area=area,
                rooms=rooms, floor=floor, total_floors=t_floors,
                address=addr, city=city, district=district,
                year_built=year, description=desc, is_published=True,
                views_count=random.randint(10, 500),
            ))
            if created:
                # Add 2-3 tags
                prop.tags.set(random.sample(tags, min(3, len(tags))))
            prop_objects.append(prop)

        # Deals
        deals_data = [
            (0, 0, 0, 'sale', 'completed', 95000, 2850, date(2024, 1, 15), date(2024, 1, 20)),
            (6, 1, 1, 'sale', 'completed', 62000, 1860, date(2024, 2, 10), date(2024, 2, 15)),
            (2, 2, 0, 'rent', 'active', 550, 55, date(2024, 3, 1), date(2024, 3, 5)),
            (7, 3, 2, 'rent', 'completed', 800, 80, date(2024, 3, 20), date(2024, 3, 25)),
            (1, 4, 1, 'sale', 'pending', 120000, 3600, date(2024, 4, 5), None),
            (4, 5, 0, 'rent', 'active', 1200, 120, date(2024, 4, 15), date(2024, 4, 20)),
            (3, 6, 2, 'sale', 'completed', 380000, 11400, date(2024, 5, 10), date(2024, 5, 15)),
            (8, 7, 1, 'sale', 'pending', 195000, 5850, date(2024, 6, 1), None),
        ]
        for pi, ci, ei, dtype, status, amount, comm, cdate, sdate in deals_data:
            Deal.objects.get_or_create(
                property=prop_objects[pi], client=clients[ci],
                defaults=dict(
                    agent=employees[ei] if employees else None,
                    deal_type=dtype, status=status, amount=amount,
                    commission=comm, contract_date=cdate, sale_date=sdate,
                )
            )

        # Articles
        articles_data = [
            ('Рынок недвижимости Беларуси в 2024 году', 'Обзор актуальных тенденций белорусского рынка', 'Рынок недвижимости Беларуси продолжает развиваться. В 2024 году наблюдается стабильный спрос на жильё...'),
            ('Как выбрать квартиру: советы эксперта', 'Рекомендации от ведущих специалистов агентства', 'При выборе квартиры важно учитывать несколько ключевых факторов: локация, инфраструктура, состояние...'),
            ('Ипотека в 2024: что изменилось?', 'Новые условия кредитования на жильё в Беларуси', 'Банки Беларуси скорректировали условия ипотечного кредитования. Разбираем основные изменения...'),
            ('Аренда vs покупка: что выгоднее?', 'Финансовый анализ двух стратегий', 'Вопрос "снимать или купить" актуален для многих. Мы провели подробный расчёт для Минска...'),
        ]
        for title, summary, content in articles_data:
            Article.objects.get_or_create(title=title, defaults=dict(summary=summary, content=content, is_published=True))

        # Glossary
        glossary_data = [
            ('Кадастровая стоимость', 'Оценка недвижимости, определённая государством для целей налогообложения и расчёта госпошлин.'),
            ('Задаток', 'Денежная сумма, передаваемая покупателем продавцу в счёт будущей оплаты как подтверждение серьёзности намерений.'),
            ('Обременение', 'Ограничение прав собственника: ипотека, арест, сервитут, аренда и т.д.'),
            ('Эскроу-счёт', 'Специальный счёт для безопасного хранения денег при сделке купли-продажи до выполнения всех условий договора.'),
            ('Технический паспорт', 'Документ с описанием технических характеристик объекта недвижимости: площадь, планировка, инженерные системы.'),
            ('Рента', 'Регулярные платежи за пользование имуществом или уступку прав на него.'),
        ]
        for term, defn in glossary_data:
            GlossaryTerm.objects.get_or_create(term=term, defaults={'definition': defn})

        # Reviews
        reviews_data = [
            ('Мария К.', 5, 'Отличное агентство! Нашли квартиру за 2 недели. Агент Анна — профессионал.'),
            ('Сергей Л.', 4, 'Хорошая работа. Немного затянулось оформление документов, но в итоге всё отлично.'),
            ('Ольга П.', 5, 'Продали дачу быстро и по хорошей цене. Рекомендую всем!'),
            ('Иван Б.', 3, 'Среднее впечатление. Пришлось несколько раз звонить самому.'),
            ('Наталья В.', 5, 'Сняли офис через РиэлтерПлюс. Всё прозрачно, честно. Спасибо!'),
        ]
        for name, rating, text in reviews_data:
            Review.objects.get_or_create(name=name, defaults=dict(rating=rating, text=text, is_approved=True))

        # Vacancies
        vacancies_data = [
            ('Агент по недвижимости', 'Поиск клиентов, показ объектов, сопровождение сделок. Опыт от 1 года.', 800, 2000),
            ('Юрист по недвижимости', 'Правовое сопровождение сделок, проверка документов. Высшее юридическое образование.', 1200, 2500),
            ('Маркетолог', 'Продвижение объектов в интернете, ведение соц. сетей, аналитика. Опыт от 2 лет.', 900, 1500),
        ]
        for title, desc, sf, st in vacancies_data:
            Vacancy.objects.get_or_create(title=title, defaults=dict(description=desc, salary_from=sf, salary_to=st, is_active=True))

        # Promo codes
        today = date.today()
        PromoCode.objects.get_or_create(code='REALTY10', defaults=dict(
            description='Скидка 10% на комиссию при продаже квартиры', discount_percent=10,
            valid_from=today, valid_to=today + timedelta(days=30), is_active=True
        ))
        PromoCode.objects.get_or_create(code='RENT15', defaults=dict(
            description='Скидка 15% на оформление аренды', discount_percent=15,
            valid_from=today, valid_to=today + timedelta(days=60), is_active=True
        ))
        PromoCode.objects.get_or_create(code='OLDPROMO', defaults=dict(
            description='Архивный промокод', discount_percent=5,
            valid_from=date(2023, 1, 1), valid_to=date(2023, 12, 31), is_active=False
        ))

        self.ensure_10_records()
        self.stdout.write(self.style.SUCCESS('✓ Database seeded successfully!'))
        self.stdout.write('  Logins: admin/admin123  |  emp: ivanova_a/emp123  |  client: kovalev_i/client123')

    # Вызывается повторно — добавим недостающие записи до 10
    def ensure_10_records(self):
        """Проверяет и дополняет таблицы до 10 записей."""
        from django.utils import timezone

        # Дополнительные статьи (до 10)
        extra_articles = [
            ('Как правильно оценить стоимость квартиры', 'Практическое руководство по оценке'),
            ('Юридическое сопровождение сделок', 'Что нужно знать о документах'),
            ('Аренда коммерческой недвижимости: советы', 'Особенности аренды офисов и складов'),
            ('Новостройки Минска 2024: обзор', 'Лучшие жилые комплексы года'),
            ('Инвестиции в недвижимость Беларуси', 'Как сохранить и приумножить капитал'),
            ('Ипотека без первоначального взноса', 'Реально ли это в 2024 году?'),
        ]
        for title, summary in extra_articles:
            Article.objects.get_or_create(title=title, defaults=dict(
                summary=summary, content=f'{summary}. Подробная информация от экспертов агентства РиэлтерПлюс. '
                        'Наши специалисты имеют многолетний опыт работы на рынке недвижимости Беларуси.',
                is_published=True
            ))

        # Дополнительные термины (до 10)
        extra_terms = [
            ('Ликвидность', 'Способность актива быть быстро проданным по цене, близкой к рыночной.'),
            ('Амортизация', 'Постепенное уменьшение стоимости имущества вследствие износа.'),
            ('Субаренда', 'Передача арендатором прав пользования имуществом третьему лицу.'),
            ('Девелопер', 'Компания или лицо, занимающееся строительством и развитием объектов недвижимости.'),
        ]
        for term, defn in extra_terms:
            GlossaryTerm.objects.get_or_create(term=term, defaults={'definition': defn})

        # Дополнительные вакансии (до 10)
        extra_vacancies = [
            ('Оценщик недвижимости', 'Проведение оценки рыночной стоимости объектов. Лицензия обязательна.', 1000, 1800),
            ('Менеджер по работе с клиентами', 'Консультирование клиентов, ведение CRM. Опыт от 1 года.', 700, 1200),
            ('Ипотечный брокер', 'Подбор ипотечных программ для клиентов. Опыт в банковской сфере.', 900, 1600),
            ('Фотограф недвижимости', 'Профессиональная фотосъёмка объектов. Опыт работы с интерьерами.', 600, 1000),
            ('IT-специалист (сайт)', 'Поддержка и развитие веб-платформы агентства. Django, Python.', 1500, 2500),
            ('Администратор офиса', 'Ведение документации, работа с клиентами на ресепшене.', 600, 900),
            ('Специалист по рекламе', 'Размещение объявлений, работа с порталами недвижимости.', 700, 1100),
        ]
        for title, desc, sf, st in extra_vacancies:
            Vacancy.objects.get_or_create(title=title, defaults=dict(
                description=desc, salary_from=sf, salary_to=st, is_active=True
            ))

        # Дополнительные промокоды (до 10)
        import random
        from datetime import date, timedelta
        today = date.today()
        extra_promos = [
            ('NEWCLIENT', 'Скидка для новых клиентов', 8, True),
            ('SUMMER24', 'Летняя акция 2024', 12, True),
            ('VIP20', 'VIP-клиентам', 20, True),
            ('FAMILY', 'Семейная ипотека', 5, True),
            ('WINTER23', 'Зимняя акция 2023 (архив)', 7, False),
            ('SPRING23', 'Весенняя акция 2023 (архив)', 10, False),
            ('BDAY10', 'Скидка в день рождения', 10, True),
        ]
        for code, desc, pct, active in extra_promos:
            PromoCode.objects.get_or_create(code=code, defaults=dict(
                description=desc, discount_percent=pct, is_active=active,
                valid_from=today if active else date(2023,1,1),
                valid_to=(today+timedelta(days=90)) if active else date(2023,12,31),
            ))

        # Дополнительные отзывы (до 10)
        extra_reviews = [
            ('Алексей Д.', 5, 'Купили квартиру через РиэлтерПлюс. Агент Дмитрий — настоящий профи!'),
            ('Виктория Н.', 4, 'Хорошее агентство, нашли арендаторов за неделю. Рекомендую.'),
            ('Игорь В.', 5, 'Продали дом быстро и дорого. Всё чисто, без скрытых комиссий.'),
            ('Татьяна К.', 3, 'В целом нормально, но хотелось бы больше вариантов на выбор.'),
            ('Михаил Г.', 5, 'Третья сделка с этим агентством. Всегда доволен результатом.'),
        ]
        for name, rating, text in extra_reviews:
            Review.objects.get_or_create(name=name, defaults=dict(
                rating=rating, text=text, is_approved=True
            ))

        self.stdout.write('  Extra records added.')
