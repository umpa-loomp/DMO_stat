import numpy as np
from scipy.stats import rankdata, kruskal
from scipy import stats
from scikit_posthocs import posthoc_dunn
import itertools
import pandas as pd
from utils.data_handler import get_data, continue_or_exit

def dunn_test():
    """
    Виконує тест Краскела-Волліса, а потім тест Данна для множинних попарних порівнянь між групами.
    
    Тест Данна - непараметричний метод для порівняння трьох і більше груп даних,
    який використовується після тесту Краскела-Волліса.
    """
    print("\n\033[92m--- ТЕСТ КРАСКЕЛА-ВОЛЛІСА І ДАННА ---\033[0m")
    print("Цей тест спочатку перевіряє наявність відмінностей між групами (Краскел-Волліс),")
    print("а потім виконує множинні попарні порівняння для визначення конкретних відмінностей (тест Данна).")
    
    # Запитуємо кількість груп
    while True:
        try:
            group_count = int(input("\n\033[93mВведіть кількість груп для порівняння (мінімум 3): \033[0m"))
            if group_count < 3:
                print("Для тестів Краскела-Волліса і Данна потрібно мінімум 3 групи!")
                continue
            break
        except ValueError:
            print("Будь ласка, введіть коректне число.")
    
    # Отримуємо дані для всіх груп
    groups = []
    group_names = []
    all_data = []
    
    for i in range(group_count):
        print(f"\n\033[93mГрупа {i+1}:\033[0m")
        group_name = input(f"Введіть назву для групи {i+1} (або залиште порожнім): ")
        if not group_name:
            group_name = f"Група {i+1}"
        group_names.append(group_name)
        
        data, n, _ = get_data(f"Введіть значення для групи {i+1} (через пробіл): ")
        groups.append(data)
        all_data.extend(data)
    
    # КРОК 1: Виконуємо тест Краскела-Волліса
    print("\n\033[93m--- Тест Краскела-Волліса ---\033[0m")
    
    try:
        # Виклик тесту Краскела-Волліса з усіма групами
        h_stat, p_value = kruskal(*groups)
        
        print(f"Статистика H: {h_stat:.4f}")
        print(f"p-значення: {p_value:.6f}")
        
        # Визначаємо результат тесту
        alpha = 0.05
        if p_value <= alpha:
            print(f"\033[92mВИСНОВОК: Існують статистично значущі відмінності між групами (p ≤ {alpha}).\033[0m")
            print("Проведемо тест Данна для визначення, які саме групи відрізняються...\n")
        else:
            print(f"\033[91mВИСНОВОК: Не виявлено статистично значущих відмінностей між групами (p > {alpha}).\033[0m")
            print("Тест Данна зазвичай не проводять, якщо тест Краскела-Волліса не показав значущих відмінностей.")
            
            # Запитуємо користувача, чи продовжувати тест Данна, незважаючи на результат тесту Краскела-Волліса
            continue_anyway = input("\nБажаєте все одно провести тест Данна? (так/ні): ").strip().lower() == "так"
            if not continue_anyway:
                return continue_or_exit()
    
    except Exception as e:
        print(f"\033[91mПомилка під час виконання тесту Краскела-Волліса: {str(e)}\033[0m")
        print("Продовжуємо з тестом Данна...")
    
    # КРОК 2: Виконуємо тест Данна
    print("\n\033[93m--- Тест Данна ---\033[0m")
    
    # Обчислюємо загальні ранги для всіх даних
    all_ranks = rankdata(all_data)
    
    # Розділяємо ранги по групах
    start_idx = 0
    group_ranks = []
    for group in groups:
        end_idx = start_idx + len(group)
        group_ranks.append(all_ranks[start_idx:end_idx])
        start_idx = end_idx
    
    # Обчислюємо середній ранг для кожної групи
    mean_ranks = [np.mean(ranks) for ranks in group_ranks]
    
    # Обчислюємо статистику Данна для кожної пари груп
    n_total = len(all_data)
    results = []
    
    for (i, j) in itertools.combinations(range(group_count), 2):
        ni, nj = len(groups[i]), len(groups[j])
        mean_diff = mean_ranks[i] - mean_ranks[j]
        std_err = np.sqrt((n_total * (n_total + 1) / 12) * (1/ni + 1/nj))
        z_value = mean_diff / std_err
        p_value = 2 * (1 - stats.norm.cdf(abs(z_value)))  # Двосторонній тест
        
        # Зберігаємо результат
        results.append({
            'group1': group_names[i],
            'group2': group_names[j],
            'mean_rank1': mean_ranks[i],
            'mean_rank2': mean_ranks[j],
            'mean_diff': mean_diff,
            'z_value': z_value,
            'p_value': p_value
        })    
    
    # Поправка Бонферроні 
    #     n_comparisons = len(results)
    #     significance_level = 0.05  
    #     adjusted_alpha = significance_level / n_comparisons
    
    # Застосовуємо поправку Холма через scikit-posthocs
    significance_level = 0.05
    result_matrix = posthoc_dunn([group for group in groups], p_adjust='holm')
    
    # Додаємо скориговані p-значення до результатів
    for result in results:
        i = group_names.index(result['group1'])
        j = group_names.index(result['group2'])
        # posthoc_dunn повертає матрицю з скоригованими p-значеннями
        result['adjusted_p_value'] = result_matrix.iloc[i, j]
        result['significant'] = result['adjusted_p_value'] < significance_level
    
    # Виводимо результати
    print("\n\033[93mРезультати тесту Данна:\033[0m")
    print(f"Кількість груп: {group_count}")
    print(f"Загальна кількість порівнянь: {len(results)}")
    print(f"Метод поправки на множинні порівняння: Холм")
    
    # Виводимо матрицю p-значень з поправкою Холма
    print("\n\033[93mМатриця p-значень (поправка Холма):\033[0m")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    print(result_matrix.round(5))
    
    # Таблиця середніх рангів
    print("\n\033[93mСередні ранги груп:\033[0m")
    for i, name in enumerate(group_names):
        print(f"{name}: {mean_ranks[i]:.2f}")
    
    # Таблиця попарних порівнянь
    print("\n\033[93mПопарні порівняння:\033[0m")
    print(f"{'Порівняння':<20} {'Різниця рангів':<15} {'Z-статистика':<15} {'p-значення':<15} {'Скориг. p-знач.':<15} {'Значущість':<10}")
    print("-" * 100)
    
    for result in results:
        significant = "Так" if result['significant'] else "Ні"
        significance_mark = "*" if result['significant'] else ""
        
        print(f"{result['group1']} vs {result['group2']:<15} {result['mean_diff']:12.2f} {result['z_value']:15.3f} {result['p_value']:15.5f} {result['adjusted_p_value']:15.5f} {significant + significance_mark:^10}")
    
    print("\n\033[93mВисновки:\033[0m")
    significant_pairs = [f"{r['group1']} і {r['group2']}" for r in results if r['significant']]
    
    if significant_pairs:
        print("Виявлено статистично значущі відмінності між такими групами:")
        for pair in significant_pairs:
            print(f"- {pair}")
    else:
        print("Не виявлено статистично значущих відмінностей між групами.")
    
    print("\nПримітка: Для інтерпретації врахована поправка Холма на множинні порівняння.")
    
    return continue_or_exit()