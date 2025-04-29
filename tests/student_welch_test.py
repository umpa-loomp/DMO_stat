import statistics as st
import numpy as np
from scipy import stats as sts
from scipy.stats import f, t

from utils.data_handler import get_data, continue_or_exit, SIGNIFICANCE

# TODO: refactor the project to use imported functions in the s_w_t function instead of defining them here (search for "TO DO!")

def student_welch_test():
    """
    Виконує порівняння двох незалежних вибірок за методикою Фішера-Стьюдента:
    1. Перевіряє нормальність кожної вибірки
    2. Шукає та обробляє промахи
    3. Проводить F-тест на однорідність дисперсій
    4. Залежно від результатів F-тесту вибирає:
       - класичний t-тест Стьюдента (при однорідності дисперсій)
       - або t-тест Уелша (при неоднорідності)
    5. Повертає p-значення, довірчий інтервал і рекомендацію
    """
    while True:
        try:
            # Отримуємо дані для обох груп
            print("\n\033[93mВведення даних для першої групи:\033[0m")
            data1, n_d1, sort_d1 = get_data("Група 1 (введіть дані через пробіл): ")
            
            print("\n\033[93mВведення даних для другої групи:\033[0m")
            data2, n_d2, sort_d2 = get_data("Група 2 (введіть дані через пробіл): ")
            
            # Перевіряємо мінімальну кількість даних для статистичного аналізу
            if n_d1 < 4 or n_d2 < 4:
                print("Для виконання тесту введіть більш ніж 3 значення в кожній групі!")
                if not continue_or_exit():
                    return
                continue
            
            print("\n\033[93m1. Перевірка на нормальність розподілу\033[0m")
            
            # Імпортуємо тут для уникнення циклічних імпортів
            from tests.normality import shapiro_stat, anderson_stat # TO DO!
            
            # Перевірка нормальності даних
            print("\nПеревірка нормальності для Групи 1:")
            shapiro_results1 = check_normality(data1, "Група 1")
            
            print("\nПеревірка нормальності для Групи 2:")
            shapiro_results2 = check_normality(data2, "Група 2")
            
            print("\n\033[93m2. Перевірка на викиди (промахи)\033[0m")
            
            # Імпортуємо тут для уникнення циклічних імпортів
            from tests.outliers import outliers_stat # TO DO!
            
            # Перевірка на промахи
            print("\nПеревірка на промахи для Групи 1:")
            outliers1 = check_outliers(data1, "Група 1")
            
            print("\nПеревірка на промахи для Групи 2:")
            outliers2 = check_outliers(data2, "Група 2")
            
            print("\n\033[93m3. F-тест на однорідність дисперсій\033[0m")
            
            # Розрахунок дисперсій
            var_d1 = st.variance(data1)
            var_d2 = st.variance(data2)
            
            # F-статистика
            f_value = var_d1 / var_d2 if var_d1 > var_d2 else var_d2 / var_d1
            
            # Ступені свободи
            df1 = n_d1 - 1
            df2 = n_d2 - 1
            
            if var_d1 < var_d2:
                df1, df2 = df2, df1
                
            # p-значення для F-тесту
            p_value_f = 2 * min(f.sf(f_value, df1, df2), f.cdf(f_value, df1, df2))
            
            # Критичне значення F
            p_05 = SIGNIFICANCE["p_values"]["5%"]
            f_crit = f.ppf(1 - p_05, df1, df2)
            
            # Результат F-тесту
            equal_variances = p_value_f > p_05
            
            print(f"Дисперсія Групи 1: {round(var_d1, 3)}")
            print(f"Дисперсія Групи 2: {round(var_d2, 3)}")
            print(f"F-статистика: {round(f_value, 3)}")
            print(f"Ступені свободи: ({df1}, {df2})")
            print(f"p-значення: {round(p_value_f, 5)}")
            print(f"Критичне значення F (α = 0.05): {round(f_crit, 3)}")
            
            if equal_variances:
                print("\nF-тест: дисперсії вибірок статистично не відрізняються.")
                print("Буде застосовано класичний t-тест Стьюдента для незалежних вибірок.")
            else:
                print("\nF-тест: дисперсії вибірок статистично відрізняються.")
                print("Буде застосовано t-тест Уелша для незалежних вибірок з нерівними дисперсіями.")
            
            print("\n\033[93m4. Тест Стьюдента / Уелша\033[0m")
            
            # Розрахунок середніх значень
            mean_d1 = sum(data1) / n_d1
            mean_d2 = sum(data2) / n_d2
            
            if equal_variances:
                # Класичний тест Стьюдента для рівних дисперсій
                
                # Об'єднана дисперсія
                sp2 = ((n_d1 - 1) * var_d1 + (n_d2 - 1) * var_d2) / (n_d1 + n_d2 - 2)
                
                # t-статистика
                t_stat = (mean_d1 - mean_d2) / (np.sqrt(sp2) * np.sqrt(1/n_d1 + 1/n_d2))
                
                # Ступені свободи
                df = n_d1 + n_d2 - 2
                
                # p-значення
                p_value_t = 2 * t.sf(abs(t_stat), df)
                
                # Критичне значення t
                t_crit = t.ppf(1 - p_05/2, df)
                
                # 95% довірчий інтервал
                se = np.sqrt(sp2 * (1/n_d1 + 1/n_d2))
                ci_lower = (mean_d1 - mean_d2) - t_crit * se
                ci_upper = (mean_d1 - mean_d2) + t_crit * se
                
                # Виведення результатів
                print("Проведення класичного t-тесту Стьюдента (рівні дисперсії):")
                print(f"Середнє Групи 1: {round(mean_d1, 3)}")
                print(f"Середнє Групи 2: {round(mean_d2, 3)}")
                print(f"Різниця середніх: {round(mean_d1 - mean_d2, 3)}")
                print(f"Об'єднана дисперсія: {round(sp2, 3)}")
                print(f"t-статистика: {round(t_stat, 3)}")
                print(f"Ступені свободи: {df}")
                print(f"p-значення: {round(p_value_t, 5)}")
                print(f"Критичне значення t (α = 0.05): {round(t_crit, 3)}")
                print(f"95% довірчий інтервал для різниці середніх: [{round(ci_lower, 3)}, {round(ci_upper, 3)}]")
            
            else:
                # Тест Уелша для нерівних дисперсій
                
                # t-статистика
                t_stat = (mean_d1 - mean_d2) / np.sqrt(var_d1/n_d1 + var_d2/n_d2)
                
                # Ступені свободи за Уелшем-Саттертвайтом
                df = ((var_d1/n_d1 + var_d2/n_d2)**2) / ((var_d1/n_d1)**2/(n_d1-1) + (var_d2/n_d2)**2/(n_d2-1))
                
                # p-значення
                p_value_t = 2 * t.sf(abs(t_stat), df)
                
                # Критичне значення t
                t_crit = t.ppf(1 - p_05/2, df) # двостороннє критичне значення
                t_crit_one_directional = t.ppf(1 - p_05, df) # одностороннє критичне значення
                
                # 95% довірчий інтервал
                se = np.sqrt(var_d1/n_d1 + var_d2/n_d2)
                ci_lower = (mean_d1 - mean_d2) - t_crit * se
                ci_upper = (mean_d1 - mean_d2) + t_crit * se
                
                # Виведення результатів
                print("Проведення t-тесту Уелша (нерівні дисперсії):")
                print(f"Середнє Групи 1: {round(mean_d1, 3)}")
                print(f"Середнє Групи 2: {round(mean_d2, 3)}")
                print(f"Різниця середніх: {round(mean_d1 - mean_d2, 3)}")
                print(f"t-статистика: {round(t_stat, 3)}")
                print(f"Ступені свободи (Уелш-Саттертвайт): {round(df, 3)}")
                print(f"p-значення: {round(p_value_t, 5)}")
                print(f"Критичне значення t (α = 0.05): {round(t_crit, 3)}")
                print(f"95% довірчий інтервал для різниці середніх: [{round(ci_lower, 3)}, {round(ci_upper, 3)}]")
            
            # Висновок
            print("\n\033[93m5. Висновок\033[0m")
            if p_value_t < p_05:
                print(f"Групи статистично значимо відрізняються (p = {round(p_value_t, 5)}),")
                if mean_d1 > mean_d2:
                    print(f"При цьому середнє значення Групи 1 ({round(mean_d1, 3)}) є більшим за середнє Групи 2 ({round(mean_d2, 3)}).")
                else:
                    print(f"При цьому середнє значення Групи 2 ({round(mean_d2, 3)}) є більшим за середнє Групи 1 ({round(mean_d1, 3)}).")
                print(f"Оскільки значення статистики {round(abs(t_stat), 3)} є більшим за критичне значення {round(t_crit, 3)}.")
            else:
                print(f"Групи статистично значимо НЕ відрізняються (p = {round(p_value_t, 5)}),")
                print(f"Оскільки значення статистики {round(abs(t_stat), 3)} є меншим за критичне значення {round(t_crit, 3)}.")
            
            print(f"\nВикористаний метод: {'Класичний t-тест Стьюдента' if equal_variances else 't-тест Уелша'}")
            print(f"95% довірчий інтервал для різниці середніх: [{round(ci_lower, 3)}, {round(ci_upper, 3)}]")
            
            # Рекомендації
            print("\n\033[93mРекомендації:\033[0m")
            if not (shapiro_results1 and shapiro_results2):
                print("- Зважайте на відхилення від нормального розподілу. Можливе застосування непараметричних тестів. Тести Mann-Whitney (незалежний) або Wilcoxon (парний) можуть бути альтернативою.")
                
            if outliers1 or outliers2:
                print("- У даних виявлено можливі промахи. Рекомендується їхня обробка перед остаточним аналізом.")
            
            if not continue_or_exit():
                return
        
        except Exception as e:
            print(f"Помилка: {str(e)}")
            if not continue_or_exit():
                return

