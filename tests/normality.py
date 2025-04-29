# ПЕРЕВІРКА НА НОРМАЛЬНИЙ РОЗПОДІЛ
import statistics as st
import numpy as np
from scipy.stats import shapiro, anderson
from utils.data_handler import get_data, SIGNIFICANCE, continue_or_exit, SHAPIRO_CRITICAL_VALUES

# ПЕРЕВІРКА НА НОРМАЛЬНИЙ РОЗПОДІЛ: Критерій Шапіро-Уілка  
def shapiro_stat():
    """
    Перевірка даних на нормальність розподілу за критерієм Шапіро-Уілка.
    
    Returns:
        tuple: (дані, кількість значень, сортований ряд) або None, якщо вихід
    """
    while True:
        try:
            # Отримуємо дані та перевіряємо їх кількість
            data, n_d, sort_d = get_data("Введіть дані через пробіл: ")
            
            if n_d < 10 or n_d > 16:
                print("Введіть від 10 до 16 значень для тесту Шапіро-Уілка")
                continue
                
            # Вибір рівня значущості
            print("\nДоступні рівні значущості для тесту Шапіро-Уілка:")
            for i, level in enumerate(["1%", "2%", "5%"]):
                print(f"[{i+1}] {level} (p = {SIGNIFICANCE['p_values'][level]})")
            
            choice = input("\nВиберіть рівень значущості (1-3) [3 за замовчуванням]: ").strip()
            if not choice:
                sig_level = "5%"  # За замовчуванням
            else:
                try:
                    idx = int(choice) - 1
                    sig_level = ["1%", "2%", "5%"][idx]
                except (ValueError, IndexError):
                    print("Некоректний вибір, використовується значення за замовчуванням (5%)")
                    sig_level = "5%"
            
            p_value = SIGNIFICANCE["p_values"][sig_level]
            
            # Критерій Шапіро-Уілка            
            stat, p = shapiro(data)  # Значення Шапіро
            
            # Отримуємо критичне значення для вибраного рівня значущості
            shap_crit = SHAPIRO_CRITICAL_VALUES[sig_level][n_d]

            print(
                f"Кількість даних: {n_d}\n"
                f"Сортований ряд даних: {sort_d}\n"
                f"Рівень значущості: {sig_level} (p = {p_value})\n"
                f"Критичне значення Шапіро: {shap_crit}\n"
                f"Отримане значення Шапіро: {round(stat, 3)}\n"
                f"p-value: {round(p, 5)}\n"
            )
            
            if stat > shap_crit:
                print(f"Тест Шапіро-Уілка: отримані нами дані\n"
                      f"підпорядковуються нормальному розподілу,\n"
                      f"оскільки значення Шапіро {round(stat, 3)} є більшим\n"
                      f"за критичне значення {shap_crit},\n"
                      f"а також значення статистичної значущості {round(p, 5)}\n"
                      f"є більшим за р {p_value}\n")
            else:
                print(f"Тест Шапіро-Уілка: отримані нами дані\n"
                      f"НЕ підпорядковуються нормальному розподілу,\n"
                      f"оскільки значення Шапіро {round(stat, 3)} є меншим\n"
                      f"за критичне значення {shap_crit},\n"
                      f"а також значення статистичної значущості {round(p, 5)}\n"
                      f"є меншим за р {p_value}\n")    
                        

            return data, n_d, sort_d
                
        except Exception as e:
            print(f"Помилка: {str(e)}")
            if not continue_or_exit():
                return None

# ПЕРЕВІРКА НА НОРМАЛЬНИЙ РОЗПОДІЛ: Критерій Андерсона-Дарлінга
def anderson_stat(input_data=None):
    """
    Перевірка даних на нормальність розподілу за критерієм Андерсона-Дарлінга.
    
    Args:
        input_data: (tuple) дані з попереднього тесту або None
    """
    while True:
        try:
            # Перевіряємо, чи є вхідні дані
            if input_data is None:
                data, n_d, sort_d = get_data("Введіть дані через пробіл: ")
            else:
                print("\nВикористання даних з попереднього тесту\n")
                data, n_d, sort_d = input_data
                input_data = None  # Скидаємо для наступної ітерації

            # Тест Андерсона-Дарлінга
            result = anderson(data)
            stat = result.statistic
            crit_values = result.critical_values  # [15%, 10%, 5%, 2.5%, 1%]
            sign_levels = result.significance_level
            
            # Індекс для рівня значущості 5% у масиві критичних значень
            # Для anderson() із scipy.stats, це третій елемент (індекс 2)
            anderson_p05_idx = 2  # Відповідає 5% рівню значущості
            
            print(
                f"Кількість даних: {n_d}\n"
                f"Сортований ряд даних: {sort_d}\n"
                f"Статистика Андерсона-Дарлінга: {round(stat, 3)}\n"
            )
            
            print("Критичні значення при різних рівнях значущості:")
            for i, (cv, sl) in enumerate(zip(crit_values, sign_levels)):
                print(f"- {sl}%: {round(cv, 3)}")
            
            # Перевірка на нормальність (при рівні значущості 5%)
            if stat < crit_values[anderson_p05_idx]:
                print(f"\nТест Андерсона-Дарлінга: отримані нами дані\n"
                      f"підпорядковуються нормальному розподілу,\n"
                      f"оскільки статистика тесту {round(stat, 3)} є меншою\n"
                      f"за критичне значення {round(crit_values[anderson_p05_idx], 3)}\n"
                      f"при рівні значущості 5%.\n")
            else:
                print(f"\nТест Андерсона-Дарлінга: отримані нами дані\n"
                      f"НЕ підпорядковуються нормальному розподілу,\n"
                      f"оскільки статистика тесту {round(stat, 3)} є більшою\n"
                      f"за критичне значення {round(crit_values[anderson_p05_idx], 3)}\n"
                      f"при рівні значущості 5%.\n")

            if not continue_or_exit():
                return
            
        except Exception as e:
            print(f"Помилка: {str(e)}")
            if not continue_or_exit():
                return