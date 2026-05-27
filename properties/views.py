import logging
import requests
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse

from .models import (
    Property, PropertyCategory, Deal, Client, Employee,
    Article, CompanyInfo, GlossaryTerm, Review, Vacancy, PromoCode, Owner
)
from .forms import PropertyFilterForm, PropertyForm, DealForm, ReviewForm, ClientForm

logger = logging.getLogger('properties')


# ===== ОБЩИЕ СТРАНИЦЫ =====

def home(request):
    latest_article = Article.objects.filter(is_published=True).first()
    featured_properties = Property.objects.filter(is_published=True, status='available')[:6]
    stats = {
        'total_properties': Property.objects.filter(is_published=True).count(),
        'completed_deals': Deal.objects.filter(status='completed').count(),
        'clients': Client.objects.count(),
        'employees': Employee.objects.filter(is_active=True).count(),
    }
    # API: Open Exchange Rates (бесплатный курс валют)
    exchange_data = {}
    try:
        resp = requests.get('https://open.er-api.com/v6/latest/USD', timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            exchange_data = {
                'BYN': round(data['rates'].get('BYN', 0), 4),
                'EUR': round(data['rates'].get('EUR', 0), 4),
                'RUB': round(data['rates'].get('RUB', 0), 4),
            }
    except Exception as e:
        logger.warning(f'Exchange API error: {e}')

    context = {
        'latest_article': latest_article,
        'featured_properties': featured_properties,
        'stats': stats,
        'exchange_data': exchange_data,
        'now': timezone.now(),
    }
    return render(request, 'main/home.html', context)


def about(request):
    company = CompanyInfo.objects.first()
    employees = Employee.objects.filter(is_active=True).select_related('user')
    return render(request, 'main/about.html', {'company': company, 'employees': employees})


def news_list(request):
    articles = Article.objects.filter(is_published=True)
    paginator = Paginator(articles, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/news.html', {'page_obj': page})


def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, 'main/news_detail.html', {'article': article})


def glossary(request):
    terms = GlossaryTerm.objects.all().order_by('term')
    return render(request, 'main/glossary.html', {'terms': terms})


def contacts(request):
    company = CompanyInfo.objects.first()
    employees = Employee.objects.filter(is_active=True).select_related('user')
    # API: геокодер для карты (wttr.in погода — демонстрация 2го API)
    weather = {}
    try:
        resp = requests.get('https://wttr.in/Minsk?format=j1', timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            weather = {
                'temp': data['current_condition'][0].get('temp_C', '?'),
                'desc': data['current_condition'][0].get('weatherDesc', [{}])[0].get('value', ''),
            }
    except Exception as e:
        logger.warning(f'Weather API error: {e}')
    return render(request, 'main/contacts.html', {'company': company, 'employees': employees, 'weather': weather})


def privacy(request):
    return render(request, 'main/privacy.html')


def vacancies(request):
    active = Vacancy.objects.filter(is_active=True)
    return render(request, 'main/vacancies.html', {'vacancies': active})


def reviews(request):
    all_reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    form = ReviewForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Для добавления отзыва необходимо войти в систему.')
            return redirect('users:login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            if not review.name:
                review.name = request.user.get_full_name() or request.user.username
            review.save()
            messages.success(request, 'Отзыв отправлен на модерацию.')
            return redirect('properties:reviews')
    return render(request, 'main/reviews.html', {'reviews': all_reviews, 'form': form})


def promo_codes(request):
    active_promos = PromoCode.objects.filter(is_active=True)
    archive_promos = PromoCode.objects.filter(is_active=False)
    today = timezone.now().date()
    return render(request, 'main/promos.html', {
        'active_promos': active_promos,
        'archive_promos': archive_promos,
        'today': today,
    })


# ===== ОБЪЕКТЫ НЕДВИЖИМОСТИ =====

def property_list(request):
    qs = Property.objects.filter(is_published=True).select_related('category', 'owner', 'agent')
    form = PropertyFilterForm(request.GET)
    if form.is_valid():
        s = form.cleaned_data
        if s.get('search'):
            qs = qs.filter(Q(title__icontains=s['search']) | Q(address__icontains=s['search']) | Q(description__icontains=s['search']))
        if s.get('category'):
            qs = qs.filter(category_id=s['category'])
        if s.get('transaction_type'):
            qs = qs.filter(transaction_type=s['transaction_type'])
        if s.get('price_min'):
            qs = qs.filter(price__gte=s['price_min'])
        if s.get('price_max'):
            qs = qs.filter(price__lte=s['price_max'])
        if s.get('city'):
            qs = qs.filter(city__icontains=s['city'])
        if s.get('rooms'):
            qs = qs.filter(rooms=s['rooms'])
        sort = s.get('sort')
        if sort:
            qs = qs.order_by(sort)

    paginator = Paginator(qs, 9)
    page = paginator.get_page(request.GET.get('page'))
    categories = PropertyCategory.objects.all()
    logger.info(f'Property list viewed: {qs.count()} results')
    return render(request, 'properties/list.html', {'page_obj': page, 'form': form, 'categories': categories})


def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk, is_published=True)
    prop.views_count += 1
    prop.save(update_fields=['views_count'])
    similar = Property.objects.filter(
        category=prop.category, is_published=True, status='available'
    ).exclude(pk=pk)[:4]
    logger.info(f'Property #{pk} viewed')
    return render(request, 'properties/detail.html', {'property': prop, 'similar': similar})


@login_required
def property_create(request):
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:list')
    form = PropertyForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        prop = form.save()
        logger.info(f'Property #{prop.pk} created by {request.user}')
        messages.success(request, 'Объект добавлен.')
        return redirect('properties:detail', pk=prop.pk)
    return render(request, 'properties/form.html', {'form': form, 'title': 'Добавить объект'})


@login_required
def property_update(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:detail', pk=pk)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=prop)
    if request.method == 'POST' and form.is_valid():
        form.save()
        logger.info(f'Property #{pk} updated by {request.user}')
        messages.success(request, 'Объект обновлён.')
        return redirect('properties:detail', pk=pk)
    return render(request, 'properties/form.html', {'form': form, 'title': 'Редактировать объект', 'property': prop})


@login_required
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('properties:detail', pk=pk)
    if request.method == 'POST':
        logger.warning(f'Property #{pk} deleted by {request.user}')
        prop.delete()
        messages.success(request, 'Объект удалён.')
        return redirect('properties:list')
    return render(request, 'properties/confirm_delete.html', {'property': prop})


# ===== СДЕЛКИ (для сотрудников и админа) =====

@login_required
def deal_list(request):
    if request.user.is_staff:
        qs = Deal.objects.all().select_related('property', 'client', 'agent')
    elif request.user.is_employee():
        try:
            emp = request.user.employee_profile
            qs = Deal.objects.filter(agent=emp).select_related('property', 'client')
        except:
            qs = Deal.objects.none()
    elif request.user.is_client():
        try:
            client = request.user.client_profile
            qs = Deal.objects.filter(client=client).select_related('property', 'agent')
        except:
            qs = Deal.objects.none()
    else:
        qs = Deal.objects.none()
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'properties/deal_list.html', {'page_obj': page})


@login_required
def deal_create(request):
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:deal_list')
    form = DealForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deal = form.save()
        prop = deal.property
        if deal.deal_type == 'sale':
            prop.status = 'sold'
        else:
            prop.status = 'rented'
        prop.save(update_fields=['status'])
        logger.info(f'Deal #{deal.pk} created by {request.user}')
        messages.success(request, 'Сделка создана.')
        return redirect('properties:deal_list')
    return render(request, 'properties/deal_form.html', {'form': form, 'title': 'Новая сделка'})


@login_required
def deal_update(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:deal_list')
    form = DealForm(request.POST or None, instance=deal)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Сделка обновлена.')
        return redirect('properties:deal_list')
    return render(request, 'properties/deal_form.html', {'form': form, 'title': 'Редактировать сделку', 'deal': deal})


@login_required
def deal_delete(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('properties:deal_list')
    if request.method == 'POST':
        deal.delete()
        messages.success(request, 'Сделка удалена.')
        return redirect('properties:deal_list')
    return render(request, 'properties/confirm_delete_deal.html', {'deal': deal})


# ===== СТАТИСТИКА =====

@login_required
def statistics(request):
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:list')

    from django.db.models.functions import TruncMonth
    from decimal import Decimal
    import statistics as stats_lib
    from users.models import CustomUser

    deals = Deal.objects.filter(status='completed')
    total_amount = deals.aggregate(s=Sum('amount'))['s'] or 0
    total_commission = deals.aggregate(s=Sum('commission'))['s'] or 0
    avg_amount = deals.aggregate(a=Avg('amount'))['a'] or 0

    # ── Медиана и мода по суммам сделок ──
    amounts = list(deals.values_list('amount', flat=True))
    amounts_float = [float(a) for a in amounts]

    if len(amounts_float) >= 2:
        median_amount = stats_lib.median(amounts_float)
    elif len(amounts_float) == 1:
        median_amount = amounts_float[0]
    else:
        median_amount = 0

    try:
        mode_amount = stats_lib.mode(amounts_float) if amounts_float else 0
    except stats_lib.StatisticsError:
        mode_amount = max(set(amounts_float), key=amounts_float.count) if amounts_float else 0

    # ── Возраст клиентов ──
    from django.utils import timezone as tz_mod
    today = tz_mod.now().date()
    users_with_bd = CustomUser.objects.filter(birth_date__isnull=False)
    ages = [(today - u.birth_date).days // 365 for u in users_with_bd]
    avg_age = round(stats_lib.mean(ages), 1) if ages else 0
    median_age = round(stats_lib.median(ages), 1) if len(ages) >= 1 else 0

    # ── Линейный тренд продаж ──
    monthly_deals = deals.annotate(month=TruncMonth('contract_date')) \
        .values('month').annotate(cnt=Count('id'), total=Sum('amount')) \
        .order_by('month')
    monthly_list = list(monthly_deals)

    trend_data = []
    if len(monthly_list) >= 2:
        n = len(monthly_list)
        x = list(range(n))
        y = [float(d['total'] or 0) for d in monthly_list]
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        # Добавляем 3 месяца прогноза
        for i in range(n + 3):
            trend_data.append(round(slope * i + intercept, 2))

    by_category = Property.objects.values('category__name').annotate(cnt=Count('id')).order_by('-cnt')
    by_city = Property.objects.values('city').annotate(cnt=Count('id')).order_by('-cnt')
    by_status = Property.objects.values('status').annotate(cnt=Count('id'))
    by_type = Property.objects.values('transaction_type').annotate(cnt=Count('id'))

    # Топ агенты
    top_agents = Employee.objects.annotate(
        deal_count=Count('deals'),
        deal_sum=Sum('deals__amount')
    ).filter(deal_count__gt=0).order_by('-deal_sum')[:5]

    # Список объектов в алфавитном порядке
    properties_sorted = Property.objects.filter(is_published=True).order_by('title')

    # Список клиентов в алфавитном порядке с суммой покупок
    clients_sorted = Client.objects.annotate(
        deals_count=Count('deals'),
        total_spent=Sum('deals__amount')
    ).order_by('last_name', 'first_name')

    import json
    import calendar as cal_module
    from django.utils import timezone as tz

    utc_now = tz.now()
    local_now = tz.localtime(utc_now)
    text_calendar = cal_module.month(local_now.year, local_now.month)

    # Сериализуем данные для Chart.js в JSON (Decimal и date не сериализуются напрямую)
    def to_json(qs):
        result = []
        for item in qs:
            row = {}
            for k, v in item.items():
                if hasattr(v, 'strftime'):
                    row[k] = v.strftime('%m/%Y')
                else:
                    row[k] = float(v) if hasattr(v, '__float__') else v
            result.append(row)
        return json.dumps(result)

    import json as _json
    trend_json = _json.dumps(trend_data)

    context = {
        'total_amount': total_amount,
        'total_commission': total_commission,
        'avg_amount': avg_amount,
        'median_amount': median_amount,
        'mode_amount': mode_amount,
        'avg_age': avg_age,
        'median_age': median_age,
        'ages_count': len(ages),
        'by_category': to_json(by_category),
        'by_city': to_json(by_city),
        'by_status': to_json(by_status),
        'by_type': to_json(by_type),
        'monthly_deals': to_json(monthly_deals),
        'trend_json': trend_json,
        'trend_months_count': len(monthly_list),
        'top_agents': top_agents,
        'properties_sorted': properties_sorted,
        'clients_sorted': clients_sorted,
        'deals_count': deals.count(),
        'utc_now': utc_now,
        'local_now': local_now,
        'text_calendar': text_calendar,
    }
    return render(request, 'properties/statistics.html', context)


# ===== КЛИЕНТЫ =====

@login_required
def client_list(request):
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:list')
    search = request.GET.get('search', '')
    qs = Client.objects.all()
    if search:
        qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone__icontains=search))
    sort = request.GET.get('sort', 'last_name')
    qs = qs.order_by(sort)
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'properties/client_list.html', {'page_obj': page, 'search': search})


@login_required
def client_create(request):
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:list')
    form = ClientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        client = form.save()
        messages.success(request, 'Клиент добавлен.')
        return redirect('properties:client_list')
    return render(request, 'properties/client_form.html', {'form': form, 'title': 'Добавить клиента'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not (request.user.is_staff or request.user.is_employee()):
        messages.error(request, 'Нет доступа.')
        return redirect('properties:client_list')
    form = ClientForm(request.POST or None, instance=client)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Клиент обновлён.')
        return redirect('properties:client_list')
    return render(request, 'properties/client_form.html', {'form': form, 'title': 'Редактировать клиента', 'client': client})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа.')
        return redirect('properties:client_list')
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Клиент удалён.')
        return redirect('properties:client_list')
    return render(request, 'properties/confirm_delete_client.html', {'client': client})


# ===== ГРАФИК ЧЕРЕЗ PYTHON (matplotlib) =====

import io
import base64
import calendar as cal_module
from django.utils import timezone as tz


def chart_python(request):
    """График средствами Python/matplotlib — НЕ JS."""
    import matplotlib
    matplotlib.use('Agg')  # без GUI
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    from django.db.models.functions import TruncMonth

    # Данные: сделки по месяцам
    from django.db.models import Sum, Count
    deals_qs = Deal.objects.filter(status='completed') \
        .annotate(month=TruncMonth('contract_date')) \
        .values('month').annotate(cnt=Count('id'), total=Sum('amount')) \
        .order_by('month')

    months = [d['month'].strftime('%m/%Y') if d['month'] else '' for d in deals_qs]
    counts = [d['cnt'] for d in deals_qs]
    totals = [float(d['total'] or 0) for d in deals_qs]

    # Если данных нет — добавим заглушку
    if not months:
        months = ['01/2024', '02/2024', '03/2024', '04/2024', '05/2024']
        counts = [2, 3, 1, 4, 2]
        totals = [180000, 250000, 95000, 320000, 160000]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
    fig.suptitle('Статистика сделок (Python/matplotlib)', fontsize=14, fontweight='bold')

    # График 1: количество сделок
    ax1.bar(months, counts, color='#1a3a5c', alpha=0.85)
    ax1.set_title('Количество завершённых сделок по месяцам')
    ax1.set_ylabel('Кол-во сделок')
    ax1.set_xlabel('Месяц')
    for i, v in enumerate(counts):
        ax1.text(i, v + 0.05, str(v), ha='center', fontsize=10, fontweight='bold')

    # График 2: сумма сделок
    ax2.plot(months, totals, marker='o', color='#e67e22', linewidth=2, markersize=8)
    ax2.fill_between(range(len(months)), totals, alpha=0.15, color='#e67e22')
    ax2.set_title('Общая сумма сделок по месяцам (USD)')
    ax2.set_ylabel('Сумма (USD)')
    ax2.set_xlabel('Месяц')
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    for i, v in enumerate(totals):
        ax2.annotate(f'${v:,.0f}', (i, v), textcoords='offset points',
                     xytext=(0, 8), ha='center', fontsize=8)

    plt.tight_layout()

    # Конвертируем в base64 для вставки в HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    chart_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    buf.close()

    # Дополнительно: диаграмма по категориям (pie chart)
    by_cat = Property.objects.values('category__name').annotate(cnt=Count('id'))
    cat_labels = [d['category__name'] for d in by_cat]
    cat_values = [d['cnt'] for d in by_cat]

    fig2, ax = plt.subplots(figsize=(7, 5))
    colors = ['#1a3a5c', '#e67e22', '#27ae60', '#e74c3c', '#3498db', '#9b59b6']
    wedges, texts, autotexts = ax.pie(
        cat_values, labels=cat_labels, autopct='%1.1f%%',
        colors=colors[:len(cat_labels)], startangle=90
    )
    ax.set_title('Распределение объектов по категориям', fontsize=13)

    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', dpi=100, bbox_inches='tight')
    buf2.seek(0)
    pie_b64 = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close(fig2)
    buf2.close()

    # Текстовый календарь (модуль calendar)
    now = tz.localtime(tz.now())
    text_calendar = cal_module.month(now.year, now.month)

    # Информация о таймзоне
    from django.conf import settings as dj_settings
    utc_now = tz.now()  # UTC
    local_now = tz.localtime(utc_now)  # в таймзоне сервера (settings.TIME_ZONE)

    context = {
        'chart_b64': chart_b64,
        'pie_b64': pie_b64,
        'text_calendar': text_calendar,
        'utc_now': utc_now,
        'local_now': local_now,
        'timezone': dj_settings.TIME_ZONE,
        'months': months,
        'counts': counts,
        'totals': totals,
    }
    return render(request, 'properties/chart_python.html', context)
