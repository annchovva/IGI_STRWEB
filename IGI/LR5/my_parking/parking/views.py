from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count, Q, F, Value, DecimalField, Subquery, OuterRef, Avg
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .forms import ReviewForm, CarForm, CustomUserCreationForm, PriceUpdateForm, AccrualForm, PaymentForm
from .models import News, CompanyInfo, Term, Employee, Vacancy, PromoCode, Review, Car, CustomUser, ParkingSpot, Accrual, Payment, Service, Category
from datetime import datetime, date
import requests
import statistics
import calendar
from django.conf import settings
import matplotlib
matplotlib.use('Agg')  # Важно: используем неинтерактивный бэкенд для серверов
import matplotlib.pyplot as plt
import io
import base64

def home(request):
    # Берем последнюю новость
    latest_news = News.objects.first()
    cars_count = Car.objects.count()

    now_utc = timezone.now()  # Текущее время в UTC
    now_local = timezone.localtime(now_utc)  # Локальное время (из settings.TIME_ZONE)
    
    # Генерация текстового календаря на текущий месяц
    cal = calendar.TextCalendar(calendar.MONDAY)
    text_calendar = cal.formatmonth(now_local.year, now_local.month)

    weather_data = None
    weather_tip = ""
    city = "Minsk"
    api_key = "63026ab9f90f2307525287f3f1e967df" # Используйте свой ключ или этот (если он активен)
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        response = requests.get(url, timeout=2) # Таймаут 2 сек, чтобы сайт не завис
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            weather_data = {
                'temp': round(temp),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon']
            }
            
            # Генерация совета на основе температуры
            if temp > 25:
                weather_tip = "Сегодня жарко. Ваша машина может перегреться, рекомендуем парковку в тени или крытый паркинг."
            elif temp < -10:
                weather_tip = "На улице мороз. Проверьте заряд аккумулятора перед поездкой."
            elif 'осадки' in data['weather'][0]['description'] or 'дождь' in data['weather'][0]['description']:
                weather_tip = "Ожидаются осадки. Будьте осторожны на дорогах и закройте люк."
            else:
                weather_tip = "Погода отличная для поездки!"
    except:
        weather_data = None

    if latest_news:
        latest_news.short_content = latest_news.content.split('.')[0] + '.'

    # Передаем эту новость в шаблон news
    context = {
        'news': latest_news,
        'cars_count': cars_count,
        'weather': weather_data,
        'weather_tip': weather_tip,
        'now_utc': now_utc,
        'now_local': now_local,
        'text_calendar': text_calendar,
    }

    return render(request, 'parking/home.html', context)

def news_list(request):
    # Забираем все новости из базы данных
    all_news = News.objects.all()

    # Для вывода одного предложения
    for item in all_news:
        item.short_content = item.content.split('.')[0] + '.'

    return render(request, 'parking/news_list.html', {'news_items': all_news})

def news_detail(request, news_id):
    # Получаем новость по ID или выдаем 404, если не найдена
    news = get_object_or_404(News, id=news_id)
    return render(request, 'parking/news_detail.html', {'news': news})

def about(request):
    # Первую запись
    company_data = CompanyInfo.objects.first()
    return render(request, 'parking/about.html', {'company': company_data})

def term_list(request):
    terms = Term.objects.all()
    return render(request, 'parking/term_list.html', {'terms': terms})

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'parking/employee_list.html', {'employees': employees})

def privacy_policy(request):
    return render(request, 'parking/privacy_policy.html')

def vacancy_list(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'parking/vacancy_list.html', {'vacancies': vacancies})

def promo_list(request):
    today = timezone.now().date()

    active_promos = PromoCode.objects.filter(
        is_active=True,
        valid_until__gte=today # Включая сегодняшнюю дату
    ).order_by('-valid_until')

    archived_promos = PromoCode.objects.filter(
        Q(is_active = False) | Q(valid_until__lt=today)
    ).order_by('-valid_until')

    return render(request, 'parking/promo_list.html', {
        'active_promos': active_promos,
        'archived_promos': archived_promos
    })

