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
            'rating' : forms.Select(),
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Напишите ваш отзыв здесь...'}),
        }

# Добавление автомобиля (с разграничением прав)
class CarForm(forms.ModelForm):
    owners = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=False, role='client'),
        widget=forms.SelectMultiple(),
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
            'brand': forms.TextInput(),
            'model_name': forms.TextInput(),
            'license_plate': forms.TextInput(),
            'current_spot': forms.Select(),
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
    field_order = (
        'username',
        'email',
        'phone_number',
        'birth_date',
        'password1',
        'password2',
        'privacy_agreement',
    )

    privacy_agreement = forms.BooleanField(
        label="Я принимаю политику конфиденциальности",
        required=True,
        error_messages={
            "required": (
                "Для регистрации необходимо принять "
                "политику конфиденциальности."
            )
        }
    )

    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Для регистрации вам должно быть больше 18 лет."
    )
    phone_number = forms.CharField(
        label="Номер телефона",
        max_length=20,
        help_text="Формат: +375 (XX) XXX-XX-XX",
        widget=forms.TextInput(attrs={'placeholder': '+375 (__) ___-__-__'})
    )
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'birth_date', 'privacy_agreement', )

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
            'car': forms.Select(),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'min': 2020, 'max': 2100}),
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
            'car': forms.Select(),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
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

class CheckoutForm(forms.Form):
    """Форма учебной оплаты заказа."""

    current_year = date.today().year

    month_choices = [
        (str(month), f'{month:02d}')
        for month in range(1, 13)
    ]

    year_choices = [
        (str(year), str(year))
        for year in range(current_year, current_year + 11)
    ]

    full_name = forms.CharField(
        max_length=150,
        label='Имя плательщика',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'name',
                'placeholder': 'Иван Иванов',
            }
        ),
    )

    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': 'user@example.com',
            }
        ),
    )

    phone = forms.RegexField(
        regex=r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$',
        label='Номер телефона',
        error_messages={
            'invalid': (
                'Введите номер в формате '
                '+375 (29) 123-45-67.'
            ),
        },
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'tel',
                'placeholder': '+375 (29) 123-45-67',
            }
        ),
    )

    card_number = forms.CharField(
        min_length=16,
        max_length=19,
        label='Номер карты',
        widget=forms.TextInput(
            attrs={
                'inputmode': 'numeric',
                'autocomplete': 'cc-number',
                'placeholder': 'Введите 16 цифр',
                'pattern': '[0-9]{16}',
                'maxlength': '16',
                'oninput': (
                    "this.value = this.value"
                    ".replace(/[^0-9]/g, '')"
                    ".slice(0,16);"
                ),
            }
        ),
    )

    expiry_month = forms.ChoiceField(
        choices=month_choices,
        label='Месяц окончания действия',
    )

    expiry_year = forms.ChoiceField(
        choices=year_choices,
        label='Год окончания действия',
    )

    cvv = forms.CharField(
        min_length=3,
        max_length=3,
        label='Защитный код CVV',
        widget=forms.TextInput(
            attrs={
                'inputmode': 'numeric',
                'autocomplete': 'cc-csc',
                'placeholder': '123',
                'pattern': '[0-9]{3}',
                'oninput': (
                    "this.value = this.value"
                    ".replace(/[^0-9]/g, '')"
                    ".slice(0,3);"
                ),
            }
        ),
    )

    agreement = forms.BooleanField(
        required=True,
        label=(
            'Я подтверждаю правильность данных '
            'и согласен с условиями оплаты'
        ),
    )

    def clean_card_number(self):
        """Проверка номера карты алгоритмом Луна."""

        card_number = self.cleaned_data['card_number']

        if not card_number.isdigit():
            raise forms.ValidationError(
                'Номер карты должен содержать только цифры.'
            )

        if len(card_number) != 16:
            raise forms.ValidationError(
                'Номер карты должен содержать 16 цифр.'
            )

        digits = [
            int(character)
            for character in card_number
        ]

        checksum = 0
        parity = len(digits) % 2

        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2

                if digit > 9:
                    digit -= 9

            checksum += digit

        if checksum % 10 != 0:
            raise forms.ValidationError(
                'Введён некорректный номер карты.'
            )

        return card_number

    def clean_cvv(self):
        """CVV должен состоять из трёх цифр."""

        cvv = self.cleaned_data['cvv']

        if not cvv.isdigit():
            raise forms.ValidationError(
                'CVV должен состоять из трёх цифр.'
            )

        return cvv

    def clean(self):
        """Проверка срока действия карты."""

        cleaned_data = super().clean()

        expiry_month = cleaned_data.get('expiry_month')
        expiry_year = cleaned_data.get('expiry_year')

        if not expiry_month or not expiry_year:
            return cleaned_data

        today = date.today()
        month = int(expiry_month)
        year = int(expiry_year)

        if year == today.year and month < today.month:
            self.add_error(
                'expiry_month',
                'Срок действия карты уже истёк.',
            )

        return cleaned_data
