from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date

# Специальные валидации
phone_regex = RegexValidator(
    regex=r'^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$',
    message="Номер телефона должен быть в формате: +375 (29) XXX-XX-XX"
)
license_regex = RegexValidator(
    regex=r'^[A-Z0-9\- ]+$',
    message="Гос. номер может содержать только заглавные буквы, цифры и дефис"
)

class CustomUser(AbstractUser):
    """Пользователь"""
    
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('staff', 'Сотрудник'),
        ('admin', 'Администратор'),
    ]
    
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=20,
        verbose_name="Номер телефона",
        help_text="Формат: +375 (29) XXX-XX-XX",
        null=True,
        blank=False
    )
    birth_date = models.DateField(
        null=True, 
        blank=False, 
        verbose_name="Дата рождения"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Роль"
    )
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    # Валидация возраста 
    def clean(self):
        super().clean()
        if self.birth_date:
            today = date.today()

            if self.birth_date > today:
                raise ValidationError({'birth_date': 'Дата не может быть в будущем.'})
            
            if self.birth_date.year < 1900:
                raise ValidationError({'birth_date': 'Введите корректный год рождения.'})

            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1

            if age < 18:
                raise ValidationError(
                    {'birth_date': 'Возраст должен быть 18 лет или старше.'}
                )
    
    # Если роль = сотрудник - is_staff 
    def save(self, *args, **kwargs):
        if self.role == 'staff' or self.role == 'admin':
            self.is_staff = True
        else:
            self.is_staff = False

        if self.role == 'admin':
            self.is_superuser = True        

        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class ParkingSpot(models.Model):
    """Парковочное место"""
    
    number = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        verbose_name="Номер места",
        help_text="Номера места от 1 до 999"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Цена за месяц"
    )
    is_occupied = models.BooleanField(
        default=False,
        verbose_name="Занято"
    )

    class Meta:
        verbose_name = "Парковочное место"
        verbose_name_plural = "Парковочные места"
        ordering = ['number']
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Место {self.number} ({self.price} руб.)"

class Car(models.Model):
    """Автомобиль"""
    
    brand = models.CharField(
        max_length=50, 
        verbose_name="Марка"
    )
    model_name = models.CharField(
        max_length=100, 
        verbose_name="Модель"
    )
    license_plate = models.CharField(
        max_length=15, 
        unique=True, 
        validators=[license_regex],
        verbose_name="Гос. номер"
    )
    owners = models.ManyToManyField(
        CustomUser, 
        limit_choices_to={'is_staff': False},
        related_name='cars', 
        verbose_name="Владельцы"

    )
    current_spot = models.OneToOneField(
        ParkingSpot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_car',
        verbose_name="Текущее парковочное место"
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ['license_plate']
    
    # Изменение поля is_occupied в парковочном месте 
    def save(self, *args, **kwargs):
        # Проверяем есть ли уже машина в бд
        if self.pk:
            old_car = Car.objects.get(pk=self.pk)
            if old_car.current_spot and old_car.current_spot != self.current_spot:
                # Освобождаем старое место
                old_car.current_spot.is_occupied = False
                old_car.current_spot.save()

        if self.current_spot:
            # Новое место помечаем как занятое
            self.current_spot.is_occupied = True
            self.current_spot.save()
        self.full_clean()
        super().save(*args, **kwargs)

    # При удалении машины освобождаем место
    def delete(self, *args, **kwargs):
        if self.current_spot:
            self.current_spot.is_occupied = False
            self.current_spot.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.license_plate})"

class Accrual(models.Model):
    """Начисление"""
    
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE, 
        related_name='accruals',
        verbose_name="Автомобиль"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="Сумма начисления"
    )
    date = models.DateField(
        auto_now_add=True, 
        verbose_name="Дата начисления"
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Месяц", 
        help_text="1-12"
    )
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2020)],
        verbose_name="Год"
    )
    
    class Meta:
        # Чтобы нельзя было создать два начисления за один месяц
        unique_together = ['car', 'year', 'month']
        ordering = ['-year', '-month']
        verbose_name = "Начисление"
        verbose_name_plural = "Начисления"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Начисление {self.car} за {self.month:02d}/{self.year}"

