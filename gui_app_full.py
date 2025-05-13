import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
import os
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, t
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Додаємо кореневу директорію проекту до шляху імпорту
sys.path.append('.')

# Імпортуємо функції з нашого проекту
try:
    from tests.dunn_test import dunn_test
    from tests.wilcoxon_mann_whitney import wilcoxon_mann_whitney_test
    from tests.normality import shapiro_stat, anderson_stat
    from tests.correlation import pearson_correlation
    from utils.data_handler import t_critical_values_05, get_data, continue_or_exit
except ImportError as e:
    print(f"Помилка імпорту: {e}")

class StatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StatMDO - Статистичний аналіз")
        self.geometry("900x650")
        self.configure(bg="#f5f5f5")
        
        # Створюємо вкладки
        style = ttk.Style()
        style.configure("TNotebook", background="#f5f5f5")
        style.configure("TFrame", background="#f5f5f5")
        
        self.tab_control = ttk.Notebook(self)
        
        # Вкладка для вибору тесту
        self.tab_main = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_main, text="Вибір тесту")
        
        # Вкладка для введення даних
        self.tab_data = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_data, text="Введення даних")
        
        # Вкладка для результатів
        self.tab_results = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_results, text="Результати")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Ініціалізуємо інтерфейс
        self._create_main_tab()
        self._create_data_tab()
        self._create_results_tab()
        
        # Стан програми
        self.current_test = None
        self.group_data = []
        self.group_names = []

    def _create_main_tab(self):
        """Створюємо вкладку з вибором тестів"""
        frame = ttk.LabelFrame(self.tab_main, text="Доступні тести")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        ttk.Label(
            frame, 
            text="Оберіть статистичний тест", 
            font=("Helvetica", 16)
        ).pack(pady=10)
        
        # Групові тести
        group_frame = ttk.LabelFrame(frame, text="Порівняння груп")
        group_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(
            group_frame, 
            text="Тест Данна",
            command=lambda: self.select_test("dunn")
        ).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(
            group_frame, 
            text="Вілкоксона-Манна-Уітні",
            command=lambda: self.select_test("wilcoxon")
        ).pack(fill="x", padx=5, pady=2)
        
        # Тести нормальності
        norm_frame = ttk.LabelFrame(frame, text="Тести на нормальність")
        norm_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(
            norm_frame, 
            text="Шапіро-Вілк",
            command=lambda: self.select_test("shapiro")
        ).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(
            norm_frame, 
            text="Андерсона-Дарлінга",
            command=lambda: self.select_test("anderson")
        ).pack(fill="x", padx=5, pady=2)       

        corr_frame = ttk.LabelFrame(frame, text="Аналіз зв'язку")
        corr_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            corr_frame, 
            text="Кореляційний аналіз",
            command=lambda: self.select_test("correlation")
        ).pack(fill="x", padx=5, pady=2)            
        
        
        # Інформація про програму
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Label(
            info_frame, 
            text="StatMDO - програма для статистичного аналізу даних",
            font=("Helvetica", 12)
        ).pack(pady=2)
        
        ttk.Label(
            info_frame, 
            text="© 2025 Dima Marchenko",
            font=("Helvetica", 10)
        ).pack(pady=1)

    def _create_data_tab(self):
        """Створюємо вкладку для введення даних"""
        self.data_frame = ttk.Frame(self.tab_data)
        self.data_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вміст буде створюватись динамічно при виборі тесту

    def _create_results_tab(self):
        """Створюємо вкладку для відображення результатів"""
        frame = ttk.Frame(self.tab_results)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Текстове поле для виведення результатів
        self.result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 14))
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Кнопки для керування результатами
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            btn_frame, 
            text="Зберегти результати", 
            command=self.save_results
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Очистити", 
            command=lambda: self.result_text.delete(1.0, tk.END)
        ).pack(side="left", padx=5)
        
        # Фрейм для графіків (створюватиметься динамічно)
        self.plot_frame = ttk.Frame(frame)
        self.plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def select_test(self, test_name):
        """Обробник вибору тесту"""
        self.current_test = test_name
        
        # Очищуємо попередні дані
        self.group_data = []
        self.group_names = []
        
        # Переходимо на вкладку введення даних
        self.tab_control.select(self.tab_data)
        
        # Очищуємо фрейм введення даних
        for widget in self.data_frame.winfo_children():
            widget.destroy()
        
        if test_name == "dunn":
            self._setup_dunn_test_input()
        elif test_name == "wilcoxon":
            self._setup_wilcoxon_test_input()
        elif test_name == "shapiro":
            self._setup_normality_test_input("shapiro")
        elif test_name == "anderson":
            self._setup_normality_test_input("anderson")
        elif test_name == "correlation":
            self._setup_correlation_input()            

    def _setup_dunn_test_input(self):
        """Налаштування введення даних для тесту Данна"""
        ttk.Label(
            self.data_frame, 
            text="Тест Данна - порівняння трьох і більше груп",
            font=("Helvetica", 14)
        ).pack(pady=5)
        
        # Фрейм для вибору кількості груп
        group_count_frame = ttk.Frame(self.data_frame)
        group_count_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            group_count_frame, 
            text="Кількість груп:"
        ).pack(side="left", padx=5)
        
        group_count_var = tk.StringVar()
        group_count_spinbox = ttk.Spinbox(
            group_count_frame, 
            from_=3, 
            to=10, 
            textvariable=group_count_var,
            width=5
        )
        group_count_spinbox.pack(side="left", padx=5)
        group_count_var.set("3")  # Значення за замовчуванням
        
        ttk.Button(
            group_count_frame, 
            text="Продовжити",
            command=lambda: self._create_group_inputs(int(group_count_var.get()))
        ).pack(side="left", padx=10)
        
        # Додатковий опис тесту
        ttk.Label(
            self.data_frame,
            text="Тест Данна виконує множинні попарні порівняння між групами\nі застосовує корекцію Холма для контролю помилок першого роду.",
            justify="left"
        ).pack(pady=10, anchor="w")

    def _setup_wilcoxon_test_input(self):
        """Налаштування введення даних для тесту Вілкоксона-Манна-Уітні"""
        ttk.Label(
            self.data_frame, 
            text="Тест Вілкоксона-Манна-Уітні - порівняння двох незалежних вибірок",
            font=("Helvetica", 14)
        ).pack(pady=5)
        
        # Опис тесту
        ttk.Label(
            self.data_frame,
            text="Цей тест є непараметричним аналогом t-тесту для незалежних вибірок\nі не потребує припущення про нормальність розподілу даних.",
            justify="left"
        ).pack(pady=10, anchor="w")
        
        # Створюємо два поля для вибірок
        for i in range(2):
            group_frame = ttk.LabelFrame(self.data_frame, text=f"Група {i+1}")
            group_frame.pack(fill="x", padx=10, pady=5)
            
            # Поле для імені групи
            name_frame = ttk.Frame(group_frame)
            name_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(
                name_frame, 
                text="Назва групи:"
            ).pack(side="left", padx=5)
            
            name_entry = ttk.Entry(name_frame)
            name_entry.pack(side="left", fill="x", expand=True, padx=5)
            name_entry.insert(0, f"Група {i+1}")  # Значення за замовчуванням
            
            # Поле для даних групи
            data_frame = ttk.Frame(group_frame)
            data_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(
                data_frame, 
                text="Дані (через пробіл):"
            ).pack(side="left", padx=5)
            
            data_entry = ttk.Entry(data_frame)
            data_entry.pack(side="left", fill="x", expand=True, padx=5)
            
            # Зберігаємо посилання на поля
            if i == 0:
                self.group1_name_entry = name_entry
                self.group1_data_entry = data_entry
            else:
                self.group2_name_entry = name_entry
                self.group2_data_entry = data_entry
        
        # Демо-дані
        self.group1_data_entry.insert(0, "12.1 11.2 13.4 12.6 13.0 12.3 11.8")
        self.group2_data_entry.insert(0, "14.2 13.1 14.5 15.2 14.8 13.9 15.0")
        
        # Кнопка для запуску аналізу
        ttk.Button(
            self.data_frame, 
            text="Виконати аналіз",
            command=self._run_wilcoxon_analysis
        ).pack(pady=10)

    def _setup_normality_test_input(self, test_type):
        """Налаштування введення даних для тестів на нормальність"""
        test_names = {
            "shapiro": "Шапіро-Вілка",
            "anderson": "Андерсона-Дарлінга"
        }
        
        ttk.Label(
            self.data_frame, 
            text=f"Тест {test_names[test_type]} - перевірка на нормальність розподілу",
            font=("Helvetica", 14)
        ).pack(pady=5)
        
        # Опис тесту
        descriptions = {
            "shapiro": "Перевіряє нульову гіпотезу про те, що дані отримані з нормально розподіленої генеральної сукупності.\nРекомендується для малих вибірок (n < 50).",
            "anderson": "Перевіряє, чи належать дані до заданого розподілу (за замовчуванням - нормального).\nПрацює краще для великих вибірок, ніж тест Шапіро-Вілка."
        }
        
        ttk.Label(
            self.data_frame,
            text=descriptions[test_type],
            justify="left"
        ).pack(pady=10, anchor="w")
        
        # Фрейм для введення даних
        data_frame = ttk.LabelFrame(self.data_frame, text="Вхідні дані")
        data_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле для імені вибірки
        name_frame = ttk.Frame(data_frame)
        name_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(
            name_frame, 
            text="Назва вибірки:"
        ).pack(side="left", padx=5)
        
        self.sample_name_entry = ttk.Entry(name_frame)
        self.sample_name_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.sample_name_entry.insert(0, "Вибірка") 
        
        # Поле для даних
        input_frame = ttk.Frame(data_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(
            input_frame, 
            text="Дані (через пробіл):"
        ).pack(side="left", padx=5)
        
        self.sample_data_entry = ttk.Entry(input_frame)
        self.sample_data_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Демо-дані
        if test_type == "shapiro":
            self.sample_data_entry.insert(0, "12.1 11.2 13.4 12.6 13.0 12.3 11.8 12.9 13.2 12.5")
        else:
            self.sample_data_entry.insert(0, "14.2 13.1 14.5 15.2 14.8 13.9 15.0 14.1 13.8 15.5 14.7 13.5")
        
        # Рівень значущості
        alpha_frame = ttk.Frame(data_frame)
        alpha_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(
            alpha_frame, 
            text="Рівень значущості α:"
        ).pack(side="left", padx=5)
        
        self.alpha_var = tk.StringVar(value="0.05")
        alpha_combo = ttk.Combobox(
            alpha_frame,
            textvariable=self.alpha_var,
            values=["0.01", "0.05", "0.1"],
            width=5,
            state="readonly"
        )
        alpha_combo.pack(side="left", padx=5)
        
        # Кнопка для запуску аналізу
        ttk.Button(
            self.data_frame, 
            text="Виконати аналіз",
            command=lambda: self._run_normality_analysis(test_type)
        ).pack(pady=10)

    def _create_group_inputs(self, group_count):
        """Створення полів введення для груп"""
        # Очищуємо все, крім вибору кількості груп
        for widget in list(self.data_frame.winfo_children())[2:]:
            widget.destroy()
        
        # Створюємо фрейм з прокруткою для введення груп
        canvas = tk.Canvas(self.data_frame)
        scrollbar = ttk.Scrollbar(self.data_frame, orient="vertical", command=canvas.yview)
        groups_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Створюємо вікно для фрейма груп всередині канвасу
        canvas.create_window((0, 0), window=groups_frame, anchor="nw")
        groups_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Поля введення для кожної групи
        self.group_entries = []
        self.group_name_entries = []
        
        for i in range(group_count):
            group_frame = ttk.LabelFrame(groups_frame, text=f"Група {i+1}")
            group_frame.pack(fill="x", padx=10, pady=5)
            
            # Поле для імені групи
            name_frame = ttk.Frame(group_frame)
            name_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(
                name_frame, 
                text="Назва групи:"
            ).pack(side="left", padx=5)
            
            name_entry = ttk.Entry(name_frame)
            name_entry.pack(side="left", fill="x", expand=True, padx=5)
            name_entry.insert(0, f"Група {i+1}")  # Значення за замовчуванням
            self.group_name_entries.append(name_entry)
            
            # Поле для даних групи
            data_frame = ttk.Frame(group_frame)
            data_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(
                data_frame, 
                text="Дані (через пробіл):"
            ).pack(side="left", padx=5)
            
            data_entry = ttk.Entry(data_frame)
            data_entry.pack(side="left", fill="x", expand=True, padx=5)
            self.group_entries.append(data_entry)
        
        # Демо-дані для стандартних груп
        demo_data = [
            "12.1 11.2 13.4 12.6 13.0",
            "14.2 13.1 14.5 15.2 14.8",
            "10.5 9.8 11.2 10.3 11.0"
        ]
        
        # Заповнюємо поля демо-даними якщо груп ≤ 3
        if group_count <= 3:
            for i in range(min(group_count, len(demo_data))):
                self.group_entries[i].insert(0, demo_data[i])
        
        # Кнопка для запуску аналізу
        ttk.Button(
            groups_frame, 
            text="Виконати аналіз",
            command=self._run_dunn_analysis
        ).pack(pady=10)

    def _run_dunn_analysis(self):
        """Запуск тесту Данна"""
        try:
            # Збираємо дані з полів введення
            self.group_data = []
            self.group_names = []
            
            for i, entry in enumerate(self.group_entries):
                text = entry.get().strip()
                if not text:
                    messagebox.showerror("Помилка", f"Група {i+1}: дані відсутні")
                    return
                
                try:
                    # Перетворюємо рядок з числами в список чисел
                    data = [float(x) for x in text.split()]
                    if len(data) < 3:
                        messagebox.showwarning("Попередження", f"Група {i+1}: менше 3 значень")
                    self.group_data.append(data)
                except ValueError:
                    messagebox.showerror("Помилка", f"Група {i+1}: некоректні числові значення")
                    return
            
            # Збираємо імена груп
            for i, entry in enumerate(self.group_name_entries):
                name = entry.get().strip()
                self.group_names.append(name if name else f"Група {i+1}")
            
            # Запускаємо аналіз
            self._run_analysis_and_display("dunn")
                
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка під час аналізу: {str(e)}")

    def _run_wilcoxon_analysis(self):
        """Запуск тесту Вілкоксона-Манна-Уітні"""
        try:
            # Збираємо дані з полів введення
            group1_text = self.group1_data_entry.get().strip()
            group2_text = self.group2_data_entry.get().strip()
            
            if not group1_text or not group2_text:
                messagebox.showerror("Помилка", "Дані відсутні для однієї або обох груп")
                return
            
            try:
                # Перетворюємо рядки з числами в списки чисел
                group1_data = [float(x) for x in group1_text.split()]
                group2_data = [float(x) for x in group2_text.split()]
                
                if len(group1_data) < 3 or len(group2_data) < 3:
                    messagebox.showwarning("Попередження", "Рекомендується мати хоча б 3 значення в кожній групі")
                
                self.group_data = [group1_data, group2_data]
                self.group_names = [
                    self.group1_name_entry.get().strip() or "Група 1",
                    self.group2_name_entry.get().strip() or "Група 2"
                ]
                
                # Запускаємо аналіз
                self._run_analysis_and_display("wilcoxon")
                
            except ValueError:
                messagebox.showerror("Помилка", "Некоректні числові значення")
                return
                
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка під час аналізу: {str(e)}")

    def _run_normality_analysis(self, test_type):
        """Запуск тесту на нормальність"""
        try:
            # Збираємо дані з поля введення
            data_text = self.sample_data_entry.get().strip()
            
            if not data_text:
                messagebox.showerror("Помилка", "Дані відсутні")
                return
            
            try:
                # Перетворюємо рядок з числами в список чисел
                data = [float(x) for x in data_text.split()]
                
                if len(data) < 3:
                    messagebox.showwarning("Попередження", "Рекомендується мати хоча б 3 значення для тестування")
                
                self.group_data = [data]
                self.group_names = [self.sample_name_entry.get().strip() or "Вибірка"]
                self.alpha = float(self.alpha_var.get())
                
                # Запускаємо аналіз
                self._run_analysis_and_display(test_type)
                
            except ValueError:
                messagebox.showerror("Помилка", "Некоректні числові значення")
                return
                
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка під час аналізу: {str(e)}")

    def _run_analysis_and_display(self, test_type):
        """Запускає аналіз і відображає результати"""
        # Очищаємо поле результатів
        self.result_text.delete(1.0, tk.END)
        
        # Викликаємо відповідний метод аналізу
        if test_type == "dunn":
            self._perform_dunn_analysis()
        elif test_type == "wilcoxon":
            self._perform_wilcoxon_analysis()
        elif test_type == "shapiro":
            self._perform_shapiro_analysis()
        elif test_type == "anderson":
            self._perform_anderson_analysis()
        elif test_type == "correlation":
            self._perform_correlation_analysis()
        
        # Переключаємося на вкладку результатів
        self.tab_control.select(self.tab_results)

    def _perform_dunn_analysis(self):
        """Виконує тест Данна і виводить результати"""
        try:
            from scipy.stats import rankdata, kruskal
            from scipy import stats
            from scikit_posthocs import posthoc_dunn
            import itertools
            
            # Виводимо заголовок
            self.print_result("--- ТЕСТ КРАСКЕЛА-ВОЛЛІСА І ДАННА ---\n", "heading")
            
            # Виконуємо тест Краскела-Волліса
            self.print_result("\n--- Тест Краскела-Волліса ---\n", "subheading")
            
            # Обчислюємо статистику і p-значення
            h_stat, p_value = kruskal(*self.group_data)
            
            self.print_result(f"Статистика H: {h_stat:.4f}\n")
            self.print_result(f"p-значення: {p_value:.6f}\n")
            
            # Визначаємо результат тесту
            alpha = 0.05
            if p_value <= alpha:
                self.print_result(f"ВИСНОВОК: Існують статистично значущі відмінності між групами (p ≤ {alpha}).\n", "success")
                self.print_result("Проведемо тест Данна для визначення, які саме групи відрізняються...\n")
            else:
                self.print_result(f"ВИСНОВОК: Не виявлено статистично значущих відмінностей між групами (p > {alpha}).\n", "warning")
                self.print_result("Тест Данна зазвичай не проводять, якщо тест Краскела-Волліса не показав значущих відмінностей.\n")
            
            # Виконуємо тест Данна
            self.print_result("\n--- Тест Данна ---\n", "subheading")
            
            # Алгоритм тесту Данна
            all_data = [item for sublist in self.group_data for item in sublist]
            all_ranks = rankdata(all_data)
            
            # Розділяємо ранги по групах
            start_idx = 0
            group_ranks = []
            for group in self.group_data:
                end_idx = start_idx + len(group)
                group_ranks.append(all_ranks[start_idx:end_idx])
                start_idx = end_idx
            
            # Обчислюємо середній ранг для кожної групи
            mean_ranks = [np.mean(ranks) for ranks in group_ranks]
            
            # Обчислюємо статистику Данна для кожної пари груп
            n_total = len(all_data)
            results = []
            
            for (i, j) in itertools.combinations(range(len(self.group_data)), 2):
                ni, nj = len(self.group_data[i]), len(self.group_data[j])
                mean_diff = mean_ranks[i] - mean_ranks[j]
                std_err = np.sqrt((n_total * (n_total + 1) / 12) * (1/ni + 1/nj))
                z_value = mean_diff / std_err
                p_value = 2 * (1 - stats.norm.cdf(abs(z_value)))  # Двосторонній тест
                
                results.append({
                    'group1': self.group_names[i],
                    'group2': self.group_names[j],
                    'mean_rank1': mean_ranks[i],
                    'mean_rank2': mean_ranks[j],
                    'mean_diff': mean_diff,
                    'z_value': z_value,
                    'p_value': p_value
                })
            
            # Застосовуємо поправку Холма
            significance_level = 0.05
            result_matrix = posthoc_dunn(self.group_data, p_adjust='holm')
            
            # Додаємо скориговані p-значення до результатів
            for result in results:
                i = self.group_names.index(result['group1'])
                j = self.group_names.index(result['group2'])
                result['adjusted_p_value'] = result_matrix.iloc[i, j]
                result['significant'] = result['adjusted_p_value'] < significance_level
            
            # Виводимо результати
            self.print_result("\nРезультати тесту Данна:\n", "subheading")
            self.print_result(f"Кількість груп: {len(self.group_data)}\n")
            self.print_result(f"Загальна кількість порівнянь: {len(results)}\n")
            self.print_result(f"Метод поправки на множинні порівняння: Холм\n")
            
            # Виводимо таблицю середніх рангів
            self.print_result("\nСередні ранги груп:\n", "subheading")
            for i, name in enumerate(self.group_names):
                self.print_result(f"{name}: {mean_ranks[i]:.2f}\n")
            
            # Виводимо таблицю попарних порівнянь
            self.print_result("\nПопарні порівняння:\n", "subheading")
            headers = ["Порівняння", "Різниця рангів", "Z-статистика", "p-значення", "Скориг. p-знач.", "Значущість"]
            
            # Додаємо роздільну лінію
            self.print_result("-" * 100 + "\n")
            
            for result in results:
                significant = "Так*" if result['significant'] else "Ні"
                line = f"{result['group1']} vs {result['group2']}".ljust(25)
                line += f"{result['mean_diff']:12.2f}"
                line += f"{result['z_value']:15.3f}"
                line += f"{result['p_value']:15.5f}"
                line += f"{result['adjusted_p_value']:15.5f}"
                line += f"{significant:^10}"
                self.print_result(line + "\n")
            
            # Виводимо висновки
            self.print_result("\nВисновки:\n", "subheading")
            significant_pairs = [f"{r['group1']} і {r['group2']}" for r in results if r['significant']]
            
            if significant_pairs:
                self.print_result("Виявлено статистично значущі відмінності між такими групами:\n")
                for pair in significant_pairs:
                    self.print_result(f"- {pair}\n")
            else:
                self.print_result("Не виявлено статистично значущих відмінностей між групами.\n")
            
            self.print_result("\nПримітка: Для інтерпретації врахована поправка Холма на множинні порівняння.\n")
            
            # Створюємо графік
            self._create_boxplot(self.group_data, self.group_names, "Порівняння розподілів груп")
            
        except Exception as e:
            self.print_result(f"Помилка під час аналізу: {str(e)}\n", "error")
            import traceback
            traceback.print_exc()

    def _perform_wilcoxon_analysis(self):
        """Виконує тест Вілкоксона-Манна-Уітні і виводить результати"""
        try:
            from scipy.stats import mannwhitneyu, ranksums
            
            # Виводимо заголовок
            self.print_result("--- ТЕСТ ВІЛКОКСОНА-МАННА-УІТНІ ---\n", "heading")
            self.print_result("Цей тест порівнює дві незалежні вибірки без припущення про нормальність розподілу.\n")
            
            # Базова статистика груп
            self.print_result("\nОписова статистика груп:\n", "subheading")
            
            for i, (name, data) in enumerate(zip(self.group_names, self.group_data)):
                n = len(data)
                mean = np.mean(data)
                median = np.median(data)
                std_dev = np.std(data, ddof=1)
                min_val = np.min(data)
                max_val = np.max(data)
                
                self.print_result(f"{name}:\n")
                self.print_result(f"  Кількість значень: {n}\n")
                self.print_result(f"  Середнє: {mean:.4f}\n")
                self.print_result(f"  Медіана: {median:.4f}\n")
                self.print_result(f"  Стандартне відхилення: {std_dev:.4f}\n")
                self.print_result(f"  Мінімум: {min_val:.4f}\n")
                self.print_result(f"  Максимум: {max_val:.4f}\n\n")
            
            # Виконуємо тест Манна-Уітні
            u_stat, p_value = mannwhitneyu(self.group_data[0], self.group_data[1], alternative='two-sided')
            
            # Додатково обчислюємо Z-статистику за допомогою ranksums
            z_stat, _ = ranksums(self.group_data[0], self.group_data[1])
            
            # Виводимо результати
            self.print_result("\nРезультати тесту:\n", "subheading")
            self.print_result(f"U-статистика: {u_stat:.4f}\n")
            self.print_result(f"Z-статистика: {z_stat:.4f}\n")
            self.print_result(f"p-значення: {p_value:.6f}\n")
            
            # Інтерпретація результатів
            alpha = 0.05
            if p_value <= alpha:
                self.print_result(f"\nВИСНОВОК: Існує статистично значуща різниця між групами (p ≤ {alpha}).\n", "success")
            else:
                self.print_result(f"\nВИСНОВОК: Не виявлено статистично значущої різниці між групами (p > {alpha}).\n", "warning")
            
            # Створюємо графік
            self._create_boxplot(self.group_data, self.group_names, "Порівняння двох груп")
            
        except Exception as e:
            self.print_result(f"Помилка під час аналізу: {str(e)}\n", "error")
            import traceback
            traceback.print_exc()

    def _perform_shapiro_analysis(self):
        """Виконує тест Шапіро-Вілка і виводить результати"""
        try:
            from scipy.stats import shapiro, normaltest
            import matplotlib.pyplot as plt
            
            # Виводимо заголовок
            self.print_result("--- ТЕСТ ШАПІРО-ВІЛКА ---\n", "heading")
            self.print_result("Перевірка вибірки на нормальність розподілу.\n")
            
            # Дані вибірки
            data = self.group_data[0]
            name = self.group_names[0]
            alpha = self.alpha
            
            # Базова статистика
            self.print_result(f"\nОписова статистика для {name}:\n", "subheading")
            n = len(data)
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data, ddof=1)
            min_val = np.min(data)
            max_val = np.max(data)
            
            self.print_result(f"Кількість значень: {n}\n")
            self.print_result(f"Середнє: {mean:.4f}\n")
            self.print_result(f"Медіана: {median:.4f}\n")
            self.print_result(f"Стандартне відхилення: {std_dev:.4f}\n")
            self.print_result(f"Мінімум: {min_val:.4f}\n")
            self.print_result(f"Максимум: {max_val:.4f}\n")
            
            # Виконуємо тест Шапіро-Вілка
            stat, p_value = shapiro(data)
            
            # Виводимо результати
            self.print_result("\nРезультати тесту Шапіро-Вілка:\n", "subheading")
            self.print_result(f"W-статистика: {stat:.4f}\n")
            self.print_result(f"p-значення: {p_value:.6f}\n")
            self.print_result(f"Рівень значущості α: {alpha}\n")
            
            # Інтерпретація результатів
            if p_value <= alpha:
                self.print_result(f"\nВИСНОВОК: Дані НЕ відповідають нормальному розподілу (p ≤ {alpha}).\n", "warning")
                self.print_result("Рекомендується використовувати непараметричні методи для аналізу цих даних.\n")
            else:
                self.print_result(f"\nВИСНОВОК: Дані відповідають нормальному розподілу (p > {alpha}).\n", "success")
                self.print_result("Можна використовувати параметричні методи для аналізу цих даних.\n")
            
            # Створюємо графіки
            self._create_normality_plots(data, name)
            
        except Exception as e:
            self.print_result(f"Помилка під час аналізу: {str(e)}\n", "error")
            import traceback
            traceback.print_exc()

    def _perform_anderson_analysis(self):
        """Виконує тест Андерсона-Дарлінга і виводить результати"""
        try:
            from scipy.stats import anderson
            
            # Виводимо заголовок
            self.print_result("--- ТЕСТ АНДЕРСОНА-ДАРЛІНГА ---\n", "heading")
            self.print_result("Перевірка вибірки на нормальність розподілу.\n")
            
            # Дані вибірки
            data = self.group_data[0]
            name = self.group_names[0]
            alpha = self.alpha
            
            # Базова статистика
            self.print_result(f"\nОписова статистика для {name}:\n", "subheading")
            n = len(data)
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data, ddof=1)
            min_val = np.min(data)
            max_val = np.max(data)
            
            self.print_result(f"Кількість значень: {n}\n")
            self.print_result(f"Середнє: {mean:.4f}\n")
            self.print_result(f"Медіана: {median:.4f}\n")
            self.print_result(f"Стандартне відхилення: {std_dev:.4f}\n")
            self.print_result(f"Мінімум: {min_val:.4f}\n")
            self.print_result(f"Максимум: {max_val:.4f}\n")
            
            # Виконуємо тест Андерсона-Дарлінга
            result = anderson(data)
            
            # Виводимо результати
            self.print_result("\nРезультати тесту Андерсона-Дарлінга:\n", "subheading")
            self.print_result(f"A²-статистика: {result.statistic:.4f}\n")
            
            # Порівнюємо з критичними значеннями
            self.print_result("\nКритичні значення:\n")
            
            significance_found = False
            for i, size in enumerate(result.critical_values):
                sl = result.significance_level[i]
                if sl/100 >= alpha and not significance_found:
                    self.print_result(f"  {sl}%: {size:.4f}", "warning")
                    if result.statistic < size:
                        self.print_result(" - пройдено\n", "success")
                    else:
                        self.print_result(" - не пройдено\n", "error")
                    significance_found = True
                else:
                    self.print_result(f"  {sl}%: {size:.4f}")
                    if result.statistic < size:
                        self.print_result(" - пройдено\n")
                    else:
                        self.print_result(" - не пройдено\n")
            
            # Інтерпретація результатів
            critical_value = None
            for i, sl in enumerate(result.significance_level):
                if sl/100 >= alpha:
                    critical_value = result.critical_values[i]
                    break
                    
            if critical_value is None:
                self.print_result("\nНе знайдено відповідного критичного значення для заданого рівня значущості.\n", "warning")
            elif result.statistic > critical_value:
                self.print_result(f"\nВИСНОВОК: Дані НЕ відповідають нормальному розподілу (рівень значущості {alpha}).\n", "warning")
                self.print_result("Рекомендується використовувати непараметричні методи для аналізу цих даних.\n")
            else:
                self.print_result(f"\nВИСНОВОК: Дані відповідають нормальному розподілу (рівень значущості {alpha}).\n", "success")
                self.print_result("Можна використовувати параметричні методи для аналізу цих даних.\n")
            
            # Створюємо графіки
            self._create_normality_plots(data, name)
            
        except Exception as e:
            self.print_result(f"Помилка під час аналізу: {str(e)}\n", "error")
            import traceback
            traceback.print_exc()

    def _create_boxplot(self, data, labels, title):
        """Створює боксплот для порівняння груп"""
        try:
            # Очищаємо попередні графіки
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
                
            # Створюємо фігуру і вісь
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Створюємо боксплот
            box = ax.boxplot(data, patch_artist=True, labels=labels)
            
            # Налаштовуємо колір і стиль
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightpink', 'lightcyan']
            for patch, color in zip(box['boxes'], colors[:len(data)]):
                patch.set_facecolor(color)
            
            # Додаємо заголовок і мітки осей
            ax.set_title(title)
            ax.set_ylabel('Значення')
            
            # Додаємо точки даних
            for i, d in enumerate(data):
                x = np.random.normal(i+1, 0.04, size=len(d))
                ax.scatter(x, d, alpha=0.7, s=30)
            
            # Створюємо віджет для відображення графіка
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.print_result(f"Помилка при створенні графіка: {str(e)}\n", "error")

    def _create_normality_plots(self, data, title):
        """Створює графіки для оцінки нормальності розподілу"""
        try:
            # Очищаємо попередні графіки
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
                
            # Створюємо фігуру з двома підграфіками
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
            
            # 1. Гістограма з кривою нормального розподілу
            _, bins, _ = ax1.hist(data, bins=min(10, len(data)//2), alpha=0.6, color='skyblue', density=True, 
                                 label='Дані')
            
            # Додаємо криву нормального розподілу
            mu, sigma = np.mean(data), np.std(data)
            x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
            ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', label='Нормальний розподіл')
            
            ax1.set_title('Гістограма з кривою нормального розподілу')
            ax1.set_xlabel('Значення')
            ax1.set_ylabel('Щільність')
            ax1.legend()
            
            # 2. Q-Q плот
            from scipy import stats
            stats.probplot(data, dist="norm", plot=ax2)
            ax2.set_title('Q-Q плот')
            
            # Підпис для графіка
            fig.suptitle(f'Аналіз нормальності розподілу: {title}', fontsize=16)
            fig.tight_layout(rect=[0, 0, 1, 0.95])
            
            # Створюємо віджет для відображення графіка
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.print_result(f"Помилка при створенні графіка: {str(e)}\n", "error")

    def print_result(self, text, style=None):
        """Виведення форматованого тексту в поле результатів"""
        self.result_text.insert(tk.END, text)
        
        # Форматування тексту
        end_pos = self.result_text.index(tk.END)
        start_pos = f"{float(end_pos) - len(text)}"
        
        if style == "heading":
            self.result_text.tag_add("heading", start_pos, end_pos)
            self.result_text.tag_configure("heading", font=("Helvetica", 16, "bold"))
        elif style == "subheading":
            self.result_text.tag_add("subheading", start_pos, end_pos)
            self.result_text.tag_configure("subheading", font=("Helvetica", 15, "bold"))
        elif style == "success":
            self.result_text.tag_add("success", start_pos, end_pos)
            self.result_text.tag_configure("success", foreground="green")
        elif style == "warning":
            self.result_text.tag_add("warning", start_pos, end_pos)
            self.result_text.tag_configure("warning", foreground="red")
        elif style == "error":
            self.result_text.tag_add("error", start_pos, end_pos)
            self.result_text.tag_configure("error", foreground="red", font=("Helvetica", 12, "bold"))

    def save_results(self):
        """Збереження результатів у файл"""
        try:
            from datetime import datetime
            
            filename = filedialog.asksaveasfilename(
                initialdir="./",
                title="Зберегти результати",
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
                defaultextension=".txt",
                initialfile=f"результат_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
            )
            
            if filename:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("Успіх", f"Результати збережено у файл {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Неможливо зберегти файл: {str(e)}")

    def _setup_correlation_input(self):
        """Налаштування введення даних для кореляційного аналізу"""
        ttk.Label(
            self.data_frame, 
            text="Кореляційний аналіз - визначення сили та напрямку зв'язку між змінними",
            font=("Helvetica", 14)
        ).pack(pady=5)
        
        # Опис аналізу
        ttk.Label(
            self.data_frame,
            text="Цей аналіз дозволяє визначити ступінь лінійного зв'язку між двома змінними.\n"
                 "Рекомендується для неперервних даних з нормальним розподілом.",
            justify="left"
        ).pack(pady=10, anchor="w")
        
        # Фрейм для вибору методу кореляції
        method_frame = ttk.Frame(self.data_frame)
        method_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            method_frame, 
            text="Метод кореляції:"
        ).pack(side="left", padx=5)
        
        self.corr_method_var = tk.StringVar(value="pearson")
        methods = ttk.Combobox(
            method_frame,
            textvariable=self.corr_method_var,
            values=["pearson", "spearman", "kendall"],
            width=10,
            state="readonly"
        )
        methods.pack(side="left", padx=5)
        
        # Рівень значущості
        alpha_frame = ttk.Frame(self.data_frame)
        alpha_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            alpha_frame, 
            text="Рівень значущості α:"
        ).pack(side="left", padx=5)
        
        self.corr_alpha_var = tk.StringVar(value="0.05")
        alpha_combo = ttk.Combobox(
            alpha_frame,
            textvariable=self.corr_alpha_var,
            values=["0.01", "0.05", "0.1"],
            width=5,
            state="readonly"
        )
        alpha_combo.pack(side="left", padx=5)
        
        # Фрейм для змінної X
        x_frame = ttk.LabelFrame(self.data_frame, text="Змінна X")
        x_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            x_frame, 
            text="Назва змінної X:"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.x_name_entry = ttk.Entry(x_frame)
        self.x_name_entry.pack(fill="x", padx=5, pady=2)
        self.x_name_entry.insert(0, "Змінна X")
        
        ttk.Label(
            x_frame, 
            text="Дані X (через пробіл):"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.x_data_entry = ttk.Entry(x_frame)
        self.x_data_entry.pack(fill="x", padx=5, pady=2)
        self.x_data_entry.insert(0, "6.28 6.89 7.34 7.92 8.26 8.74 8.39 8.34 8.74 9.72 14.0 15.6 17.7 18.5 20.1 22.9 24.8 31.3 36.2 39.9")
        
        # Фрейм для змінної Y
        y_frame = ttk.LabelFrame(self.data_frame, text="Змінна Y")
        y_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            y_frame, 
            text="Назва змінної Y:"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.y_name_entry = ttk.Entry(y_frame)
        self.y_name_entry.pack(fill="x", padx=5, pady=2)
        self.y_name_entry.insert(0, "Змінна Y")
        
        ttk.Label(
            y_frame, 
            text="Дані Y (через пробіл):"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.y_data_entry = ttk.Entry(y_frame)
        self.y_data_entry.pack(fill="x", padx=5, pady=2)
        self.y_data_entry.insert(0, "5.11 5.82 6.96 7.39 7.07 7.73 7.81 7.56 8.00 8.45 8.77 9.01 9.13 9.45 9.77 10.1 10.6 10.8 11.3 12.4")
        
        # Кнопка для запуску аналізу
        ttk.Button(
            self.data_frame, 
            text="Виконати аналіз",
            command=self._run_correlation_analysis
        ).pack(pady=10)

    def _run_correlation_analysis(self):
        """Збір даних для кореляційного аналізу"""
        try:
            # Отримуємо дані з полів введення
            x_text = self.x_data_entry.get().strip()
            y_text = self.y_data_entry.get().strip()
            
            if not x_text or not y_text:
                messagebox.showerror("Помилка", "Дані відсутні для однієї або обох змінних")
                return
            
            try:
                # Перетворюємо рядки з числами в списки чисел
                x_data = [float(x) for x in x_text.split()]
                y_data = [float(y) for y in y_text.split()]
                
                if len(x_data) != len(y_data):
                    messagebox.showerror("Помилка", "Кількість значень у змінних повинна бути однаковою")
                    return
                    
                if len(x_data) < 3:
                    messagebox.showwarning("Попередження", "Для кореляційного аналізу рекомендується мати більше значень")
                
                self.group_data = [x_data, y_data]
                self.group_names = [
                    self.x_name_entry.get().strip() or "Змінна X",
                    self.y_name_entry.get().strip() or "Змінна Y"
                ]
                
                # Отримуємо метод і рівень значущості
                self.corr_method = self.corr_method_var.get()
                self.alpha = float(self.corr_alpha_var.get())
                
                # Запускаємо аналіз
                self._run_analysis_and_display("correlation")
                
            except ValueError:
                messagebox.showerror("Помилка", "Некоректні числові значення")
                return
                
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка під час аналізу: {str(e)}")

    def _perform_correlation_analysis(self):
        """Виконує кореляційний аналіз і виводить результати"""
        try:
            from scipy.stats import pearsonr, spearmanr, kendalltau
            import numpy as np
            
            # Дані
            x_data = self.group_data[0]
            y_data = self.group_data[1]
            x_name = self.group_names[0]
            y_name = self.group_names[1]
            method = self.corr_method
            alpha = self.alpha
            
            # Виводимо заголовок
            method_names = {
                'pearson': 'Пірсона',
                'spearman': 'Спірмена',
                'kendall': 'Кендалла'
            }
            self.print_result(f"--- КОРЕЛЯЦІЙНИЙ АНАЛІЗ ({method_names[method]}) ---\n", "heading")
            
            # Базова статистика
            self.print_result("\nОписова статистика:\n", "subheading")
            
            for name, data in zip([x_name, y_name], [x_data, y_data]):
                n = len(data)
                mean = np.mean(data)
                median = np.median(data)
                std_dev = np.std(data, ddof=1)
                min_val = np.min(data)
                max_val = np.max(data)
                
                self.print_result(f"{name}:\n")
                self.print_result(f"  Кількість значень: {n}\n")
                self.print_result(f"  Середнє: {mean:.4f}\n")
                self.print_result(f"  Медіана: {median:.4f}\n")
                self.print_result(f"  Стандартне відхилення: {std_dev:.4f}\n")
                self.print_result(f"  Мінімум: {min_val:.4f}\n")
                self.print_result(f"  Максимум: {max_val:.4f}\n\n")
            
            # Обчислюємо коефіцієнт кореляції
            if method == 'pearson':
                corr, p_value = pearsonr(x_data, y_data)
                method_desc = "лінійний зв'язок між нормально розподіленими даними"
            elif method == 'spearman':
                corr, p_value = spearmanr(x_data, y_data)
                method_desc = "монотонний зв'язок, менш чутливий до викидів"
            else:  # kendall
                corr, p_value = kendalltau(x_data, y_data)
                method_desc = "порядкова кореляція, найбільш стійкий до викидів"
            
            # Виводимо результати
            self.print_result("\nРезультати кореляційного аналізу:\n", "subheading")
            self.print_result(f"Метод: Кореляція {method_names[method]} ({method_desc})\n")
            self.print_result(f"Коефіцієнт кореляції: {corr:.4f}\n")
            self.print_result(f"p-значення: {p_value:.6f}\n")
            self.print_result(f"Рівень значущості α: {alpha}\n")
            
            # Інтерпретація коефіцієнту кореляції
            corr_abs = abs(corr)
            if corr_abs < 0.3:
                strength = "слабка"
            elif corr_abs < 0.7:
                strength = "середня"
            else:
                strength = "сильна"
            
            direction = "позитивний" if corr > 0 else "негативний"
            
            self.print_result(f"\nІнтерпретація величини: {strength} кореляція\n")
            self.print_result(f"Напрямок зв'язку: {direction}\n")
            
            # Перевірка статистичної значущості
            if p_value <= alpha:
                self.print_result(f"\nВИСНОВОК: Кореляція є статистично значущою (p ≤ {alpha}).\n", "success")
                self.print_result(f"Існує {strength} {direction} зв'язок між {x_name} та {y_name}.\n")
            else:
                self.print_result(f"\nВИСНОВОК: Кореляція не є статистично значущою (p > {alpha}).\n", "warning")
                self.print_result("Недостатньо доказів для підтвердження наявності зв'язку.\n")
            
            # Створюємо графік
            self._create_correlation_plot(x_data, y_data, x_name, y_name, corr, p_value)
            
        except Exception as e:
            self.print_result(f"Помилка під час аналізу: {str(e)}\n", "error")
            import traceback
            traceback.print_exc()

    def _setup_correlation_input(self):
        """Налаштування введення даних для кореляційного аналізу"""
        ttk.Label(
            self.data_frame, 
            text="Кореляційний аналіз - визначення сили та напрямку зв'язку між змінними",
            font=("Helvetica", 14)
        ).pack(pady=5)
        
        # Опис аналізу
        ttk.Label(
            self.data_frame,
            text="Цей аналіз дозволяє визначити ступінь лінійного зв'язку між двома змінними.\n"
                "Рекомендується для неперервних даних з нормальним розподілом.",
            justify="left"
        ).pack(pady=10, anchor="w")
        
        # Фрейм для вибору методу кореляції
        method_frame = ttk.Frame(self.data_frame)
        method_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            method_frame, 
            text="Метод кореляції:"
        ).pack(side="left", padx=5)
        
        self.corr_method_var = tk.StringVar(value="pearson")
        methods = ttk.Combobox(
            method_frame,
            textvariable=self.corr_method_var,
            values=["pearson", "spearman", "kendall"],
            width=10,
            state="readonly"
        )
        methods.pack(side="left", padx=5)
        
        # Рівень значущості
        alpha_frame = ttk.Frame(self.data_frame)
        alpha_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            alpha_frame, 
            text="Рівень значущості α:"
        ).pack(side="left", padx=5)
        
        self.corr_alpha_var = tk.StringVar(value="0.05")
        alpha_combo = ttk.Combobox(
            alpha_frame,
            textvariable=self.corr_alpha_var,
            values=["0.01", "0.05", "0.1"],
            width=5,
            state="readonly"
        )
        alpha_combo.pack(side="left", padx=5)
        
        # Фрейм для змінної X
        x_frame = ttk.LabelFrame(self.data_frame, text="Змінна X")
        x_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            x_frame, 
            text="Назва змінної X:"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.x_name_entry = ttk.Entry(x_frame)
        self.x_name_entry.pack(fill="x", padx=5, pady=2)
        self.x_name_entry.insert(0, "Змінна X")
        
        ttk.Label(
            x_frame, 
            text="Дані X (через пробіл):"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.x_data_entry = ttk.Entry(x_frame)
        self.x_data_entry.pack(fill="x", padx=5, pady=2)
        self.x_data_entry.insert(0, "1.2 2.3 3.4 4.5 5.6 6.7 7.8 8.9 9.0 10.1")
        
        # Фрейм для змінної Y
        y_frame = ttk.LabelFrame(self.data_frame, text="Змінна Y")
        y_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            y_frame, 
            text="Назва змінної Y:"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.y_name_entry = ttk.Entry(y_frame)
        self.y_name_entry.pack(fill="x", padx=5, pady=2)
        self.y_name_entry.insert(0, "Змінна Y")
        
        ttk.Label(
            y_frame, 
            text="Дані Y (через пробіл):"
        ).pack(anchor="w", padx=5, pady=2)
        
        self.y_data_entry = ttk.Entry(y_frame)
        self.y_data_entry.pack(fill="x", padx=5, pady=2)
        self.y_data_entry.insert(0, "2.1 3.1 3.8 4.9 5.7 7.1 7.6 9.2 8.8 10.4")
        
        # Кнопка для запуску аналізу
        ttk.Button(
            self.data_frame, 
            text="Виконати аналіз",
            command=self._run_correlation_analysis
        ).pack(pady=10)

    def _run_correlation_analysis(self):
        """Збір даних для кореляційного аналізу"""
        try:
            # Отримуємо дані з полів введення
            x_text = self.x_data_entry.get().strip()
            y_text = self.y_data_entry.get().strip()
            
            if not x_text or not y_text:
                messagebox.showerror("Помилка", "Дані відсутні для однієї або обох змінних")
                return
            
            try:
                # Перетворюємо рядки з числами в списки чисел
                x_data = [float(x) for x in x_text.split()]
                y_data = [float(y) for y in y_text.split()]
                
                if len(x_data) != len(y_data):
                    messagebox.showerror("Помилка", "Кількість значень у змінних повинна бути однаковою")
                    return
                    
                if len(x_data) < 3:
                    messagebox.showwarning("Попередження", "Для кореляційного аналізу рекомендується мати більше значень")
                
                self.group_data = [x_data, y_data]
                self.group_names = [
                    self.x_name_entry.get().strip() or "Змінна X",
                    self.y_name_entry.get().strip() or "Змінна Y"
                ]
                
                # Отримуємо метод і рівень значущості
                self.corr_method = self.corr_method_var.get()
                self.alpha = float(self.corr_alpha_var.get())
                
                # Запускаємо аналіз
                self._run_analysis_and_display("correlation")
                
            except ValueError:
                messagebox.showerror("Помилка", "Некоректні числові значення")
                return
                
        except Exception as e:
            messagebox.showerror("Помилка", f"Виникла помилка під час аналізу: {str(e)}")

    def _perform_correlation_analysis(self):
        """Виконує кореляційний аналіз і виводить результати"""
        try:
            from scipy.stats import pearsonr, spearmanr, kendalltau
            import numpy as np
            
            # Дані
            x_data = self.group_data[0]
            y_data = self.group_data[1]
            x_name = self.group_names[0]
            y_name = self.group_names[1]
            method = self.corr_method
            alpha = self.alpha
            
            # Виводимо заголовок
            method_names = {
                'pearson': 'Пірсона',
                'spearman': 'Спірмена',
                'kendall': 'Кендалла'
            }
            self.print_result(f"--- КОРЕЛЯЦІЙНИЙ АНАЛІЗ ({method_names[method]}) ---\n", "heading")
            
            # Базова статистика
            self.print_result("\nОписова статистика:\n", "subheading")
            
            for name, data in zip([x_name, y_name], [x_data, y_data]):
                n = len(data)
                mean = np.mean(data)
                median = np.median(data)
                std_dev = np.std(data, ddof=1)
                min_val = np.min(data)
                max_val = np.max(data)
                
                self.print_result(f"{name}:\n")
                self.print_result(f"  Кількість значень: {n}\n")
                self.print_result(f"  Середнє: {mean:.4f}\n")
                self.print_result(f"  Медіана: {median:.4f}\n")
                self.print_result(f"  Стандартне відхилення: {std_dev:.4f}\n")
                self.print_result(f"  Мінімум: {min_val:.4f}\n")
                self.print_result(f"  Максимум: {max_val:.4f}\n\n")
            
            # Обчислюємо коефіцієнт кореляції
            if method == 'pearson':
                corr, p_value = pearsonr(x_data, y_data)
                method_desc = "лінійний зв'язок між нормально розподіленими даними"
            elif method == 'spearman':
                corr, p_value = spearmanr(x_data, y_data)
                method_desc = "монотонний зв'язок, менш чутливий до викидів"
            else:  # kendall
                corr, p_value = kendalltau(x_data, y_data)
                method_desc = "порядкова кореляція, найбільш стійкий до викидів"
            
            # Виводимо результати
            self.print_result("\nРезультати кореляційного аналізу:\n", "subheading")
            self.print_result(f"Метод: Кореляція {method_names[method]} ({method_desc})\n")
            self.print_result(f"Коефіцієнт кореляції: {corr:.4f}\n")
            self.print_result(f"p-значення: {p_value:.6f}\n")
            self.print_result(f"Рівень значущості α: {alpha}\n")
            
            # Інтерпретація коефіцієнту кореляції
            corr_abs = abs(corr)
            if corr_abs < 0.3:
                strength = "слабка"
            elif corr_abs < 0.7:
                strength = "середня"
            else:
                strength = "сильна"
            
            direction = "позитивний" if corr > 0 else "негативний"
            
            self.print_result(f"\nІнтерпретація величини: {strength} кореляція\n")
            self.print_result(f"Напрямок зв'язку: {direction}\n")
            
            # Перевірка статистичної значущості
            if p_value <= alpha:
                self.print_result(f"\nВИСНОВОК: Кореляція є статистично значущою (p ≤ {alpha}).\n", "success")
                self.print_result(f"Існує {strength} {direction} зв'язок між {x_name} та {y_name}.\n")
            else:
                self.print_result(f"\nВИСНОВОК: Кореляція не є статистично значущою (p > {alpha}).\n", "warning")
                self.print_result("Недостатньо доказів для підтвердження наявності зв'язку.\n")
            
            # Створюємо графік
            self._create_correlation_plot(x_data, y_data, x_name, y_name, corr, p_value)
            
        except Exception as e:
            self.print_result(f"Помилка під час аналізу: {str(e)}\n", "error")
            import traceback
            traceback.print_exc()

    def _create_correlation_plot(self, x_data, y_data, x_name, y_name, corr, p_value):
        """Створює діаграму розсіювання для кореляційного аналізу"""
        try:
            # Очищаємо попередні графіки
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
                
            # Створюємо фігуру і вісь
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Створюємо діаграму розсіювання
            ax.scatter(x_data, y_data, alpha=0.7, s=50, color='steelblue')
            
            # Додаємо лінію регресії
            m, b = np.polyfit(x_data, y_data, 1)
            x_line = np.linspace(min(x_data), max(x_data), 100)
            y_line = m * x_line + b
            ax.plot(x_line, y_line, color='red', linestyle='--')
            
            # Додаємо рівняння регресії
            equation = f'y = {m:.4f}x + {b:.4f}'
            ax.text(0.05, 0.95, equation, transform=ax.transAxes, 
                    fontsize=10, verticalalignment='top')
            
            # Додаємо коефіцієнт кореляції
            if p_value < 0.001:
                p_text = "p < 0.001"
            else:
                p_text = f"p = {p_value:.4f}"
            corr_text = f'r = {corr:.4f} ({p_text})'
            ax.text(0.05, 0.90, corr_text, transform=ax.transAxes,
                    fontsize=10, verticalalignment='top')
            
            # Налаштовуємо осі та заголовок
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            ax.set_title('Кореляційне поле')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Створюємо віджет для відображення графіка
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.print_result(f"Помилка при створенні графіка: {str(e)}\n", "error")

if __name__ == "__main__":
    try:
        app = StatApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        traceback.print_exc()
        
        # Write to log file
        with open("error_log.txt", "w") as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())