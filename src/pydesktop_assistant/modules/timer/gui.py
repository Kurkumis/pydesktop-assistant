import tkinter as tk
from tkinter import ttk, messagebox
from .timer import TimerManager


class TimerGUI(tk.Toplevel):
    """Окно управления таймерами"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Таймер")
        self.geometry("600x400")
        self.timer_manager = TimerManager()
        self._create_widgets()
        self._update_timers_list()

    def _create_widgets(self):
        """Создание элементов интерфейса"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Поля ввода времени
        time_frame = ttk.LabelFrame(main_frame, text="Установите время")
        time_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=5)

        # Часы
        ttk.Label(time_frame, text="Часы:").grid(row=0, column=0, padx=5, pady=5)
        self.hours_var = tk.IntVar(value=0)
        self.hours_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=24,
            width=5,
            textvariable=self.hours_var
        )
        self.hours_spin.grid(row=0, column=1, padx=5, pady=5)

        # Минуты
        ttk.Label(time_frame, text="Минуты:").grid(row=0, column=2, padx=5, pady=5)
        self.minutes_var = tk.IntVar(value=0)
        self.minutes_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.minutes_var
        )
        self.minutes_spin.grid(row=0, column=3, padx=5, pady=5)

        # Секунды
        ttk.Label(time_frame, text="Секунды:").grid(row=0, column=4, padx=5, pady=5)
        self.seconds_var = tk.IntVar(value=0)
        self.seconds_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.seconds_var
        )
        self.seconds_spin.grid(row=0, column=5, padx=5, pady=5)

        # Поле сообщения
        ttk.Label(main_frame, text="Сообщение:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.message_entry = ttk.Entry(main_frame)
        self.message_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        # Кнопка запуска
        ttk.Button(
            main_frame,
            text="Запустить таймер",
            command=self._start_timer
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # Список активных таймеров
        ttk.Label(main_frame, text="Активные таймеры:").grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.timers_list = ttk.Treeview(
            main_frame,
            columns=("id", "time_left", "message"),
            show="headings",
            height=5
        )
        self.timers_list.heading("id", text="ID")
        self.timers_list.heading("time_left", text="Осталось времени")
        self.timers_list.heading("message", text="Сообщение")
        self.timers_list.column("id", width=50, anchor=tk.CENTER)
        self.timers_list.column("time_left", width=100)
        self.timers_list.column("message", width=200)
        self.timers_list.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW)

        # Кнопка отмены
        ttk.Button(
            main_frame,
            text="Отменить выбранный таймер",
            command=self._cancel_timer
        ).grid(row=5, column=0, columnspan=2, pady=10)

        # Настройка веса строк и столбцов
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def _start_timer(self):
        """Запуск нового таймера"""
        try:
            # Получаем значения времени
            hours = self.hours_var.get()
            minutes = self.minutes_var.get()
            seconds = self.seconds_var.get()

            # Вычисляем общее время в секундах
            total_seconds = hours * 3600 + minutes * 60 + seconds

            message = self.message_entry.get().strip()

            if total_seconds <= 0:
                messagebox.showerror("Ошибка", "Установите время для таймера!")
                return
            if not message:
                messagebox.showerror("Ошибка", "Введите сообщение для таймера!")
                return

            # Запускаем таймер
            self.timer_manager.start_timer(total_seconds, message)

            # Обновляем список
            self._update_timers_list()

            # Очищаем поля
            self.hours_var.set(0)
            self.minutes_var.set(0)
            self.seconds_var.set(0)
            self.message_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное время!")

    def _cancel_timer(self):
        """Отмена выбранного таймера"""
        selected = self.timers_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите таймер для отмены!")
            return

        timer_id = int(self.timers_list.item(selected[0], "values")[0])
        self.timer_manager.cancel_timer(timer_id)
        self._update_timers_list()

    def _update_timers_list(self):
        """Обновление списка активных таймеров"""
        for item in self.timers_list.get_children():
            self.timers_list.delete(item)

        for timer in self.timer_manager.get_active_timers():
            # Форматируем время в ЧЧ:ММ:СС
            remaining = timer["remaining"]
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            self.timers_list.insert(
                "",
                tk.END,
                values=(timer["id"], time_str, timer["message"])
            )

        # Обновляем список каждую секунду
        self.after(1000, self._update_timers_list)
