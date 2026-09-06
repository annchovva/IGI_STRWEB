# parking/tests/test_admin.py
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from datetime import date
from ..admin import CustomUserAdmin, CarAdmin, ParkingSpotAdmin
from ..models import CustomUser, Car, ParkingSpot

User = get_user_model()


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
        self.assertEqual(self.user_admin.search_fields, ('username', 'role'))


class CarAdminTest(TestCase):
    """Тесты админ-панели для автомобилей"""

    def setUp(self):
        self.admin_site = AdminSite()
        self.car_admin = CarAdmin(Car, self.admin_site)
        self.user = User.objects_create_user(
            username='owner',
            email='owner@example.com',
            phone_number='+375 (29) 111-22-33',
            birth_date=date(2000, 1, 1)
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