class Payment(models.Model):
    """Платёж"""
    
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name="Автомобиль"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="Сумма платежа"
    )
    date = models.DateField(
        auto_now_add=True, 
        verbose_name="Дата платежа"
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ['-date']
    
    def save(self, *args, **kwargs): 
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Платёж {self.amount} по авто {self.car}"

class CompanyInfo(models.Model):
    """Информация о компании"""

    name = models.CharField(
        max_length=100, 
        verbose_name="Название компании"
    )
    description = models.TextField(
        verbose_name="Описание компании"
    )
    main_logo = models.ImageField(
        upload_to='company/', 
        verbose_name="Главный логотип", 
        blank=True, 
        null=True
    )
    logo = models.ImageField(
        upload_to='company/', 
        verbose_name="Логотип",
        blank=True, 
        null=True
    )
    address = models.CharField(
        max_length=255, 
        verbose_name="Адрес", 
        blank=True
    )
    email = models.EmailField(
        verbose_name="Электронная почта", 
        blank=True
    )

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return self.name

class News(models.Model):
    """Новости"""

    title = models.CharField(
        max_length=200, 
        verbose_name="Заголовок"
    )
    content = models.TextField(
        verbose_name="Содержание"
    )
    image = models.ImageField(
        upload_to='news/', 
        null=True, 
        blank=True, 
        verbose_name="Изображение"
    )
    published_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата публикации"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Дата изменения"
    )
    class Meta:
        ordering = ['-published_at']
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
    
    def __str__(self):
        return self.title

class Term(models.Model):
    """Словарь терминов"""

    term = models.CharField(
        max_length=100, 
        verbose_name="Термин"
    )
    definition = models.TextField(
        verbose_name="Определение"
    )
    added_at = models.DateField(
        auto_now_add=True, 
        verbose_name="Дата добавления"
    )
    
    class Meta:
        verbose_name = "Термин"
        verbose_name_plural = "Словарь терминов"
        ordering = ['term']
    
    def __str__(self):
        return self.term

class Employee(models.Model):
    """Сотрудник"""

    photo = models.ImageField(
        upload_to='employees/', 
        null=True, 
        blank=True, 
        verbose_name="Фото"
    )
    name = models.CharField(
        max_length=100, 
        verbose_name="ФИО"
    )
    position = models.CharField(
        max_length=100, 
        verbose_name="Должность"
    )
    phone = models.CharField(
        max_length=20, 
        verbose_name="Телефон"
    )
    email = models.EmailField(
        verbose_name="Email"
    )
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.position}"

class Vacancy(models.Model):
    """Вакансия"""

    title = models.CharField(
        max_length=100, 
        verbose_name="Название"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    requirements = models.TextField(
        verbose_name="Требования"
    )
    salary = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Зарплата"
    )
    
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
    
    def __str__(self):
        return self.title

class Review(models.Model):
    """Отзыв клиента"""

    author = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Автор отзыва"
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], 
        verbose_name="Оценка (1-5)"
    )
    text = models.TextField(
        verbose_name="Текст отзыва"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at'] 
    
    def __str__(self):
        return f"Отзыв от {self.author.username} (оценка: {self.rating})"

class PromoCode(models.Model):
    """Промокод"""

    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Код"
    )
    discount_percent = models.IntegerField(
        verbose_name="Скидка %", 
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="От 1 до 100"
    )
    valid_from = models.DateField(
        verbose_name="Действует с"
    )
    valid_until = models.DateField(
        verbose_name="Действует до"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Активен"
    )
    
    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
    
    # Проверяем корректность срока действия промокода
    def clean(self):
        if self.valid_from > self.valid_until:
            raise ValidationError('Дата начала не может быть позже даты окончания')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "Активен" if self.is_active else "Архив"
        return f"{self.code} ({self.discount_percent}%) - {status}"

class Category(models.Model):
    """Категории услуг"""

    name = models.CharField(
        max_length=100, 
        verbose_name="Название категории"
    )

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"

    def __str__(self):
        return self.name

class Service(models.Model):
    """Сами услуги"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE, 
        related_name='services', 
        verbose_name="Категория"
    )
    name = models.CharField(
        max_length=100, 
        verbose_name="Название услуги"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
    is_additional = models.BooleanField(
        default=False, 
        verbose_name="Дополнительная услуга"
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)    

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"