def review_list(request):
    reviews = Review.objects.all()

    if request.method == 'POST':
        if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.author = request.user
                review.save()
                return redirect('review_list')
        else:
            return redirect('login')
    else:
        form = ReviewForm()  

    return render(request, 'parking/review_list.html', {
        'reviews': reviews,
        'form': form
    })     

# READ
def car_index(request):
    if request.user.is_staff:
        cars = Car.objects.all()
    else:
        cars = Car.objects.filter(owners=request.user)    
    return render(request, 'parking/car_index.html', {'cars': cars})

#CREATE
@login_required
def car_create(request):
    if request.method == 'POST':
        form = CarForm(request.POST, user=request.user)
        if form.is_valid():
            car = form.save()
            if not request.user.is_staff:
                if request.user not in car.owners.all():
                    car.owners.add(request.user)
            return redirect("car_index")
    else:
        form = CarForm(user=request.user)
    return render(request, "parking/car_form.html", {"form": form, "title": "Добавить автомобиль"})

#UPDATE
@login_required
def car_edit(request, id):
    car = get_object_or_404(Car, id=id)

    if not request.user.is_staff and request.user not in car.owners.all():
        raise PermissionDenied
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car, user=request.user)
        if form.is_valid():
            car = form.save()
            if not request.user.is_staff and request.user not in car.owners.all():
                car.owners.add(request.user)
            return redirect('car_index')
    else:
        form = CarForm(instance=car, user=request.user)
    return render(request, 'parking/car_form.html', {'form': form, 'title': "Редактировать"})    

#DELETE
@login_required
def car_delete(request, id):
    car = get_object_or_404(Car, id=id)
    
    if not request.user.is_staff and request.user not in car.owners.all():
        raise PermissionDenied

    if request.method == 'POST':
        car.delete()
        return redirect('car_index')
    
    return redirect('car_index')

# Регистрация
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})  

