# parking/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from ..models import News, Term, Employee, Vacancy, Review, Car, ParkingSpot

User = get_user_model()


class PublicPagesTest(TestCase):
    """Тесты публичных страниц (доступны всем)"""

    def setUp(self):
        self.today = date.today()
        News.objects.create(
            title='Test News',
            content='Test content.',
            published_at=self.today
        )
        Term.objects.create(
            term='Test Term',
            definition='Test definition'
        )
        Employee.objects.create(
            name='John Doe',
            position='Manager',
            phone='+375 (29) 111-22-33',
            email='john@example.com'
        )
        Vacancy.objects.create(
            title='Developer',
            description='Python developer',
            requirements='Django experience'
        )
        self.user = User.objects.create_user(
            username='reviewer',
            email='review@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1)
        )
        Review.objects.create(
            author=self.user,
            rating=5,
            text='Great!'
        )
        ParkingSpot.objects.create(number=1, price=100)
        ParkingSpot.objects.create(number=2, price=150)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_news_list_page(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test News')

    def test_news_detail_page(self):
        news = News.objects.first()
        response = self.client.get(reverse('news_detail', args=[news.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, news.title)

    def test_term_list_page(self):
        response = self.client.get(reverse('term_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Term')

    def test_employee_list_page(self):
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_vacancy_list_page(self):
        response = self.client.get(reverse('vacancy_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Developer')

    def test_review_list_page(self):
        response = self.client.get(reverse('review_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Great!')

    def test_promo_list_page(self):
        response = self.client.get(reverse('promo_list'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy_page(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)

    def test_services_catalog_page(self):
        response = self.client.get(reverse('services_catalog'))
        self.assertEqual(response.status_code, 200)


class CarViewsTest(TestCase):
    """Тесты CRUD для автомобилей"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='client',
            email='client@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='testpass123'
        )
        self.spot = ParkingSpot.objects.create(number=1, price=100)

    def test_car_index_redirects_if_not_logged_in(self):
        """Неавторизованный → редирект на логин"""
        response = self.client.get(reverse('car_index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('car_index')}")

    def test_car_index_logged_in(self):
        """Авторизованный клиент видит список своих авто"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('car_index'))
        self.assertEqual(response.status_code, 200)

    def test_car_create_get(self):
        """Страница создания доступна авторизованному"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('car_create'))
        self.assertEqual(response.status_code, 200)

    def test_car_create_post_valid(self):
        """Создание автомобиля"""
        self.client.force_login(self.user)
        response = self.client.post(reverse('car_create'), {
            'brand': 'Toyota',
            'model_name': 'Camry',
            'license_plate': 'TEST123',
            'current_spot': '',
        })
        # Редирект после успешного создания
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Car.objects.filter(license_plate='TEST123').exists())


class AuthViewsTest(TestCase):
    """Тесты аутентификации"""

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'birth_date': '2000-01-01',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        # Редирект на страницу входа после успешной регистрации
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_invalid_age(self):
        response = self.client.post(reverse('register'), {
            'username': 'younguser',
            'email': 'young@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'birth_date': '2010-01-01',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertEqual(response.status_code, 200)  # форма с ошибкой
        self.assertFalse(User.objects.filter(username='younguser').exists())

    def test_register_invalid_phone(self):
        response = self.client.post(reverse('register'), {
            'username': 'badphone',
            'email': 'bad@example.com',
            'phone_number': '12345',
            'birth_date': '2000-01-01',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='badphone').exists())

    def test_login_valid_credentials(self):
        # Сначала создадим пользователя
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='testpass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Редирект после успешного входа
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # форма с ошибкой


class DashboardViewsTest(TestCase):
    """Тесты дашбордов (роли)"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username='client',
            email='client@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='testpass123',
            role='client'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(1990, 1, 1),
            password='testpass123',
            role='staff'
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_client_accessible(self):
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_staff_accessible(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_client_can_make_payment(self):
        self.client.force_login(self.client_user)
        car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='ABC123'
        )
        car.owners.add(self.client_user)
        response = self.client.post(reverse('dashboard'), {
            'make_payment': '1',
            'car': car.id,
            'amount': 500
        })
        self.assertEqual(response.status_code, 302)  # редирект после оплаты

    def test_staff_can_create_accrual(self):
        self.client.force_login(self.staff_user)
        car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='ABC123'
        )
        car.owners.add(self.client_user)
        response = self.client.post(reverse('dashboard'), {
            'create_accrual': '1',
            'car': car.id,
            'amount': 100,
            'month': 5,
            'year': 2025
        })
        self.assertEqual(response.status_code, 302)  # редирект после создания


class AdminPanelTest(TestCase):
    """Тесты админ-панели"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(1990, 1, 1),
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='userpass123'
        )

    def test_admin_panel_redirects_for_regular_user(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 302)  # редирект (нет прав)

    def test_admin_panel_accessible_for_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)

    def test_update_price_post(self):
        self.client.force_login(self.admin_user)
        spot = ParkingSpot.objects.create(number=10, price=500)
        response = self.client.post(reverse('admin_panel'), {
            'update_price': '1',
            'spot_id': spot.id,
            'price': 750
        })
        self.assertEqual(response.status_code, 302)  # редирект после обновления
        spot.refresh_from_db()
        self.assertEqual(spot.price, 750)