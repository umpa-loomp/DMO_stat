# ОПИСОВА СТАТИСТИКА
from utils.data_handler import get_data, SIGNIFICANCE, continue_or_exit

import statistics as st
import numpy as np
from scipy import stats as sts

def describe_stat():
    while True:
        # Отримуємо дані та перевіряємо їх кількість
        try:
            data, n_d, sort_d = get_data("Введіть дані через пробіл: ")
            
            if n_d < 4 or n_d > 10:
                print("Введіть більше ніж три та менш ніж десять значень!")
                continue


            # Мінімальне значення
            min_d = min(data)

            # Максимальне значення
            max_d = max(data)

            # Середнє арифметичне значення
            mean_d1 = st.mean(data)
            mean_d2 = np.mean(data)
            mean_d3 = sum(data) / n_d

            # Медіана
            median_d1 = st.median(data)
            median_d2 = np.median(data)

            # Мода
            mode_d = st.multimode(data)
            # if len(mode_d) == n_d:
            #     print("Ряд даних не містить МОДИ!!!")
            # else:
            #     print(f"Мода: {mode_d}\n")

            # Стандартне відхилення Statistics
            st_d1 = st.stdev(data)

            # Стандартне відхилення NumPy
            st_d2 = np.std(data, ddof=1) # 1 - для вибірки, 0 - для генеральної сукупності

            # Стандартне відхилення SciPy
            st_d3 = sts.tstd(data, ddof=1)

            # Стандартне відхилення - ФОРМУЛА
            st_d4 = (sum((i - mean_d3)**2 for i in data) / (n_d - 1))**0.5

            # Дисперсія
            var_d = st.variance(data)

            # Похибка середнього арифметичного значення
            sem_d = st_d4 / n_d**0.5

            # Квартиль 25, 50, 75
            q_d = st.quantiles(data)

            print(
                f"Кількість даних: {n_d}\n"
                f"Сортований ряд даних: {sort_d}\n"
                f"Мінімальне значення: {min_d}\n"
                f"Максимальне значення: {max_d}\n"
                # f"Середнє арифметичне значення: {mean_d1}\n"
                # f"Середнє арифметичне значення: {mean_d2}\n"
                f"Середнє арифметичне значення: {round(mean_d3, 2)}\n"
                f"Медіана: {median_d1}\n"
                # f"Медіана: {median_d2}\n"
                f"{"Ряд даних не містить МОДИ!!!" if len(mode_d) == n_d else f"Мода: {mode_d}"}\n"
                # f"Стандартне відхилення Statistic: {st_d1}\n"
                # f"Стандартне відхилення NumPy: {st_d2}\n"
                # f"Стандартне відхилення SciPy: {st_d3}\n"
                f"Стандартне відхилення Формула: {round(st_d4, 2)}\n"
                f"Дисперсія: {round(var_d, 2)}\n"
                f"Похибка середнього арифметичного: {round(sem_d, 2)}\n"
                f"Квартиль 25, 50, 75: {q_d}"
            )

            if not continue_or_exit():
                break
        
        except Exception as e:
            print(f"Помилка: {str(e)}")   
            
        if not continue_or_exit():
            return
