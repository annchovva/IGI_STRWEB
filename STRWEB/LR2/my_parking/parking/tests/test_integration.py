"""Интеграционные проверки Django, БД, маршрутов и внешнего HTTP-вызова."""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from parking.admin import CarAdmin, CustomUserAdmin, ParkingSpotAdmin
from parking.models import (
    Accrual,
    Car,
    Category,
    CustomUser,
    Employee,
    News,
    ParkingSpot,
    Payment,
    PromoCode,
    Review,
    Service,
    Term,
    Vacancy,
)


User = get_user_model()


def create_user(username, role="client"):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        phone_number="+375 (29) 123-45-67",
        birth_date=date(1990, 1, 1),
        password="StrongPass123!",
        role=role,
    )


class WeatherHttpIntegrationTests(TestCase):
    """HTTP-зависимость заменена заглушкой на границе requests.get."""

    def test_home_uses_weather_http_stub_and_renders_received_data(self):
        # Arrange
        http_stub = Mock(status_code=200)
        http_stub.json.return_value = {
            "main": {"temp": 18.6},
            "weather": [
                {"main": "Clear", "description": "ясно", "icon": "01d"}
            ],
        }

        with patch("parking.views.requests.get", return_value=http_stub) as get_mock:
            # Act
            response = self.client.get(reverse("home"))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["weather"]["temp"], 19)
        self.assertEqual(response.context["weather"]["description"], "Ясно")
        called_url = get_mock.call_args.args[0]
        self.assertIn("api.openweathermap.org", called_url)
        self.assertIn("q=Minsk", called_url)
        self.assertEqual(get_mock.call_args.kwargs["timeout"], 5)

    def test_home_remains_available_when_weather_http_call_fails(self):
        # Arrange
        weather_error = requests.Timeout("weather timeout")

        with patch("parking.views.requests.get", side_effect=weather_error):
            # Act
            response = self.client.get(reverse("home"))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["weather"])


class DatabaseIntegrationTests(TestCase):
    def setUp(self):
        self.owner = create_user("db-owner")
        self.spot = ParkingSpot.objects.create(
            number=201,
            price=Decimal("150.00"),
        )
        self.car = Car.objects.create(
            brand="Toyota",
            model_name="Corolla",
            license_plate="DB-201",
            current_spot=self.spot,
        )
        self.car.owners.add(self.owner)

    def test_related_financial_records_are_persisted_and_aggregated(self):
        # Arrange
        Accrual.objects.create(
            car=self.car,
            amount=Decimal("300.00"),
            month=10,
            year=2026,
        )
        Payment.objects.create(car=self.car, amount=Decimal("125.00"))

        # Act
        total_accrued = sum(item.amount for item in self.car.accruals.all())
        total_paid = sum(item.amount for item in self.car.payments.all())

        # Assert
        self.assertEqual(total_accrued, Decimal("300.00"))
        self.assertEqual(total_paid, Decimal("125.00"))
        self.assertEqual(total_paid - total_accrued, Decimal("-175.00"))

    def test_duplicate_monthly_accrual_is_rejected(self):
        # Arrange
        Accrual.objects.create(
            car=self.car,
            amount=Decimal("100.00"),
            month=10,
            year=2026,
        )

        # Act / Assert
        with self.assertRaises(ValidationError):
            Accrual.objects.create(
                car=self.car,
                amount=Decimal("200.00"),
                month=10,
                year=2026,
            )

    def test_deleting_car_cascades_financial_records_and_frees_spot(self):
        # Arrange
        Accrual.objects.create(
            car=self.car,
            amount=Decimal("100.00"),
            month=9,
            year=2026,
        )
        Payment.objects.create(car=self.car, amount=Decimal("50.00"))
        car_id = self.car.pk

        # Act
        self.car.delete()
        self.spot.refresh_from_db()

        # Assert
        self.assertFalse(Car.objects.filter(pk=car_id).exists())
        self.assertFalse(Accrual.objects.filter(car_id=car_id).exists())
        self.assertFalse(Payment.objects.filter(car_id=car_id).exists())
        self.assertFalse(self.spot.is_occupied)