def check_normality(data, group_name):
    """
    Перевіряє нормальність розподілу використовуючи тест Шапіро-Уілка
    
    Args:
        data: дані для перевірки
        group_name: назва групи для виведення
    
    Returns:
        bool: True, якщо дані мають нормальний розподіл
    """
    try:
        stat, p = sts.shapiro(data)
        p_05 = SIGNIFICANCE["p_values"]["5%"]
        
        n_d = len(data)
        if n_d >= 10 and n_d <= 16:
            # Використовуємо табличні критичні значення для n від 10 до 16
            from utils.data_handler import SHAPIRO_CRITICAL_VALUES
            shap_crit = SHAPIRO_CRITICAL_VALUES["5%"][n_d]
            
            is_normal = stat > shap_crit
            
            print(f"{group_name}:")
            print(f"Статистика Шапіро: {round(stat, 3)}")
            print(f"Критичне значення (α = 0.05): {shap_crit}")
            print(f"p-значення: {round(p, 5)}")
            print(f"Дані {'підпорядковуються' if is_normal else 'НЕ підпорядковуються'} нормальному розподілу.")
            
            return is_normal
        else:
            # Для n < 10 або n > 16 використовуємо лише p-value TODO: додати ще значення у SHAPIRO_CRITICAL_VALUES!
            is_normal = p > p_05
            
            print(f"{group_name}:")
            print(f"Статистика Шапіро: {round(stat, 3)}")
            print(f"p-значення: {round(p, 5)}")
            print(f"Дані {'підпорядковуються' if is_normal else 'НЕ підпорядковуються'} нормальному розподілу.")
            
            return is_normal
        
    except Exception as e:
        print(f"Помилка при перевірці нормальності для {group_name}: {str(e)}")
        return False

