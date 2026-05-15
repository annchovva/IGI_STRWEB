from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from .models import News, CompanyInfo, Term, Employee, Vacancy, PromoCode, Review

def home(request):
    # Берем последнюю новость
    latest_news = News.objects.first()

    if latest_news:
        latest_news.short_content = latest_news.content.split('.')[0] + '.'

    # Передаем эту новость в шаблон news
    context = {
        'news': latest_news
    }

    return render(request, 'parking/home.html', context)

def news_list(request):
    # Забираем все новости из базы данных
    all_news = News.objects.all()

    for item in all_news:
        item.short_content = item.content.split('.')[0] + '.'

    return render(request, 'parking/news_list.html', {'news_items': all_news})

def about(request):
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
        valid_until__gte=today
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
        if request.user.is_authenticated:
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