class ServiceCatalogIntegrationTests(TestCase):
    def setUp(self):
        self.basic = Category.objects.create(name="Базовые")
        self.extra = Category.objects.create(name="Дополнительные")
        self.cheap = Service.objects.create(
            category=self.basic,
            name="Эконом",
            description="Недорогая услуга",
            price=Decimal("50.00"),
        )
        self.middle = Service.objects.create(
            category=self.basic,
            name="Стандарт",
            description="Средняя услуга",
            price=Decimal("100.00"),
        )
        self.expensive = Service.objects.create(
            category=self.extra,
            name="Премиум",
            description="Дорогая услуга",
            price=Decimal("200.00"),
            is_additional=True,
        )

    def test_filters_are_parameterized_by_category_and_price_range(self):
        # Arrange
        cases = [
            ({"category": self.basic.pk}, {"Эконом", "Стандарт"}),
            ({"min_price": "100"}, {"Стандарт", "Премиум"}),
            ({"max_price": "100"}, {"Эконом", "Стандарт"}),
            (
                {
                    "category": self.basic.pk,
                    "min_price": "60",
                    "max_price": "150",
                },
                {"Стандарт"},
            ),
        ]

        for query, expected_names in cases:
            with self.subTest(query=query):
                # Act
                response = self.client.get(reverse("services_catalog"), query)
                actual_names = {
                    service.name for service in response.context["services"]
                }

                # Assert
                self.assertEqual(response.status_code, 200)
                self.assertSetEqual(actual_names, expected_names)

    def test_invalid_price_filters_do_not_filter_data_or_crash(self):
        # Arrange
        invalid_queries = [
            {"min_price": "-1"},
            {"max_price": "-1"},
            {"min_price": "200", "max_price": "100"},
            {"min_price": "not-a-number"},
        ]

        for query in invalid_queries:
            with self.subTest(query=query):
                # Act
                response = self.client.get(reverse("services_catalog"), query)

                # Assert
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["services"].count(), 3)


