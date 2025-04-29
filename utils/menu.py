import os
import sys

os.system('color')

def normality_submenu():
    """Підменю вибору тестів на нормальність розподілу з ../tests/normality.py"""
    while True:
        print(
            f"\n\033[92mТЕСТИ НА НОРМАЛЬНІСТЬ РОЗПОДІЛУ\033[0m\n"
            f"\033[93m[1]\033[0m Тест Шапіро-Уілка\n"
            f"\033[93m[2]\033[0m Тест Андерсона-Дарлінга\n"
            f"\033[93m[3]\033[0m Обидва тести послідовно\n"
            f"\033[93m[0]\033[0m Повернутися до головного меню\n"
        )

        choice = input("\033[94mВиберіть тест (пусто - обидва тести):\033[0m ")
        
        # Імпортуємо тут для уникнення циклічних імпортів
        from tests.normality import shapiro_stat, anderson_stat
        
        if not choice or choice == "3":
            print("\nВиконання обох тестів на нормальність розподілу\n")
            print("\n--- Тест Шапіро-Уілка ---")
            data_result = shapiro_stat()
            if data_result:
                print("\n--- Тест Андерсона-Дарлінга ---")
                anderson_stat(data_result)
            return
            
        elif choice == "1":
            print("\n--- Тест Шапіро-Уілка ---")
            shapiro_stat()
            return
            
        elif choice == "2":
            print("\n--- Тест Андерсона-Дарлінга ---")
            anderson_stat()
            return
            
        elif choice == "0":
            return
            
        else:
            print("\033[91mНекоректний вибір!\033[0m")

def main_menu():
    while True:
        print(
            f"\n\033[92mГОЛОВНЕ МЕНЮ\033[0m\n"
            f"\033[93m[1]\033[0m Перевірка даних на ПРОМАХИ\n"
            f"\033[93m[2]\033[0m Описова статистика\n"
            f"\033[93m[3]\033[0m Перевірка даних на НОРМАЛЬНИЙ розподіл: тести: [Шапіро, Андерсона]\n"
            f"\033[93m[4]\033[0m Тест Стюдента для незалежних даних двох вибірок\n"
            f"\033[93m[5]\033[0m ПАРНИЙ тест Стюдента для залежних даних\n"
            f"\033[93m[6]\033[0m Тест Тюкі\n"
            f"\033[93m[7]\033[0m Тест Данна\n"
            f"\033[93m[8]\033[0m Кореляційний аналіз\n"
            f"\033[93m[9]\033[0m Регресійний аналіз\n"
            f"\033[93m[10]\033[0m \033[91mВихід\033[0m\n"
        )

        input_d = input("\033[94mВведіть номер тесту для його виконання:\033[0m ")
        
        # Імпортуємо тести тут, щоб уникнути циклічних імпортів
        if input_d == "1":
            from tests.outliers import outliers_stat
            outliers_stat()

        elif input_d == "2":
            from tests.descriptive import describe_stat
            describe_stat()

        elif input_d == "3":
            # Замінюємо прямий виклик на підменю вибору тесту
            normality_submenu()

        elif input_d == "4":
            from tests.student_welch_test import student_welch_test
            student_welch_test()
            
        elif input_d == "5":
            print("\nФункціональність у розробці\n")
            input("Натисніть Enter для продовження...")
            
        elif input_d == "6":
            print("\nФункціональність у розробці\n")
            input("Натисніть Enter для продовження...")
            
        elif input_d == "7":
            print("\nФункціональність у розробці\n")
            input("Натисніть Enter для продовження...")
            
        elif input_d == "8":
            print("\nФункціональність у розробці\n")
            input("Натисніть Enter для продовження...")
            
        elif input_d == "9":
            print("\nФункціональність у розробці\n")
            input("Натисніть Enter для продовження...")
            
        elif input_d == "10":
            print("\033[91mВихід з програми...\033[0m")
            sys.exit(0)
            
        else:
            print("\033[91mВведено некоректне значення!\033[0m")
            input("Натисніть Enter для продовження...")