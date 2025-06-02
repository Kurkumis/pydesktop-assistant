import tkinter as tk
from tkinter import ttk, messagebox
from .calculator import Calculator


class CalculatorGUI(tk.Toplevel):
    """Класс графического интерфейса калькулятора"""

    def __init__(self, master=None):
        super().__init__(master)
        self.calculator = Calculator()
        self.title("Калькулятор")
        self.geometry("320x450")
        self.minsize(300, 420)
        self.current_expression = ""

        # Настраиваем стили
        self._setup_style()

        # Создаём и располагаем виджеты
        self._create_widgets()

    def _setup_style(self):
        """Настройка стиля для ttk-виджетов"""
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use(style.theme_use())

        # Стиль для поля вывода (Entry)
        style.configure(
            "Calculator.TEntry",
            font=("Segoe UI", 20),
            padding=15
        )

        # Стиль для кнопок
        style.configure(
            "Calculator.TButton",
            font=("Segoe UI", 14),
            padding=(10, 10)
        )

    def _create_widgets(self):
        """Создание и расположение всех виджетов окна"""
        # Основной контейнер с отступами
        container = ttk.Frame(self, padding=10)
        container.grid(sticky="nsew")

        # Адаптивность контейнера
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        # ---- Поле вывода ----
        self.result_var = tk.StringVar(value="0")
        entry = ttk.Entry(
            container,
            textvariable=self.result_var,
            style="Calculator.TEntry",
            justify="right"
        )
        entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # ---- Сетка кнопок ----
        buttons_frame = ttk.Frame(container)
        buttons_frame.grid(row=1, column=0, sticky="nsew")
        for i in range(6):
            buttons_frame.rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.columnconfigure(j, weight=1)

        # Определяем кнопки: текст, строка, столбец
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('C', 5, 0), ('^', 5, 3)
        ]

        for (text, row, col) in buttons:
            btn = ttk.Button(
                buttons_frame,
                text=text,
                style="Calculator.TButton",
                command=lambda t=text: self._on_button_click(t)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

    def _on_button_click(self, char: str):
        """Обработка нажатия кнопок калькулятора"""
        if char == 'C':
            self.current_expression = ""
            self.result_var.set("0")
        elif char == '=':
            try:
                result = self.calculator.calculate(self.current_expression)
                if self.calculator.error_message:
                    self.result_var.set("Error")
                    messagebox.showerror("Ошибка", self.calculator.error_message)
                else:
                    self.result_var.set(str(result))
                    self.current_expression = str(result)
            except Exception:
                self.result_var.set("Error")
        else:
            if self.current_expression == "0" or self.result_var.get() == "Error":
                self.current_expression = char
            else:
                self.current_expression += char
            self.result_var.set(self.current_expression)
