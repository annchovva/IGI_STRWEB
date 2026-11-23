from django.urls import path, include
from . import views
from django.urls import path, re_path

urlpatterns = [
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('services/', views.services_catalog, name='services_catalog'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('services/<int:service_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/<int:service_id>/increase/', views.cart_increase, name='cart_increase'),
    path('cart/<int:service_id>/decrease/', views.cart_decrease, name='cart_decrease'),
    path('cart/<int:service_id>/remove/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('', views.home, name='home'), # Главная страница
    path('news/', views.news_list, name='news_list'), # Страница новостей
    re_path(r'^news/(?P<news_id>[0-9]+)/$', views.news_detail, name='news_detail'),
    path('about/', views.about, name='about'), # О компании
    path('terms/', views.term_list, name='term_list'), # Ваши вопросы
    path('contacts/', views.employee_list, name='employee_list'), # Сотрудники
    path('privacy/', views.privacy_policy, name='privacy_policy'), # Пока пустая страница
    path('vacancies/', views.vacancy_list, name='vacancy_list'), # Вакансии
    path('promocodes/', views.promo_list, name='promo_list'), # Промокоды
    path('reviews/', views.review_list, name='review_list'), # Отзывы
    # Управление автомобилями
    path('cars/', views.car_index, name='car_index'), 
    path('cars/create/', views.car_create, name='car_create'),  
    path('cars/edit/<int:id>/', views.car_edit, name='car_edit'),
    path('cars/delete/<int:id>/', views.car_delete, name='car_delete'),
    # Регистрация
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
]