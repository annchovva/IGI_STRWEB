"""Сценарные проверки переходов между состояниями сущностей."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from parking.models import Accrual, Car, ParkingSpot, Payment


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


class CarLifecycleScenarioTests(TestCase):
    """Сценарий из диаграммы состояний лабораторной работы №1."""

    def setUp(self):
        self.owner = create_user("lifecycle-owner")
        self.first_spot = ParkingSpot.objects.create(
            number=301,
            price=Decimal("100.00"),
        )
        self.second_spot = ParkingSpot.objects.create(
            number=302,
            price=Decimal("120.00"),
        )
        self.client.force_login(self.owner)

    def test_full_car_lifecycle_through_http_endpoints(self):
        # Arrange: автомобиль отсутствует, оба места свободны.
        self.assertFalse(Car.objects.filter(license_plate="FLOW-301").exists())
        self.assertFalse(self.first_spot.is_occupied)
        self.assertFalse(self.second_spot.is_occupied)

        # Act 1: создать автомобиль без места.
        create_response = self.client.post(
            reverse("car_create"),
            {
                "brand": "Toyota",
                "model_name": "Prius",
                "license_plate": "FLOW-301",
                "current_spot": "",
            },
        )

        # Assert 1: состояние «Зарегистрирован без места».
        self.assertRedirects(create_response, reverse("car_index"))
        car = Car.objects.get(license_plate="FLOW-301")
        self.assertIn(self.owner, car.owners.all())
        self.assertIsNone(car.current_spot)

        # Act 2: назначить первое свободное место.
        assign_response = self.client.post(
            reverse("car_edit", args=[car.pk]),
            {
                "brand": car.brand,
                "model_name": car.model_name,
                "license_plate": car.license_plate,
                "current_spot": self.first_spot.pk,
            },
        )

        # Assert 2: состояние «Припаркован».
        self.assertRedirects(assign_response, reverse("car_index"))
        car.refresh_from_db()
        self.first_spot.refresh_from_db()
        self.assertEqual(car.current_spot, self.first_spot)
        self.assertTrue(self.first_spot.is_occupied)

        # Act 3: перейти на другое свободное место.
        move_response = self.client.post(
            reverse("car_edit", args=[car.pk]),
            {
                "brand": car.brand,
                "model_name": car.model_name,
                "license_plate": car.license_plate,
                "current_spot": self.second_spot.pk,
            },
        )

        # Assert 3: старое место свободно, новое занято.
        self.assertRedirects(move_response, reverse("car_index"))
        car.refresh_from_db()
        self.first_spot.refresh_from_db()
        self.second_spot.refresh_from_db()
        self.assertEqual(car.current_spot, self.second_spot)
        self.assertFalse(self.first_spot.is_occupied)
        self.assertTrue(self.second_spot.is_occupied)

        # Act 4: снять назначение места.
        unassign_response = self.client.post(
            reverse("car_edit", args=[car.pk]),
            {
                "brand": car.brand,
                "model_name": car.model_name,
                "license_plate": car.license_plate,
                "current_spot": "",
            },
        )

        # Assert 4: автомобиль снова зарегистрирован без места.
        self.assertRedirects(unassign_response, reverse("car_index"))
        car.refresh_from_db()
        self.second_spot.refresh_from_db()
        self.assertIsNone(car.current_spot)
        self.assertFalse(self.second_spot.is_occupied)

        # Act 5: снова назначить место и удалить автомобиль.
        car.current_spot = self.first_spot
        car.save()
        delete_response = self.client.post(reverse("car_delete", args=[car.pk]))

        # Assert 5: конечное состояние, запись удалена, место освобождено.
        self.assertRedirects(delete_response, reverse("car_index"))
        self.first_spot.refresh_from_db()
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())
        self.assertFalse(self.first_spot.is_occupied)


class FinancialFlowScenarioTests(TestCase):
    """Сценарий: начисление сотрудником → платёж клиентом → новый баланс."""

    def setUp(self):
        self.client_user = create_user("financial-client")
        self.staff_user = create_user("financial-staff", role="staff")
        self.car = Car.objects.create(
            brand="Volkswagen",
            model_name="Golf",
            license_plate="FLOW-401",
        )
        self.car.owners.add(self.client_user)

    def test_accrual_then_payment_changes_client_balance(self):
        # Arrange
        self.assertEqual(Accrual.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

        # Act 1: сотрудник создаёт начисление.
        self.client.force_login(self.staff_user)
        accrual_response = self.client.post(
            reverse("dashboard"),
            {
                "create_accrual": "1",
                "car": self.car.pk,
                "amount": "300.00",
                "month": 10,
                "year": 2026,
            },
        )

        # Assert 1
        self.assertRedirects(accrual_response, reverse("dashboard"))
        self.assertTrue(
            Accrual.objects.filter(
                car=self.car,
                amount=Decimal("300.00"),
                month=10,
                year=2026,
            ).exists()
        )

        # Act 2: клиент регистрирует частичный платёж.
        self.client.force_login(self.client_user)
        payment_response = self.client.post(
            reverse("dashboard"),
            {
                "make_payment": "1",
                "car": self.car.pk,
                "amount": "125.00",
            },
        )

        # Assert 2
        self.assertRedirects(payment_response, reverse("dashboard"))
        self.assertTrue(
            Payment.objects.filter(
                car=self.car,
                amount=Decimal("125.00"),
            ).exists()
        )

        # Act 3: клиент повторно открывает кабинет.
        dashboard_response = self.client.get(reverse("dashboard"))
        car_data = dashboard_response.context["cars_data"][0]

        # Assert 3: 125 - 300 = -175.
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(car_data["car"], self.car)
        self.assertEqual(car_data["balance"], Decimal("-175.00"))
