"""Модульные проверки валидаторов, форм и локальной бизнес-логики."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase

from parking.forms import (
    AccrualForm,
    CustomUserCreationForm,
    PaymentForm,
    PriceUpdateForm,
    ReviewForm,
)
from parking.models import Car, ParkingSpot, PromoCode, license_regex, phone_regex
from parking.views import home, is_admin


User = get_user_model()


class ValidatorUnitTests(SimpleTestCase):
    """Параметризованные проверки изолированных валидаторов модели."""

    def test_phone_validator_accepts_supported_operator_codes(self):
        # Arrange
        valid_phones = [
            "+375 (25) 123-45-67",
            "+375 (29) 123-45-67",
            "+375 (33) 123-45-67",
            "+375 (44) 123-45-67",
        ]

        for phone in valid_phones:
            with self.subTest(phone=phone):
                # Act / Assert
                phone_regex(phone)

    def test_phone_validator_rejects_invalid_formats(self):
        # Arrange
        invalid_phones = [
            "+375 (17) 123-45-67",
            "+375291234567",
            "375 (29) 123-45-67",
            "+375 (29) 12-345-67",
            "",
        ]

        for phone in invalid_phones:
            with self.subTest(phone=phone):
                # Act / Assert
                with self.assertRaises(ValidationError):
                    phone_regex(phone)

    def test_license_validator_accepts_and_rejects_parameter_sets(self):
        # Arrange
        cases = [
            ("A123BC", True),
            ("AA-1234", True),
            ("123 ABC", True),
            ("a123bc", False),
            ("A_123", False),
            ("А123ВС", False),
            ("", False),
        ]

        for license_plate, is_valid in cases:
            with self.subTest(license_plate=license_plate):
                # Act / Assert
                if is_valid:
                    license_regex(license_plate)
                else:
                    with self.assertRaises(ValidationError):
                        license_regex(license_plate)


class PromoCodeUnitTests(SimpleTestCase):
    def test_clean_rejects_reversed_validity_period(self):
        # Arrange
        promo = PromoCode(
            code="REVERSED",
            discount_percent=10,
            valid_from=date(2026, 12, 31),
            valid_until=date(2026, 1, 1),
        )

        # Act / Assert
        with self.assertRaises(ValidationError):
            promo.clean()

    def test_clean_accepts_equal_boundary_dates(self):
        # Arrange
        promo = PromoCode(
            code="ONE-DAY",
            discount_percent=10,
            valid_from=date(2026, 10, 15),
            valid_until=date(2026, 10, 15),
        )

        # Act / Assert
        promo.clean()


class RolePredicateUnitTests(SimpleTestCase):
    def test_is_admin_for_parameterized_role_flags(self):
        # Arrange
        cases = [
            (True, True, True),
            (True, False, False),
            (False, True, False),
            (False, False, False),
        ]

        for is_authenticated, is_superuser, expected in cases:
            with self.subTest(
                is_authenticated=is_authenticated,
                is_superuser=is_superuser,
            ):
                user = SimpleNamespace(
                    is_authenticated=is_authenticated,
                    is_superuser=is_superuser,
                )

                # Act
                result = is_admin(user)

                # Assert
                self.assertEqual(result, expected)


class HomeViewUnitTests(SimpleTestCase):
    """View проверяется изолированно от ORM, шаблонизатора и HTTP-сервиса."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_weather_tips_are_selected_for_parameterized_weather(self):
        # Arrange
        cases = [
            ("Rain", 10, "Идет дождь"),
            ("Snow", -2, "Снегопад"),
            ("Clear", 30, "Сегодня жарко"),
            ("Clear", -15, "На улице мороз"),
            ("Clear", 15, "Погода отличная"),
        ]

        for status, temperature, expected_tip_part in cases:
            with self.subTest(status=status, temperature=temperature):
                news = SimpleNamespace(content="Первая новость. Продолжение")
                weather_response = Mock(status_code=200)
                weather_response.json.return_value = {
                    "main": {"temp": temperature},
                    "weather": [
                        {
                            "main": status,
                            "description": "ясно",
                            "icon": "01d",
                        }
                    ],
                }
                rendered_response = HttpResponse("rendered")

                with (
                    patch("parking.views.News.objects.first", return_value=news),
                    patch("parking.views.Car.objects.count", return_value=7),
                    patch("parking.views.requests.get", return_value=weather_response),
                    patch("parking.views.render", return_value=rendered_response) as render_mock,
                ):
                    # Act
                    result = home(self.factory.get("/"))

                # Assert
                self.assertIs(result, rendered_response)
                context = render_mock.call_args.args[2]
                self.assertIn(expected_tip_part, context["weather_tip"])
                self.assertEqual(context["cars_count"], 7)
                self.assertEqual(news.short_content, "Первая новость.")

    def test_non_successful_weather_response_hides_weather_block(self):
        # Arrange
        weather_response = Mock(status_code=503)

        with (
            patch("parking.views.News.objects.first", return_value=None),
            patch("parking.views.Car.objects.count", return_value=0),
            patch("parking.views.requests.get", return_value=weather_response),
            patch("parking.views.render", return_value=HttpResponse("rendered")) as render_mock,
        ):
            # Act
            home(self.factory.get("/"))

        # Assert
        context = render_mock.call_args.args[2]
        self.assertIsNone(context["weather"])

