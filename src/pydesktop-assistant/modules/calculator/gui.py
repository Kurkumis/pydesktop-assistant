import tkinter as tk
from tkinter import ttk
from .calculator import Calculator


class CalculatorGUI(tk.Toplevel):
    """Класс графического интерфейса калькулятора"""
    def __init__(self, master=None):
        super().__init__(master)
        self.calculator = Calculator()
        self.title("Калькулятор")
        self.geometry("300x400")
        self.current_expression = ""
        self._create_widgets()

    def _create_widgets(self):
        """Создание элементов интерфейса"""
        self.result_var = tk.StringVar(value="0")

        # Поле вывода
        entry = ttk.Entry(
            self,
            textvariable=self.result_var,
            font=('Arial', 20),
            justify='right'
        )
        entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

        # Кнопки
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('C', 5, 0), ('^', 5, 3)
        ]

        for (text, row, col) in buttons:
            ttk.Button(
                self,
                text=text,
                command=lambda t=text: self._on_button_click(t)
            ).grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        # Настройка сетки
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for i in range(4):
            self.columnconfigure(i, weight=1)

    def _on_button_click(self, char: str):
        """Обработчик нажатий"""
        if char == 'C':
            self.current_expression = ""
            self.result_var.set('0')
        elif char == '=':
            try:
                result = self.calculator.calculate(self.current_expression)
                self.result_var.set(str(result))
                self.current_expression = str(result)
            except Exception as e:
                self.result_var.set("Error")
                self.current_expression = ""
        else:
            self.current_expression += char
            self.result_var.set(self.current_expression)