def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Данные для панели администратора
@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_panel(request):
    # Изменение цены
    if request.method == 'POST' and 'update_price' in request.POST:
        spot_id = request.POST.get('spot_id')
        spot = get_object_or_404(ParkingSpot, id=spot_id)
        form = PriceUpdateForm(request.POST, instance=spot)
        if form.is_valid():
            form.save()
            messages.success(request, f"Цена для места №{spot.number} обновлена.")
            return redirect('admin_panel')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
            return redirect('admin_panel')    

    # Для фильтрации
    params = {
        'start_date': request.GET.get('start_date', '2020-01-01'),
        'end_date': request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d')),
        'user_search': request.GET.get('user_search', ''),
        'user_sort': request.GET.get('user_sort', 'username'),
        'brand': request.GET.get('brand', ''),
    }
    
    # Самый большой долг
    user_accruals_sub = Accrual.objects.filter(car__owners=OuterRef('pk')).values('car__owners').annotate(
        total=Sum('amount')
    ).values('total')

    user_payments_sub = Payment.objects.filter(car__owners=OuterRef('pk')).values('car__owners').annotate(
        total=Sum('amount')
    ).values('total')

    top_debtor = CustomUser.objects.filter(role='client').annotate(
        total_accruals=Coalesce(Subquery(user_accruals_sub, output_field=DecimalField()), Value(0, output_field=DecimalField())),
        total_payments=Coalesce(Subquery(user_payments_sub, output_field=DecimalField()), Value(0, output_field=DecimalField()))
    ).annotate(
        debt=F('total_accruals') - F('total_payments')
    ).filter(debt__gt=0).order_by('-debt').first()    

    last_payment_date = "Нет платежей"
    if top_debtor:
        last_payment = Payment.objects.filter(car__owners=top_debtor).order_by('-date').first()
        if last_payment:
            last_payment_date = last_payment.date
            
    # Общий долг за период
    t_accruals = Accrual.objects.filter(date__range=[params['start_date'], params['end_date']]).aggregate(Sum('amount'))['amount__sum'] or 0
    t_payments = Payment.objects.filter(date__range=[params['start_date'], params['end_date']]).aggregate(Sum('amount'))['amount__sum'] or 0
    total_debt = t_accruals - t_payments
    
    # Несколько владельцев
    shared_cars = Car.objects.annotate(cnt=Count('owners')).filter(cnt__gt=1)

    # Минимальный долг за период
    car_accruals_sub = Accrual.objects.filter(
        car=OuterRef('pk'), 
        date__range=[params['start_date'], params['end_date']]
    ).values('car').annotate(total=Sum('amount')).values('total')

    car_payments_sub = Payment.objects.filter(
        car=OuterRef('pk'), 
        date__range=[params['start_date'], params['end_date']]
    ).values('car').annotate(total=Sum('amount')).values('total')

    min_debt_car = Car.objects.annotate(
        period_accruals=Coalesce(Subquery(car_accruals_sub, output_field=DecimalField()), Value(0, output_field=DecimalField())),
        period_payments=Coalesce(Subquery(car_payments_sub, output_field=DecimalField()), Value(0, output_field=DecimalField()))
    ).annotate(
        period_debt=F('period_accruals') - F('period_payments')
    ).order_by('period_debt').first()

    branded_cars = []
    if params['brand']:
        branded_cars = Car.objects.filter(brand__icontains=params['brand']).prefetch_related('owners')

    # Список клиентов
    clients_list = CustomUser.objects.filter(role='client')
    if params['user_search']:
        clients_list = clients_list.filter(Q(username__icontains=params['user_search']) | Q(phone_number__icontains=params['user_search']))
    clients_list = clients_list.order_by(params['user_sort'])

    spots_list = ParkingSpot.objects.all()

    # Статистика по платежам
    payments_qs = Payment.objects.values_list('amount', flat=True)
    payments_list = list(payments_qs)
    
    stats_payments = {
        'avg': round(statistics.mean(payments_list), 2) if payments_list else 0,
        'median': round(statistics.median(payments_list), 2) if payments_list else 0,
        'mode': 0
    }
    if payments_list:
        try:
            stats_payments['mode'] = statistics.mode(payments_list)
        except statistics.StatisticsError:
            stats_payments['mode'] = "Нет"

    # Статистика по возрасту   
    today = date.today()
    birth_dates = CustomUser.objects.filter(role='client', birth_date__isnull=False).values_list('birth_date', flat=True)
    ages = [today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day)) for bday in birth_dates]
    
    stats_ages = {
        'avg': round(statistics.mean(ages), 1) if ages else 0,
        'median': statistics.median(ages) if ages else 0
    }  

    # Самая популярная марка
    popular_brand_data = Car.objects.values('brand').annotate(count=Count('id')).order_by('-count').first()
    popular_brand = popular_brand_data['brand'] if popular_brand_data else "—"

    # Самая прибыльная  
    profitable_brand_data = Car.objects.annotate(brand_revenue=Sum('payments__amount')).order_by('-brand_revenue').first()
    profitable_brand = f"{profitable_brand_data.brand} ({profitable_brand_data.brand_revenue} руб.)" if profitable_brand_data and profitable_brand_data.brand_revenue else "—"   

    # Визуализация
    brand_revenue_qs = Car.objects.values('brand').annotate(
        total_rev=Sum('payments__amount')
    ).filter(total_rev__gt=0) # Берем только те, где есть доход

    graphic = None
    if brand_revenue_qs:
        labels = [item['brand'] for item in brand_revenue_qs]
        values = [float(item['total_rev']) for item in brand_revenue_qs]

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, shadow=True)
        ax.set_title("Распределение доходов по маркам автомобилей")  

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig) 

        graphic = base64.b64encode(image_png).decode('utf-8')

    context = {
        **params, 
        'top_debtor': top_debtor,
        'total_debt': total_debt,
        'clients_list': clients_list,
        'spots_list': spots_list,
        'shared_cars': shared_cars,
        'min_debt_car': min_debt_car, 
        'branded_cars': branded_cars,
        'stats_payments': stats_payments,
        'stats_ages': stats_ages,
        'popular_brand': popular_brand,
        'profitable_brand': profitable_brand,
        'graphic': graphic,
    }
    return render(request, 'parking/admin_panel.html', context)

