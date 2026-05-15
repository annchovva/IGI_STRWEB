from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, ParkingSpot, Car, Accrual, Payment,
    CompanyInfo, News, Term, Employee, Vacancy, Review, PromoCode
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительная информация", {'fields' : ('phone_number', 'birth_date', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Дополнительная информация", {'fields': ('phone_number', 'birth_date', 'role')}),
    )

admin.site.register(ParkingSpot)
admin.site.register(Car)
admin.site.register(Accrual)
admin.site.register(Payment)
admin.site.register(CompanyInfo)
admin.site.register(News)            
admin.site.register(Term)
admin.site.register(Employee)
admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(PromoCode)