def check_outliers(data, group_name):
    """
    Перевіряє наявність промахів (викидів) у даних
    
    Args:
        data: дані для перевірки
        group_name: назва групи для виведення
    
    Returns:
        bool: True, якщо знайдено промахи
    """
    try:
        n_d = len(data)
        sort_d = sorted(data)
        min_d = min(data)
        max_d = max(data)
        mean_d = sum(data) / n_d
        st_d = (sum((i - mean_d)**2 for i in data) / (n_d - 1))**0.5
        
        has_outliers = False
        
        # Критерій Шовене
        if 4 <= n_d <= 10:
            sh_crits = {
                4: 1.64, 5: 1.68, 6: 1.73, 7: 1.79, 
                8: 1.86, 9: 1.92, 10: 1.96
            }
            sh_crit = sh_crits[n_d]
            
            # Перевірка мін та макс значень
            sh_min = (mean_d - min_d) / st_d
            if sh_min > sh_crit:
                print(f"Тест Шовене: мінімальне значення {min_d} є промахом (знач.: {round(sh_min, 2)} > {sh_crit})")
                has_outliers = True
                
            sh_max = (max_d - mean_d) / st_d
            if sh_max > sh_crit:
                print(f"Тест Шовене: максимальне значення {max_d} є промахом (знач.: {round(sh_max, 2)} > {sh_crit})")
                has_outliers = True              

        
        if not has_outliers:
            print("Промахів не виявлено.")
            
        return has_outliers
        
    except Exception as e:
        print(f"Помилка при перевірці промахів для {group_name}: {str(e)}")
        return False