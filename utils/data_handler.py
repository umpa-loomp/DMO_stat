"""Модуль для централізованої обробки введення та базової обробки даних"""
# Загальні статистичні константи

min_values = 3  # Мінімальна кількість значень для тесту

# Рівні значущості
SIGNIFICANCE = {
    "p_values": {
        "0.1%": 0.001,
        "1%": 0.01,
        "2%": 0.02,
        "5%": 0.05,
        "10%": 0.1,
        "15%": 0.15,
        "20%": 0.2
    },
    "indices": {
        "0.1%": 0,
        "1%": 1,
        "2%": 2,
        "5%": 3,
        "10%": 4,
        "15%": 5,
        "20%": 6
    }
}

# Критичні значення Shapiro
SHAPIRO_CRITICAL_VALUES = {
    "1%": {
        10: 0.781, 11: 0.792, 12: 0.805, 13: 0.814, 
        14: 0.825, 15: 0.835, 16: 0.844
    },
    "2%": {
        10: 0.806, 11: 0.817, 12: 0.828, 13: 0.837, 
        14: 0.846, 15: 0.855, 16: 0.863
    },
    "5%": {
        10: 0.842, 11: 0.850, 12: 0.859, 13: 0.866, 
        14: 0.874, 15: 0.881, 16: 0.887
    }
}

# Критичні значення t-критерію Стьюдента для рівня значимості 0.05
t_critical_values_05 = {
    10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160,
    14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110,
    18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
    22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
    30: 2.042, 40: 2.021, 50: 2.009, 60: 2.000,
    70: 1.994, 80: 1.990, 90: 1.987, 100: 1.984,
    120: 1.980, 150: 1.976, 200: 1.972, 300: 1.968,
    500: 1.965, 1000: 1.962
}


def get_data(message="Введіть дані через пробіл: "):
    """
    Отримує дані від користувача з перевіркою на мінімальну кількість значень.
    
    Args:
        min_values (int): Мінімальна кількість значень для введення
        message (str): Повідомлення для введення даних
    
    Returns:
        tuple: (дані, кількість значень, сортований ряд)
    """
    while True:
        try:
            data = list(map(float, input(message).replace(",", ".").split()))
            n = len(data)
            
            if min_values > 0 and n < min_values:
                print(f"Для виконання тесту введіть {min_values} або більше значень!")
                continue
                
            # Сортований ряд даних
            sorted_data = sorted(data)
            
            return data, n, sorted_data
            
        except ValueError:
            print("Помилка! Введіть коректні числові дані.")

def choose_significance_level():
    """
    Запитує у користувача рівень значущості у відсотках.
    
    Returns:
        tuple: (значення рівня значущості, індекс для критичних значень, назва рівня)
    """
    available_levels = list(SIGNIFICANCE["p_values"].keys())
    available_values = [level.replace("%", "") for level in available_levels]
    
    print("\nДоступні рівні значущості:")
    for i, level in enumerate(available_levels):
        print(f"[{i+1}] {level}")
    
    while True:
        try:
            user_input = input("\nВведіть рівень значущості у відсотках (наприклад, 5): ")
            
            # Перевірка на порожнє введення - використовуємо значення за замовчуванням (5%)
            if not user_input.strip():
                selected_level = "5%"
                print(f"Обрано рівень значущості за замовчуванням: {selected_level}")
                break
                
            # Додаємо символ відсотка, якщо користувач його не ввів
            if "%" not in user_input:
                user_input = user_input.strip() + "%"
            
            # Перевіряємо, чи є такий рівень у словнику
            if user_input in available_levels:
                selected_level = user_input
                break
            else:
                print(f"Помилка! Доступні рівні значущості: {', '.join(available_levels)}")
        
        except ValueError:
            print("Помилка! Введіть коректне число.")
    
    # Отримуємо значення та індекс для обраного рівня
    p_value = SIGNIFICANCE["p_values"][selected_level]
    p_index = SIGNIFICANCE["indices"][selected_level]
    
    print(f"Обрано рівень значущості: {selected_level} (p = {p_value})")
    return p_value, p_index, selected_level

def continue_or_exit():
    ind_d = input("Чи потрібно виконувати наступні обчислення - так/ні: ")
    return ind_d == "так"