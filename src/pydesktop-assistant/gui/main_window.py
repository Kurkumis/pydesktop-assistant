import tkinter as tk
from tkinter import ttk
from ..modules.calculator.gui import CalculatorGUI
from ..modules.notes.gui import NotesGUI
from ..modules.task_manager.gui import TaskManagerGUI


class MainWindow(tk.Tk):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.title("PyDesktop Assistant")
        self.geometry("400x300")
        self._create_widgets()

    def _create_widgets(self):
        """Кнопки для модулей"""
        ttk.Button(
            self,
            text="Калькулятор",
            command=self.open_calculator
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Заметки",
            command=self.open_notes
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Менеджер задач",
            command=self.open_task_manager
        ).pack(pady=10)

    def open_task_manager(self):
        """Открыть окно менеджера задач"""
        TaskManagerGUI(self)

    def open_notes(self):
        """Открыть окно заметок"""
        NotesGUI(self)

    def open_calculator(self):
        """Открыть окно калькулятора"""
        CalculatorGUI(self)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
