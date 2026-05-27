import logging
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import CustomUser

logger = logging.getLogger('properties')


class PropertyCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Категория недвижимости'
        verbose_name_plural = 'Категории недвижимости'
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile', verbose_name='Пользователь')
    position = models.CharField(max_length=100, verbose_name='Должность')
    department = models.CharField(max_length=100, blank=True, verbose_name='Отдел')
    hire_date = models.DateField(verbose_name='Дата найма')
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Зарплата')
    photo = models.ImageField(upload_to='employees/', blank=True, null=True, verbose_name='Фото')
    bio = models.TextField(blank=True, verbose_name='Биография')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.position}'

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def phone(self):
        return self.user.phone

    @property
    def email(self):
        return self.user.email


class Owner(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    passport_series = models.CharField(max_length=10, blank=True, verbose_name='Серия паспорта')
    passport_number = models.CharField(max_length=20, blank=True, verbose_name='Номер паспорта')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Владелец'
        verbose_name_plural = 'Владельцы'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()


class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profile', verbose_name='Аккаунт')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Покупатель/Арендатор'
        verbose_name_plural = 'Покупатели/Арендаторы'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()


class Property(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_SOLD = 'sold'
    STATUS_RENTED = 'rented'
    STATUS_RESERVED = 'reserved'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Доступно'),
        (STATUS_SOLD, 'Продано'),
        (STATUS_RENTED, 'Сдано'),
        (STATUS_RESERVED, 'Зарезервировано'),
    ]

    TYPE_SALE = 'sale'
    TYPE_RENT = 'rent'
    TYPE_CHOICES = [
        (TYPE_SALE, 'Продажа'),
        (TYPE_RENT, 'Аренда'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(PropertyCategory, on_delete=models.PROTECT, related_name='properties', verbose_name='Категория')
    owner = models.ForeignKey(Owner, on_delete=models.PROTECT, related_name='properties', verbose_name='Владелец')
    agent = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties', verbose_name='Агент')
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_SALE, verbose_name='Тип сделки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE, verbose_name='Статус')
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Цена (USD)')
    area = models.FloatField(validators=[MinValueValidator(0)], verbose_name='Площадь (м²)')
    rooms = models.PositiveIntegerField(default=1, verbose_name='Количество комнат')
    floor = models.IntegerField(null=True, blank=True, verbose_name='Этаж')
    total_floors = models.IntegerField(null=True, blank=True, verbose_name='Этажей в доме')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    city = models.CharField(max_length=100, default='Минск', verbose_name='Город')
    district = models.CharField(max_length=100, blank=True, verbose_name='Район')
    description = models.TextField(verbose_name='Описание')
    year_built = models.PositiveIntegerField(null=True, blank=True, verbose_name='Год постройки')
    tags = models.ManyToManyField('PropertyTag', blank=True, related_name='properties', verbose_name='Теги')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Объект недвижимости'
        verbose_name_plural = 'Объекты недвижимости'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.price} USD'

    @property
    def price_per_sqm(self):
        if self.area:
            return round(float(self.price) / self.area, 2)
        return 0


class PropertyTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images', verbose_name='Объект')
    image = models.ImageField(upload_to='properties/', verbose_name='Изображение')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')
    is_main = models.BooleanField(default=False, verbose_name='Главное фото')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фото объекта'
        verbose_name_plural = 'Фото объектов'

    def __str__(self):
        return f'Фото для {self.property.title}'


class Deal(models.Model):
    DEAL_SALE = 'sale'
    DEAL_RENT = 'rent'
    DEAL_TYPE_CHOICES = [
        (DEAL_SALE, 'Купля-продажа'),
        (DEAL_RENT, 'Аренда'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'В обработке'),
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_CANCELLED, 'Отменена'),
    ]

    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='deals', verbose_name='Объект')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='deals', verbose_name='Клиент')
    agent = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals', verbose_name='Агент')
    deal_type = models.CharField(max_length=10, choices=DEAL_TYPE_CHOICES, verbose_name='Тип сделки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Статус')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Сумма сделки (USD)')
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Комиссия агентства (USD)')
    contract_date = models.DateField(verbose_name='Дата договора')
    sale_date = models.DateField(null=True, blank=True, verbose_name='Дата продажи/начала аренды')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания (для аренды)')
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'
        ordering = ['-contract_date']

    def __str__(self):
        return f'Сделка #{self.pk}: {self.property.title} — {self.client}'

    def get_profit(self):
        return self.commission


# ===== ОБЩИЕ СТРАНИЦЫ =====

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    summary = models.CharField(max_length=500, verbose_name='Краткое содержание')
    content = models.TextField(verbose_name='Полный текст')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Изображение')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название компании')
    description = models.TextField(verbose_name='Описание')
    founded_year = models.PositiveIntegerField(verbose_name='Год основания')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(verbose_name='Email')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name='Логотип')
    inn = models.CharField(max_length=20, blank=True, verbose_name='ИНН')
    ogrn = models.CharField(max_length=20, blank=True, verbose_name='ОГРН/УНП')
    history = models.TextField(blank=True, verbose_name='История компании')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return self.name


class GlossaryTerm(models.Model):
    term = models.CharField(max_length=200, verbose_name='Термин')
    definition = models.TextField(verbose_name='Определение')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Термин'
        verbose_name_plural = 'Словарь терминов'
        ordering = ['term']

    def __str__(self):
        return self.term


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Автор')
    name = models.CharField(max_length=100, verbose_name='Имя')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Оценка')
    text = models.TextField(verbose_name='Текст отзыва')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.name} — {self.rating}★'


class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(blank=True, verbose_name='Требования')
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Зарплата от')
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Зарплата до')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    description = models.TextField(blank=True, verbose_name='Описание')
    discount_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Скидка %')
    valid_from = models.DateField(verbose_name='Действует с')
    valid_to = models.DateField(verbose_name='Действует до')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-valid_to']

    def __str__(self):
        return f'{self.code} ({self.discount_percent}%)'

    @property
    def is_current(self):
        from django.utils.timezone import now
        today = now().date()
        return self.valid_from <= today <= self.valid_to and self.is_active
