# !!! дебаг поки що з поправкою Бонферроні, а не Холма !!! 
import os
import sys

# TO RUN alternative from root dir: python -m tests.dunn_test_debug
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import numpy as np
from scipy.stats import rankdata, kruskal
from scipy import stats
import itertools
from utils.data_handler import get_data, continue_or_exit

def dunn_test_debug():
    """
    Виконує тест Краскела-Волліса, а потім тест Данна для множинних попарних порівнянь між групами.
    Включає детальний режим відстеження значень змінних на кожному етапі.
    """
    print("\n\033[92m--- ТЕСТ КРАСКЕЛА-ВОЛЛІСА І ДАННА (РЕЖИМ ВІДЛАГОДЖЕННЯ) ---\033[0m")
    print("Цей тест спочатку перевіряє наявність відмінностей між групами (Краскел-Волліс),")
    print("а потім виконує множинні попарні порівняння для визначення конкретних відмінностей (тест Данна).")
    print("\n\033[93mУВАГА: Увімкнено режим відлагодження. Всі проміжні значення будуть виведені.\033[0m")
    
    # Запитуємо кількість груп
    while True:
        try:
            group_count = int(input("\n\033[93mВведіть кількість груп для порівняння (мінімум 3): \033[0m"))
            print(f"\n\033[96mDEBUG: Кількість груп = {group_count}\033[0m")
            
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
        
        print(f"\033[96mDEBUG: Група {i+1} '{group_name}' має {n} значень: {data}\033[0m")
    
    print(f"\n\033[96mDEBUG: Всі групи: {groups}\033[0m")
    print(f"\033[96mDEBUG: Назви груп: {group_names}\033[0m")
    print(f"\033[96mDEBUG: Всі дані об'єднані: {all_data}\033[0m")
    
    # КРОК 1: Виконуємо тест Краскела-Волліса
    print("\n\033[93m--- Тест Краскела-Волліса ---\033[0m")
    
    try:
        # Виклик тесту Краскела-Волліса з усіма групами
        h_stat, p_value = kruskal(*groups)
        
        print(f"\033[96mDEBUG: Аргументи для kruskal(): {[g[:5] + ['...'] if len(g) > 5 else g for g in groups]}\033[0m")
        print(f"\033[96mDEBUG: Статистика H = {h_stat}, p-значення = {p_value}\033[0m")
        
        print(f"Статистика H: {h_stat:.4f}")
        print(f"p-значення: {p_value:.6f}")
        
        # Визначаємо результат тесту
        alpha = 0.05
        print(f"\033[96mDEBUG: Рівень значущості alpha = {alpha}\033[0m")
        
        if p_value <= alpha:
            print(f"\033[92mВИСНОВОК: Існують статистично значущі відмінності між групами (p ≤ {alpha}).\033[0m")
            print("Проведемо тест Данна для визначення, які саме групи відрізняються...\n")
        else:
            print(f"\033[91mВИСНОВОК: Не виявлено статистично значущих відмінностей між групами (p > {alpha}).\033[0m")
            print("Тест Данна зазвичай не проводять, якщо тест Краскела-Волліса не показав значущих відмінностей.")
            
            # Запитуємо користувача, чи продовжувати тест Данна, незважаючи на результат
            continue_anyway = input("\nБажаєте все одно провести тест Данна? (так/ні): ").strip().lower() == "так"
            print(f"\033[96mDEBUG: Продовжувати тест Данна = {continue_anyway}\033[0m")
            
            if not continue_anyway:
                return continue_or_exit()
    
    except Exception as e:
        print(f"\033[91mПомилка під час виконання тесту Краскела-Волліса: {str(e)}\033[0m")
        print(f"\033[96mDEBUG: Помилка: {e}\033[0m")
        print("Продовжуємо з тестом Данна...")
    
    # КРОК 2: Виконуємо тест Данна
    print("\n\033[93m--- Тест Данна ---\033[0m")
    
    # Обчислюємо загальні ранги для всіх даних
    all_ranks = rankdata(all_data)
    print(f"\033[96mDEBUG: Всі ранги: {all_ranks}\033[0m")
    print(f"\033[96mDEBUG: Перевірка: кількість рангів = {len(all_ranks)}, кількість даних = {len(all_data)}\033[0m")
    
    # Розділяємо ранги по групах
    start_idx = 0
    group_ranks = []
    for idx, group in enumerate(groups):
        end_idx = start_idx + len(group)
        group_rank = all_ranks[start_idx:end_idx]
        group_ranks.append(group_rank)
        
        print(f"\033[96mDEBUG: Ранги для групи {group_names[idx]}: {group_rank}\033[0m")
        print(f"\033[96mDEBUG: Індекси: від {start_idx} до {end_idx-1}\033[0m")
        
        start_idx = end_idx
    
    # Обчислюємо середній ранг для кожної групи
    mean_ranks = [np.mean(ranks) for ranks in group_ranks]
    for idx, mean_rank in enumerate(mean_ranks):
        print(f"\033[96mDEBUG: Середній ранг для групи {group_names[idx]}: {mean_rank:.4f}\033[0m")
    
    # Обчислюємо статистику Данна для кожної пари груп
    n_total = len(all_data)
    print(f"\033[96mDEBUG: Загальна кількість спостережень n_total = {n_total}\033[0m")
    
    results = []
    
    print("\n\033[96mDEBUG: Обчислення статистики Данна для кожної пари груп:\033[0m")
    for (i, j) in itertools.combinations(range(group_count), 2):
        ni, nj = len(groups[i]), len(groups[j])
        mean_diff = mean_ranks[i] - mean_ranks[j]
        std_err = np.sqrt((n_total * (n_total + 1) / 12) * (1/ni + 1/nj))
        z_value = mean_diff / std_err
        p_value = 2 * (1 - stats.norm.cdf(abs(z_value)))  # Двосторонній тест
        
        print(f"\033[96mDEBUG: Порівняння {group_names[i]} vs {group_names[j]}:\033[0m")
        print(f"\033[96m  - Розміри груп: ni = {ni}, nj = {nj}\033[0m")
        print(f"\033[96m  - Середні ранги: {mean_ranks[i]:.4f} vs {mean_ranks[j]:.4f}\033[0m")
        print(f"\033[96m  - Різниця середніх рангів: {mean_diff:.4f}\033[0m")
        print(f"\033[96m  - Стандартна помилка: {std_err:.4f}\033[0m")
        print(f"\033[96m  - Z-значення: {z_value:.4f}\033[0m")
        print(f"\033[96m  - p-значення: {p_value:.6f}\033[0m")
        
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
    
    # Застосовуємо поправку Бонферроні для множинних порівнянь
    n_comparisons = len(results)
    significance_level = 0.05  # Стандартний рівень значущості
    adjusted_alpha = significance_level / n_comparisons
    
    print(f"\n\033[96mDEBUG: Загальна кількість порівнянь: {n_comparisons}\033[0m")
    print(f"\033[96mDEBUG: Стандартний рівень значущості: {significance_level}\033[0m")
    print(f"\033[96mDEBUG: Скоригований рівень значущості (поправка Бонферроні): {adjusted_alpha:.6f}\033[0m")
    
    # Виводимо результати
    print("\n\033[93mРезультати тесту Данна:\033[0m")
    print(f"Кількість груп: {group_count}")
    print(f"Загальна кількість порівнянь: {n_comparisons}")
    print(f"Скоригований рівень значущості (поправка Бонферроні): {adjusted_alpha:.5f}")
    
    # Таблиця середніх рангів
    print("\n\033[93mСередні ранги груп:\033[0m")
    for i, name in enumerate(group_names):
        print(f"{name}: {mean_ranks[i]:.2f}")
    
    # Таблиця попарних порівнянь
    print("\n\033[93mПопарні порівняння:\033[0m")
    print(f"{'Порівняння':<30} {'Різниця рангів':<15} {'Z-статистика':<15} {'p-значення':<15} {'Значущість':<10}")
    print("-" * 85)
    
    print(f"\033[96mDEBUG: Таблиця попарних порівнянь з висновками:\033[0m")
    
    significant_count = 0
    for result in results:
        significant = "Так" if result['p_value'] < adjusted_alpha else "Ні"
        if result['p_value'] < adjusted_alpha:
            significant_count += 1
            
        significance_mark = "*" if significant == "Так" else ""
        
        print(f"{result['group1']} vs {result['group2']:<15} {result['mean_diff']:12.2f} {result['z_value']:15.3f} {result['p_value']:15.5f} {significant + significance_mark:^10}")
        
        print(f"\033[96mDEBUG: {result['group1']} vs {result['group2']} - p={result['p_value']:.6f} < {adjusted_alpha:.6f}? {significant}\033[0m")
    
    print(f"\033[96mDEBUG: Кількість статистично значущих порівнянь: {significant_count} з {n_comparisons}\033[0m")
    
    print("\n\033[93mВисновки:\033[0m")
    significant_pairs = [f"{r['group1']} і {r['group2']}" for r in results if r['p_value'] < adjusted_alpha]
    
    print(f"\033[96mDEBUG: Список пар із значущими відмінностями: {significant_pairs}\033[0m")
    
    if significant_pairs:
        print("Виявлено статистично значущі відмінності між такими групами:")
        for pair in significant_pairs:
            print(f"- {pair}")
    else:
        print("Не виявлено статистично значущих відмінностей між групами.")
    
    print("\nПримітка: Для інтерпретації врахована поправка Бонферроні на множинні порівняння.")
    
    return continue_or_exit()

# Виклик функції, якщо скрипт запущено безпосередньо
if __name__ == "__main__":
    dunn_test_debug()