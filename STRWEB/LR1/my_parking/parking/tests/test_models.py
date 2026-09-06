# parking/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal
from ..models import (
    CustomUser, ParkingSpot, Car, Accrual, Payment,
    News, Term, Employee, Vacancy, Review, PromoCode
)

User = get_user_model()


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
        spot = ParkingSpot.objects.create(number=5, price=3500.00)
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
        self.user = User.objects_create_user(
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