@login_required
def dashboard(request):
    user = request.user

    if user.role == 'staff':
        if request.method == 'POST' and 'create_accrual' in request.POST:
            form = AccrualForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Начисление успешно создано!")
                return redirect('dashboard')
            else:
                messages.error(request, "Ошибка в данных начисления. Проверьте введенные значения.")
        else:
            form = AccrualForm()

        all_accruals = Accrual.objects.all().select_related('car')
        all_payments = Payment.objects.all().select_related('car')
        
        context = {
            'total_sales': Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
            'recent_payments': all_payments[:10],
            'all_payments': all_payments,
            'all_accruals': all_accruals,
            'clients': CustomUser.objects.filter(role='client'),
            'total_spots': ParkingSpot.objects.count(),
            'occupied_spots': ParkingSpot.objects.filter(is_occupied=True).count(),
            'accrual_form': form,
        }
        context['free_spots'] = context['total_spots'] - context['occupied_spots']
        return render(request, 'dashboard_staff.html', context)

    else:
        if request.method == 'POST' and 'make_payment' in request.POST:
            form = PaymentForm(request.POST, user=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Оплата произведена успешно!")
                return redirect('dashboard')
            else:
                messages.error(request, "Ошибка при совершении платежа.")
        else:
            form = PaymentForm(user=user)

        my_cars = user.cars.all()
        cars_data = []
        for car in my_cars:
            accruals = car.accruals.all()
            payments = car.payments.all()
            total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
            total_accrued = accruals.aggregate(Sum('amount'))['amount__sum'] or 0
            
            cars_data.append({
                'car': car,
                'accruals': accruals,
                'payments': payments,
                'balance': total_paid - total_accrued
            })
        
        return render(request, 'dashboard_client.html', {
            'cars_data': cars_data,
            'payment_form': form
        })
    
def get_nbrb_rates():
    try:
        response = requests.get('https://www.nbrb.by/api/exrates/rates?periodicity=0', timeout=5)
        if response.status_code == 200:
            rates_data = response.json()
            needed_cur = ['USD', 'EUR', 'RUB']
            rates = {item['Cur_Abbreviation']: item for item in rates_data if item['Cur_Abbreviation'] in needed_cur}
            return rates
    except Exception:
        return None
    return None    

def services_catalog(request):
    categories = Category.objects.all()
    services = Service.objects.all()

    cat_id = request.GET.get('category')
    min_p_raw = request.GET.get('min_price', '')
    max_p_raw = request.GET.get('max_price', '')
    
    min_p = None
    max_p = None

    try:
        if min_p_raw:
            min_p = float(min_p_raw)
            if min_p < 0:
                messages.error(request, "Цена 'от' не может быть отрицательной.")
                min_p = None

        if max_p_raw:
            max_p = float(max_p_raw)
            if max_p < 0:
                messages.error(request, "Цена 'до' не может быть отрицательной.")
                max_p = None

        if min_p is not None and max_p is not None and min_p > max_p:
            messages.error(request, "Цена 'от' не может быть больше цены 'до'.")
            min_p, max_p = None, None
            
    except ValueError:
        messages.error(request, "Пожалуйста, введите корректные числа в поля цен.")
        min_p, max_p = None, None

    if cat_id:
        services = services.filter(category_id=cat_id)
    if min_p is not None:
        services = services.filter(price__gte=min_p)
    if max_p is not None:
        services = services.filter(price__lte=max_p)        

    promo_codes = PromoCode.objects.filter(is_active=True)

    context = {
        'services': services,
        'categories': categories,
        'promo_codes': promo_codes,
        'selected_cat': cat_id,
        'min_p_val': min_p,
        'max_p_val': max_p,
    }
    return render(request, 'services_catalog.html', context)