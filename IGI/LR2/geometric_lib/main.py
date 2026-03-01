import os
import circle
import square

# Получаем данные извне (Docker -e)
r = float(os.getenv("RADIUS", "5"))
a = float(os.getenv("SIDE", "10"))

print(f"--- Расчеты для Круга (R={r}) ---")
print(f"Площадь: {circle.area(r):.2f}, Периметр: {circle.perimeter(r):.2f}")
print(f"--- Расчеты для Квадрата (A={a}) ---")
print(f"Площадь: {square.area(a):.2f}, Периметр: {square.perimeter(a):.2f}")



