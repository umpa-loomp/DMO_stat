import numpy as np
from scipy.stats import pearsonr, t
import matplotlib.pyplot as plt
from utils.data_handler import t_critical_values_05, get_data, continue_or_exit

# alternatibe to manual entered df table
# def get_t_critical(df, alpha=0.05):
#    return t.ppf(1 - alpha/2, df) 

def get_t_critical(df):
    """
    Отримати критичне значення t-критерію для заданих ступенів свободи
    
    Args:
        df (int): Ступені свободи
        
    Returns:
        float: Критичне значення t-критерію
    """
    # Шукаємо найближче значення в словнику
    keys = list(t_critical_values_05.keys())
    if df <= min(keys):
        return t_critical_values_05[min(keys)]
    elif df >= max(keys):
        return t_critical_values_05[max(keys)]
    else:
        # Знаходимо найближчі значення
        lower_key = max([k for k in keys if k <= df])
        upper_key = min([k for k in keys if k >= df])
        
        # Якщо є точне значення
        if lower_key == df:
            return t_critical_values_05[lower_key]
        elif upper_key == df:
            return t_critical_values_05[upper_key]
        
        # Лінійна інтерполяція (if df is not in table) (temporary)
        lower_t = t_critical_values_05[lower_key]
        upper_t = t_critical_values_05[upper_key]
        return lower_t + (upper_t - lower_t) * (df - lower_key) / (upper_key - lower_key)

def pearson_correlation():
    """
    Виконує кореляційний аналіз за методом Пірсона, перевіряє значущість коефіцієнта
    кореляції і будує кореляційне поле.
    
    Обмеження: розмір вибірки має бути > 9.
    """
    print("\n\033[92m--- КОРЕЛЯЦІЙНИЙ АНАЛІЗ ЗА ПІРСОНОМ ---\033[0m")
    print("Цей аналіз дозволяє визначити силу і напрямок лінійного зв'язку між двома змінними.")
    print("Для достовірного результату розмір вибірки має бути більше 9 елементів.")
    
    # Отримуємо дані для першої змінної
    print("\n\033[93mВведіть дані для першої змінної (X):\033[0m")
    data1, n1, _ = get_data("Введіть значення через пробіл: ")
    
    # Перевіряємо розмір вибірки
    if n1 <= 9:
        print("\033[91mРозмір вибірки має бути більше 9 елементів для достовірного результату!\033[0m")
        return continue_or_exit()
    
    # Отримуємо дані для другої змінної
    print("\n\033[93mВведіть дані для другої змінної (Y):\033[0m")
    data2, n2, _ = get_data("Введіть значення через пробіл: ")
    
    # Перевіряємо чи розміри вибірок однакові
    if n1 != n2:
        print("\033[91mРозміри вибірок мають бути однаковими!\033[0m")
        return continue_or_exit()
    
    # Перевіряємо розмір другої вибірки
    if n2 <= 9:
        print("\033[91mРозмір вибірки має бути більше 9 елементів для достовірного результату!\033[0m")
        return continue_or_exit()
    
    # Обчислюємо коефіцієнт кореляції Пірсона
    try:
        corr, p_value = pearsonr(data1, data2)
        
        # Обчислюємо t-статистику
        df = n1 - 2  # Ступені свободи
        t_stat = corr * np.sqrt(df) / np.sqrt(1 - corr**2)
        
        # Отримуємо критичне значення
        t_crit = get_t_critical(df)
        
        # Визначаємо значущість кореляції (по модулю!!!)
        is_significant = abs(t_stat) > t_crit
        
        # Виводимо результати
        print("\n\033[93m--- Результати кореляційного аналізу ---\033[0m")
        print(f"Кількість пар даних: {n1}")
        print(f"Коефіцієнт кореляції Пірсона (r): {corr:.4f}")
        
        # Інтерпретація коефіцієнта кореляції
        if abs(corr) < 0.3:
            strength = "слабка"
        elif abs(corr) < 0.7:
            strength = "помірна"        
        elif abs(corr) < 0.9:
            strength = "сильна"        
        elif abs(corr) < 0.999:
            strength = "дуже сильна"
        else:
            strength = "функціональна"
            
        if corr > 0:
            direction = "позитивна"
        else:
            direction = "негативна"
            
        if abs(corr) < 0.1:
            print(f"Інтерпретація: відсутність лінійного зв'язку")
        else:
            print(f"Інтерпретація: {strength} {direction} кореляція")
        
        # Перевірка значущості
        print("\n\033[93m--- Перевірка значущості (H₀: r = 0) ---\033[0m")
        print(f"Ступені свободи (df): {df}")
        print(f"t-статистика: {t_stat:.4f}")
        print(f"Критичне значення t (α = 0.05): {t_crit:.4f}")
        print(f"p-значення: {p_value:.6f}")
        
        if is_significant:
            print(f"\033[92mВисновок: Кореляція є статистично значущою (|t| > t_crit, p < 0.05).\033[0m")
            print("Ми відхиляємо нульову гіпотезу про відсутність кореляції.")
        else:
            print(f"\033[91mВисновок: Кореляція не є статистично значущою (|t| ≤ t_crit, p ≥ 0.05).\033[0m")
            print("Ми не можемо відхилити нульову гіпотезу про відсутність кореляції.")
        
        # Будуємо кореляційне поле
        plt.figure(figsize=(10, 6))
        plt.scatter(data1, data2, alpha=0.7, s=50)
        
        # Додаємо лінію регресії
        m, b = np.polyfit(data1, data2, 1)
        plt.plot(data1, [m*x + b for x in data1], color='red', linestyle='--')
        
        # Додаємо назви осей та заголовок
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title(f'Кореляційне поле (r = {corr:.4f})')
        
        # Додаємо текст з рівнянням лінії регресії
        equation = f'y = {m:.4f}x + {b:.4f}'
        plt.text(0.05, 0.95, equation, transform=plt.gca().transAxes, 
                 fontsize=16, verticalalignment='top')
        
        # Додаємо текст з коефіцієнтом кореляції та значущістю
        sig_text = "значуща" if is_significant else "не значуща"
        corr_text = f'r = {corr:.4f} ({sig_text})'
        plt.text(0.05, 0.90, corr_text, transform=plt.gca().transAxes, 
                 fontsize=16, verticalalignment='top')
        
        # Додаємо сітку
        plt.grid(True, alpha=0.3)
        
        # Відображаємо графік
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"\033[91mПомилка при обчисленні кореляції: {str(e)}\033[0m")
    
    return continue_or_exit()