class ReviewIntegrationTests(TestCase):
    def test_authenticated_client_post_creates_review_in_database(self):
        # Arrange
        client_user = create_user("review-author")
        self.client.force_login(client_user)

        # Act
        response = self.client.post(
            reverse("review_list"),
            {"rating": 5, "text": "Отличная парковка"},
        )

        # Assert
        self.assertRedirects(response, reverse("review_list"))
        review = Review.objects.get(author=client_user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Отличная парковка")


class CustomUserModelTest(TestCase):
    """Тесты модели CustomUser"""

    def setUp(self):
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'birth_date': date(2000, 1, 1),
            'password': 'testpass123'
        }

    def test_create_client_sets_is_staff_false(self):
        """При создании клиента is_staff = False"""
        user = User.objects.create_user(**self.valid_user_data)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, 'client')

    def test_create_staff_sets_is_staff_true(self):
        """При создании сотрудника is_staff = True"""
        user = User.objects.create_user(**self.valid_user_data, role='staff')
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, 'staff')

    def test_create_admin_sets_is_superuser_true(self):
        """При создании администратора is_superuser = True"""
        user = User.objects.create_user(**self.valid_user_data, role='admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'admin')

    def test_age_validation_under_18_raises_error(self):
        """Пользователь младше 18 лет не может быть создан"""
        user = User(
            username='young',
            email='young@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2010, 1, 1)
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_phone_validation_invalid_format_raises_error(self):
        """Неверный формат телефона вызывает ошибку"""
        user = User(
            username='badphone',
            email='bad@example.com',
            phone_number='12345',
            birth_date=date(2000, 1, 1)
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_phone_validation_valid_format_passes(self):
        """Верный формат телефона проходит валидацию"""
        user = User(
            username='goodphone',
            email='good@example.com',
            phone_number='+375 (29) 123-45-67',
            birth_date=date(2000, 1, 1)
        )
        user.set_password('testpass123')
        try:
            user.full_clean()
        except ValidationError:
            self.fail('ValidationError raised')

    def test_birth_date_in_future_raises_error(self):
        """Дата рождения в будущем недопустима"""
        tomorrow = date.today() + timedelta(days=1)
        user = User(
            username='future',
            email='future@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=tomorrow
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_str_method(self):
        user = User.objects.create_user(**self.valid_user_data)
        self.assertEqual(str(user), f"{user.username} (Клиент)")


class ParkingSpotModelTest(TestCase):
    """Тесты модели ParkingSpot"""

    def test_number_validation_out_of_range_raises_error(self):
        """Номер места должен быть от 1 до 999"""
        spot = ParkingSpot(number=1000, price=100)
        with self.assertRaises(ValidationError):
            spot.full_clean()

    def test_number_validation_lower_bound_passes(self):
        spot = ParkingSpot(number=1, price=100)
        try:
            spot.full_clean()
        except ValidationError:
            self.fail('ValidationError raised for number=1')

    def test_number_validation_upper_bound_passes(self):
        spot = ParkingSpot(number=999, price=100)
        try:
            spot.full_clean()
        except ValidationError:
            self.fail('ValidationError raised for number=999')

    def test_number_unique_constraint(self):
        """Номера мест должны быть уникальными"""
        ParkingSpot.objects.create(number=1, price=100)
        spot2 = ParkingSpot(number=1, price=200)
        with self.assertRaises(ValidationError):
            spot2.full_clean()

    def test_price_validation_negative_raises_error(self):
        """Цена не может быть отрицательной"""
        spot = ParkingSpot(number=1, price=-10)
        with self.assertRaises(ValidationError):
            spot.full_clean()

    def test_price_validation_zero_raises_error(self):
        """Цена не может быть нулевой"""
        spot = ParkingSpot(number=1, price=0)
        with self.assertRaises(ValidationError):
            spot.full_clean()

    def test_str_method(self):
        spot = ParkingSpot.objects.create(number=5, price=Decimal('3500.00'))
        self.assertEqual(str(spot), "Место 5 (3500.00 руб.)")


class CarModelTest(TestCase):
    """Тесты модели Car"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1)
        )
        self.spot = ParkingSpot.objects.create(number=1, price=100)

    def test_car_creation_requires_owner(self):
        """Автомобиль должен иметь хотя бы одного владельца"""
        car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        car.owners.add(self.user)
        self.assertEqual(car.owners.count(), 1)
        self.assertEqual(car.owners.first().username, 'owner')

    def test_car_current_spot_updates_occupancy(self):
        """При установке current_spot место становится занятым"""
        car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        car.owners.add(self.user)
        car.current_spot = self.spot
        car.save()

        self.spot.refresh_from_db()
        self.assertTrue(self.spot.is_occupied)

    def test_license_plate_unique_constraint(self):
        """Гос. номера должны быть уникальными"""
        Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        car2 = Car(
            brand='BMW',
            model_name='X5',
            license_plate='A123BC'
        )
        with self.assertRaises(ValidationError):
            car2.full_clean()

    def test_license_plate_validator_passes(self):
        car = Car(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        try:
            car.full_clean()
        except ValidationError:
            self.fail('ValidationError raised for valid license plate')

    def test_str_method(self):
        car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        car.owners.add(self.user)
        self.assertEqual(str(car), "Toyota Camry (A123BC)")


class AccrualModelTest(TestCase):
    """Тесты модели Accrual"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1)
        )
        self.car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        self.car.owners.add(self.user)

    def test_accrual_amount_must_be_positive(self):
        """Сумма начисления должна быть больше 0"""
        accrual = Accrual(car=self.car, amount=0, month=1, year=2025)
        with self.assertRaises(ValidationError):
            accrual.full_clean()

    def test_accrual_amount_positive_passes(self):
        accrual = Accrual(car=self.car, amount=100, month=1, year=2025)
        try:
            accrual.full_clean()
        except ValidationError:
            self.fail('ValidationError raised for positive amount')

    def test_accrual_month_validation_lower_bound(self):
        accrual = Accrual(car=self.car, amount=100, month=0, year=2025)
        with self.assertRaises(ValidationError):
            accrual.full_clean()

    def test_accrual_month_validation_upper_bound(self):
        accrual = Accrual(car=self.car, amount=100, month=13, year=2025)
        with self.assertRaises(ValidationError):
            accrual.full_clean()

    def test_accrual_unique_together(self):
        """Нельзя создать два начисления за один месяц для одного авто"""
        Accrual.objects.create(car=self.car, amount=100, month=1, year=2025)
        accrual2 = Accrual(car=self.car, amount=200, month=1, year=2025)
        with self.assertRaises(ValidationError):
            accrual2.full_clean()

    def test_str_method(self):
        accrual = Accrual.objects.create(car=self.car, amount=100, month=5, year=2025)
        self.assertEqual(str(accrual), f"Начисление {self.car} за 05/2025")


class PaymentModelTest(TestCase):
    """Тесты модели Payment"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='testpass123'
        )
        self.car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        self.car.owners.add(self.user)

    def test_payment_amount_must_be_positive(self):
        payment = Payment(car=self.car, amount=0)
        with self.assertRaises(ValidationError):
            payment.full_clean()

    def test_payment_amount_positive_passes(self):
        payment = Payment(car=self.car, amount=100)
        try:
            payment.full_clean()
        except ValidationError:
            self.fail('ValidationError raised for positive amount')

    def test_str_method(self):
        payment = Payment.objects.create(car=self.car, amount=500)
        self.assertEqual(str(payment), f"Платёж 500 по авто {self.car}")


class ReviewModelTest(TestCase):
    """Тесты модели Review"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            email='review@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1)
        )

    def test_rating_choices_invalid_raises_error(self):
        review = Review(author=self.user, rating=6, text='Test')
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_choices_valid_passes(self):
        for rating in range(1, 6):
            review = Review(author=self.user, rating=rating, text='Test')
            try:
                review.full_clean()
            except ValidationError:
                self.fail(f'ValidationError raised for rating={rating}')

    def test_str_method(self):
        review = Review.objects.create(
            author=self.user,
            rating=5,
            text='Great service!'
        )
        self.assertEqual(str(review), f"Отзыв от {self.user.username} (оценка: 5)")


class PromoCodeModelTest(TestCase):
    """Тесты модели PromoCode"""

    def setUp(self):
        self.today = date.today()
        self.next_week = self.today + timedelta(days=7)
        self.prev_week = self.today - timedelta(days=7)

    def test_discount_percent_validation_lower_bound(self):
        promo = PromoCode(
            code='TEST1',
            discount_percent=0,
            valid_from=self.today,
            valid_until=self.next_week
        )
        with self.assertRaises(ValidationError):
            promo.full_clean()

    def test_discount_percent_validation_upper_bound(self):
        promo = PromoCode(
            code='TEST1',
            discount_percent=101,
            valid_from=self.today,
            valid_until=self.next_week
        )
        with self.assertRaises(ValidationError):
            promo.full_clean()

    def test_valid_from_after_valid_until_raises_error(self):
        promo = PromoCode(
            code='TEST1',
            discount_percent=10,
            valid_from=self.next_week,
            valid_until=self.today
        )
        with self.assertRaises(ValidationError):
            promo.full_clean()

    def test_str_method_active(self):
        promo = PromoCode.objects.create(
            code='SUMMER2024',
            discount_percent=20,
            valid_from=self.today,
            valid_until=self.next_week,
            is_active=True
        )
        self.assertEqual(str(promo), "SUMMER2024 (20%) - Активен")


class CustomUserAdminTest(TestCase):
    """Тесты админ-панели для пользователей"""

    def setUp(self):
        self.admin_site = AdminSite()
        self.user_admin = CustomUserAdmin(CustomUser, self.admin_site)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='testpass123'
        )

    def test_list_display(self):
        self.assertEqual(
            self.user_admin.list_display,
            ['username', 'email', 'phone_number', 'birth_date', 'role', 'is_staff']
        )

    def test_list_filter(self):
        self.assertEqual(self.user_admin.list_filter, ['role', 'is_staff'])

    def test_search_fields(self):
        self.assertEqual(
            self.user_admin.search_fields,
            ('username', 'email', 'phone_number', 'role')
        )


class CarAdminTest(TestCase):
    """Тесты админ-панели для автомобилей"""

    def setUp(self):
        self.admin_site = AdminSite()
        self.car_admin = CarAdmin(Car, self.admin_site)
        self.user = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1),
            password='testpass123'
        )

    def test_list_display(self):
        self.assertIn('license_plate', self.car_admin.list_display)
        self.assertIn('brand', self.car_admin.list_display)
        self.assertIn('model_name', self.car_admin.list_display)

    def test_owner_names_method(self):
        car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='TEST123'
        )
        car.owners.add(self.user)
        result = self.car_admin.owner_names(car)
        self.assertEqual(result, self.user.username)


class ParkingSpotAdminTest(TestCase):
    """Тесты админ-панели для парковочных мест"""

    def setUp(self):
        self.admin_site = AdminSite()
        self.spot_admin = ParkingSpotAdmin(ParkingSpot, self.admin_site)

    def test_list_display(self):
        self.assertIn('number', self.spot_admin.list_display)
        self.assertIn('price', self.spot_admin.list_display)
        self.assertIn('is_occupied', self.spot_admin.list_display)

    def test_current_car_info_method(self):
        spot = ParkingSpot.objects.create(number=5, price=1000)
        result = self.spot_admin.current_car_info(spot)
        self.assertEqual(result, "-")  # нет машины


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

    @patch('parking.views.requests.get')
    def test_home_page(self, weather_get_mock):
        # Arrange: внешний HTTP-вызов заменён локальной заглушкой.
        weather_get_mock.return_value = Mock(status_code=503)

        # Act
        response = self.client.get(reverse('home'))

        # Assert
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
            'privacy_agreement': True,
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
