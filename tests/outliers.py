# ПРОМАХИ
from utils.data_handler import get_data, SIGNIFICANCE, continue_or_exit

def outliers_stat():
    while True:
        # Отримуємо дані та перевіряємо їх кількість
        try:
            data, n_d, sort_d = get_data("Введіть дані через пробіл: ")
            
            if n_d < 4 or n_d > 10:
                print("Введіть більше ніж три та менш ніж десять значень!")
                continue
             
            min_d = min(data)
            max_d = max(data)
            mean_d3 = sum(data) / n_d

            st_d4 = (sum((i - mean_d3)**2 for i in data) / (n_d - 1))**0.5 # Стандартне відхилення

            p_05 = SIGNIFICANCE["p_values"]["5%"]
            p_01 = SIGNIFICANCE["p_values"]["1%"]
            
            # Шовене
            sh_min = (mean_d3 - min_d) / st_d4
            sh_max = (max_d - mean_d3) / st_d4

            # Критичні значення Шовене
            sh_crits = {
                4: 1.64,
                5: 1.68,
                6: 1.73,
                7: 1.79,
                8: 1.86,
                9: 1.92,
                10: 1.96
            }

            sh_crit = sh_crits[n_d]

            # Діксон
            d_min = (sort_d[1] - min_d) / (max_d - min_d)
            # Діксон
            d_max = (max_d - sort_d[-2]) / (max_d - min_d)

            # Критичні значення Діксона
            d_crits = {
                4: [0.926, 0.829],
                5: [0.821, 0.710],
                6: [0.740, 0.625],
                7: [0.680, 0.568],
                8: [0.634, 0.526],
                9: [0.598, 0.493],
                10: [0.568, 0.466]
            }

            d_crit = d_crits[n_d][1]
            
            # Романовський
            rom_min = abs(min_d - mean_d3) / st_d4            
            # Романовський
            rom_max = abs(max_d - mean_d3) / st_d4
            
            # Критичні значення Романовського при α = 0.05
            rom_crits = {
                4: 1.71, 
                5: 2.10,              
                6: 2.10,
                7: 2.27,
                8: 2.27,
                9: 2.41,
                10: 2.41
            }
            
            rom_crit = rom_crits[n_d]
            
            # Ірвін для всіх значень
            irwin_values = []
            for i in range(1, n_d):
                irwin_values.append((sort_d[i] - sort_d[i-1]) / st_d4)
            
            # Знаходження максимального значення Ірвіна
            irwin_max = max(irwin_values)
            irwin_max_idx = irwin_values.index(irwin_max)
            
            # Критичні значення Ірвіна при α = 0.05
            irwin_crits = {
                3: 2.19,
                4: 2,
                5: 1.87,
                6: 1.77,
                7: 1.69,
                8: 1.63,
                9: 1.58,
                10: 1.54
            }
            
            irwin_crit = irwin_crits[n_d]

            print(
                f"Кількість даних: {n_d}\n"
                f"Сортований ряд даних: {sort_d}\n"
                f"Критичне значення Шовене: {sh_crit}\n"
                f"Критичне значення Діксона: {d_crit}\n"
                f"Критичне значення Романовського: {rom_crit}\n"
                f"Критичне значення Ірвіна: {irwin_crit}"
            )
            if sh_min > sh_crit:
                print(f"Тест Шовене: мінімальне значення: {min_d} є промахом,"
                      f"оскільки обчислене значення Шовене {round(sh_min, 2)}"
                      f"є більшим за його критичне значення {sh_crit}")
            else:
                print(f"Тест Шовене: мінімальне значення: {min_d} НЕ є промахом")
            if d_min > d_crit:
                print(f"Тест Діксона: мінімальне значення: {min_d} є промахом з р < {p_05}")
            else:
                print(f"Тест Діксона: мінімальне значення: {min_d} НЕ є промахом з р < {p_05}")
            if sh_max > sh_crit:
                print(f"Тест Шовене: максимальне значення: {max_d} є промахом")
            else:
                print(f"Тест Шовене: максимальне значення: {max_d} НЕ є промахом")
            if d_max > d_crit:
                print(f"Тест Діксона: максимальне значення: {max_d} є промахом з р < {p_05}")
            else:
                print(f"Тест Діксона: максимальне значення: {max_d} НЕ є промахом з р < {p_05}")
                
            # Результати тесту Романовського
            if rom_min > rom_crit:
                print(f"Тест Романовського: мінімальне значення: {min_d} є промахом,"
                      f"оскільки обчислене значення Романовського {round(rom_min, 2)}"
                      f"є більшим за його критичне значення {rom_crit}")
            else:
                print(f"Тест Романовського: мінімальне значення: {min_d} НЕ є промахом")
                
            if rom_max > rom_crit:
                print(f"Тест Романовського: максимальне значення: {max_d} є промахом,"
                      f"оскільки обчислене значення Романовського {round(rom_max, 2)}"
                      f"є більшим за його критичне значення {rom_crit}")
            else:
                print(f"Тест Романовського: максимальне значення: {max_d} НЕ є промахом")
                
            # Результати тесту Ірвіна
            if irwin_max > irwin_crit:
                suspicious_value = sort_d[irwin_max_idx + 1]
                print(f"Тест Ірвіна: значення: {suspicious_value} є промахом,"
                      f"оскільки обчислене значення Ірвіна {round(irwin_max, 2)}"
                      f"є більшим за його критичне значення {irwin_crit}")
            else:
                print(f"Тест Ірвіна: жодне значення НЕ є промахом")


            if not continue_or_exit():
                return
        
        except Exception as e:
            print(f"Помилка: {str(e)}")