class CustomUserCreationFormTest(TestCase):
    """Тесты формы регистрации"""

    def test_valid_form_creates_user(self):
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'birth_date': '2000-01-01',
            'privacy_agreement': True,
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.role, 'client')
        self.assertFalse(user.is_staff)

    def test_invalid_birth_date_under_18(self):
        form_data = {
            'username': 'younguser',
            'email': 'young@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'birth_date': '2010-01-01',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_invalid_phone_format(self):
        form_data = {
            'username': 'badphone',
            'email': 'bad@example.com',
            'phone_number': '12345',
            'birth_date': '2000-01-01',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_passwords_mismatch(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '+375 (29) 123-45-67',
            'birth_date': '2000-01-01',
            'password1': 'StrongPass123',
            'password2': 'DifferentPass456',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class ReviewFormTest(TestCase):
    """Тесты формы отзыва"""

    def test_valid_review(self):
        form_data = {
            'rating': 5,
            'text': 'Great service!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_rating(self):
        form_data = {
            'rating': '',
            'text': 'Great service!'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_missing_text(self):
        form_data = {
            'rating': 5,
            'text': ''
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_rating_out_of_range(self):
        # Django choices автоматически проверит, что rating из choices
        form_data = {
            'rating': 6,
            'text': 'Great service!'
        }
        form = ReviewForm(data=form_data)
        # ModelChoiceField проверяет допустимость значения до сохранения модели.
        self.assertFalse(form.is_valid())


class PriceUpdateFormTest(TestCase):
    """Тесты формы обновления цены"""

    def test_valid_price(self):
        form = PriceUpdateForm(data={'price': 1500.00})
        self.assertTrue(form.is_valid())

    def test_zero_price_invalid(self):
        form = PriceUpdateForm(data={'price': 0})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_negative_price_invalid(self):
        form = PriceUpdateForm(data={'price': -100})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_non_numeric_price_invalid(self):
        form = PriceUpdateForm(data={'price': 'abc'})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)


class AccrualFormTest(TestCase):
    """Тесты формы начислений"""

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

    def test_valid_accrual_form(self):
        form_data = {
            'car': self.car.id,
            'amount': 100.00,
            'month': 5,
            'year': 2025
        }
        form = AccrualForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_zero_amount_invalid(self):
        form_data = {
            'car': self.car.id,
            'amount': 0,
            'month': 5,
            'year': 2025
        }
        form = AccrualForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_negative_amount_invalid(self):
        form_data = {
            'car': self.car.id,
            'amount': -50,
            'month': 5,
            'year': 2025
        }
        form = AccrualForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_invalid_month(self):
        form_data = {
            'car': self.car.id,
            'amount': 100,
            'month': 13,
            'year': 2025
        }
        form = AccrualForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('month', form.errors)

    def test_invalid_year(self):
        form_data = {
            'car': self.car.id,
            'amount': 100,
            'month': 5,
            'year': 1999
        }
        form = AccrualForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)


class PaymentFormTest(TestCase):
    """Тесты формы платежа"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='client',
            email='client@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1)
        )
        self.car = Car.objects.create(
            brand='Toyota',
            model_name='Camry',
            license_plate='A123BC'
        )
        self.car.owners.add(self.user)

    def test_valid_payment_form(self):
        form_data = {
            'car': self.car.id,
            'amount': 500.00
        }
        form = PaymentForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_zero_amount_invalid(self):
        form_data = {
            'car': self.car.id,
            'amount': 0
        }
        form = PaymentForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_negative_amount_invalid(self):
        form_data = {
            'car': self.car.id,
            'amount': -100
        }
        form = PaymentForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
