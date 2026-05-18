from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Review, Car, CustomUser, ParkingSpot, Accrual, Payment
from datetime import datetime, date
import re

User = get_user_model()

# Форма для отзыва
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [ 'rating', 'text' ]
        widgets = {
            'rating' : forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Напишите ваш отзыв здесь...'}),
        }

# Добавление автомобиля (с разграничением прав)
class CarForm(forms.ModelForm):
    owners = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=False, role='client'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Совладельцы",
        required=False,
        error_messages={
            'required': 'Пожалуйста, выберите хотя бы одного клиента из списка.',
            'invalid_choice': 'Выбранный пользователь не существует или недоступен.'
        }
    )
    class Meta:
        model = Car
        fields = [ 'brand', 'model_name', 'license_plate', 'owners', 'current_spot' ]
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'current_spot': forms.Select(attrs={'class': 'form-control'}),
        }    
        error_messages = {
            'license_plate': {
                'unique': "Автомобиль с таким номером уже есть в базе.",
            }
        }    

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CarForm, self).__init__(*args, **kwargs)

        self.fields['owners'].empty_label = None 
        if (self.user and self.user.is_staff):
            self.fields['owners'].required = True
            self.fields['owners'].help_text = "Вы должны выбрать хотя бы одного клиента в качестве владельца."
        else:
            self.fields['owners'].required = False
            self.fields['owners'].help_text = "Вы будете добавлены как владелец автоматически. Можно выбрать совладельцев."

        occupied_spots = Car.objects.exclude(pk=self.instance.pk).filter(current_spot__isnull=False).values_list('current_spot_id', flat=True)
        self.fields['current_spot'].queryset = ParkingSpot.objects.exclude(id__in=occupied_spots)
        self.fields['current_spot'].label = "Выберите свободное место"  
        self.fields['current_spot'].empty_label = "Не припаркован"


# Форма регистрации
class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Для регистрации вам должно быть больше 18 лет."
    )
    phone_number = forms.CharField(
        label="Номер телефона",
        max_length=20,
        help_text="Формат: +375 (XX) XXX-XX-XX",
        widget=forms.TextInput(attrs={'placeholder': '+375 (__) ___-__-__', 'class': 'form-control'})
    )
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'birth_date')

        help_texts = {
            'username': "Используйте буквы, цифры и символы @/./+/-/_.",
        }

    # Валидация возраста
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 18:
                raise ValidationError("Регистрация разрешена только лицам старше 18 лет.")
            if birth_date.year < 1900:
                raise ValidationError("Пожалуйста, введите корректный год рождения.")
            if birth_date > today:
                raise ValidationError("Дата рождения не может быть в будущем.")
        return birth_date

    # Валидация телефона 
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        pattern = r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, phone):
            raise ValidationError("Введите номер в формате +375 (XX) XXX-XX-XX")
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  
        self.fields['password1'].help_text = "Пароль должен быть сложным."
      
# Изменение цены
class PriceUpdateForm(forms.ModelForm):
    price = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            'invalid': "Введите корректное число.",
            'min_value': "Цена не может быть отрицательной!",
            'required': "Поле не может быть пустым!"
        },
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm', 
            'style': 'width: 100px; display: inline-block;',
            'step': '0.01',
            'min': '0.01'
        })
    )
    class Meta:
        model = ParkingSpot
        fields = ['price']

# Создание начисления 
class AccrualForm(forms.ModelForm):
    class Meta:
        model = Accrual
        fields = ['car', 'amount', 'month', 'year']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2100}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError("Сумма начисления должна быть строго больше нуля.")
        return amount

    def clean_month(self):
        month = self.cleaned_data.get('month')
        if month < 1 or month > 12:
            raise ValidationError("Месяц должен быть в диапазоне от 1 до 12.")
        return month

    def clean_year(self):
        year = self.cleaned_data.get('year')
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 5:
            raise ValidationError(f"Указан некорректный год ({year}).")
        return year    

# Создание платежа
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['car', 'amount']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise ValidationError("Сумма платежа должна быть строго больше нуля.")
        return amount      
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['car'].queryset = user.cars.all()              