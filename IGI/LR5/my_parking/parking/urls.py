from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Главная страница
    path('news/', views.news_list, name='news_list'), # Страница новостей
    path('about/', views.about, name='about'), # О компании
    path('terms/', views.term_list, name='term_list'), # Отзывы
    path('contacts/', views.employee_list, name='employee_list'), # Сотрудники
    path('privacy/', views.privacy_policy, name='privacy_policy'), # Пока пустая страница
    path('vacancies/', views.vacancy_list, name='vacancy_list'), # Вакансии
    path('promocodes/', views.promo_list, name='promo_list'), # Промокоды
    path('reviews/', views.review_list, name='review_list'), # Отзывы
]