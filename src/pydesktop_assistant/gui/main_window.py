import tkinter as tk
from tkinter import ttk
from ..modules.calculator.gui import CalculatorGUI
from ..modules.notes.gui import NotesGUI
from ..modules.task_manager.gui import TaskManagerGUI
from ..modules.timer.gui import TimerGUI
from ..modules.calendar.gui import CalendarGUI


class MainWindow(tk.Tk):
    """Главное окно приложения PyDesktop Assistant"""

    def __init__(self):
        super().__init__()

        # Заголовок и начальные параметры окна
        self.title("PyDesktop Assistant")
        self.geometry("450x350")
        self.minsize(350, 300)

        # Применяем тему и стили
        self._setup_style()

        # Создаём и размещаем все виджеты
        self._create_widgets()

    def _setup_style(self):
        """Настройка стиля для ttk-виджетов"""
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use(style.theme_use())

        # Настраиваем стиль для кнопок: шрифт, отступы
        style.configure(
            "TButton",
            font=("Segoe UI", 12),
            padding=(10, 5)
        )

        # Стиль для заголовка
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 16, "bold"),
            foreground="#333333"
        )

    def _create_widgets(self):
        """Создаём и размещаем основные виджеты"""
        # Центральный фрейм с отступами
        container = ttk.Frame(self, padding=20)
        container.grid(sticky="nsew")

        # Делаем так, чтобы фрейм растягивался при изменении размера окна
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        # Заголовок вверху
        header = ttk.Label(container, text="PyDesktop Assistant", style="Header.TLabel")
        header.grid(row=0, column=0, pady=(0, 15))

        # Фрейм для кнопок
        buttons_frame = ttk.Frame(container)
        buttons_frame.grid(row=1, column=0, sticky="nsew")

        # Настроим сетку внутри buttons_frame
        buttons_frame.columnconfigure((0,), weight=1)
        for i in range(5):
            buttons_frame.rowconfigure(i, weight=1)

        # Список кнопок: текст и соответствующий метод-обработчик
        buttons = [
            ("Калькулятор", self.open_calculator),
            ("Заметки", self.open_notes),
            ("Менеджер задач", self.open_task_manager),
            ("Таймер", self.open_timer),
            ("Календарь", self.open_calendar),
        ]

        # Создаём кнопки по порядку
        for idx, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(buttons_frame, text=text, command=cmd)
            btn.grid(row=idx, column=0, sticky="ew", pady=5)

    def open_calculator(self):
        """Открыть окно калькулятора"""
        CalculatorGUI(self)

    def open_notes(self):
        """Открыть окно заметок"""
        NotesGUI(self)

    def open_task_manager(self):
        """Открыть окно менеджера задач"""
        TaskManagerGUI(self)

    def open_timer(self):
        """Открыть окно таймера"""
        TimerGUI(self)

    def open_calendar(self):
        """Открыть окно календаря"""
        CalendarGUI(self)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
