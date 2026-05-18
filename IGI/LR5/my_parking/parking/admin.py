from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, ParkingSpot, Car, Accrual, Payment, CompanyInfo, 
    News, Term, Employee, Vacancy, Review, PromoCode, Service, Category
)

# Редактирование связанных моделей в родительской модели
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

class AccrualInline(admin.TabularInline):
    model = Accrual
    extra = 1
    fields = ('month', 'year', 'amount') 

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1       

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'birth_date', 'role', 'is_staff']
    list_filter = ['role', 'is_staff']

    # К стандартным полям добавляем свои 
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительная информация", {'fields' : ('phone_number', 'birth_date', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Дополнительная информация", {'fields': ('phone_number', 'birth_date', 'role')}),
    )
    search_fields = ('username', 'email', 'phone_number', 'role')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'model_name', 'current_spot', 'owner_names')
    list_filter = ('brand', 'current_spot') 
    search_fields = ('license_plate', 'brand', 'model_name')

    inlines = [AccrualInline, PaymentInline]

    # Одним запросом все связные данные
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('owners').select_related('current_spot')

    def owner_names(self, obj):
        return ", ".join([user.username for user in obj.owners.all()]) 
    
    owner_names.short_description = "Владельцы"

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('number', 'price', 'is_occupied', 'current_car_info')
    list_filter = ('is_occupied',)
    search_fields = ('number',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('current_car')

    def current_car_info(self, obj):
        car = getattr(obj, 'current_car', None)
        if car:
            return f"{car.license_plate} ({car.brand} {car.model_name})"
        return "-"
    current_car_info.short_description = "Текущий автомобиль"

@admin.register(Accrual)
class AccrualAdmin(admin.ModelAdmin):
    list_display = ('car', 'month', 'year', 'amount', 'date')
    list_filter = ('year', 'month', 'car__brand')
    search_fields = ('car__license_plate',) 

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('car', 'amount', 'date')
    list_filter = ('date', 'car__brand')       
    search_fields = ('car__license_plate',) 

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    list_filter = ('published_at',)
    search_fields = ('title', 'content')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'phone')
    search_fields = ('name', 'position')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('author',)

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'valid_until')
    search_fields = ('code',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ServiceInline] 

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_additional')
    list_filter = ('category', 'is_additional')
    search_fields = ('name',)

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'address')

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'added_at')
    search_fields = ('term',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary')
