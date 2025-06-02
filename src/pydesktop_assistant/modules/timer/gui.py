import tkinter as tk
from tkinter import ttk, messagebox
from .timer import TimerManager


class TimerGUI(tk.Toplevel):
    """Окно управления таймерами"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Таймер")
        self.geometry("650x450")
        self.minsize(600, 400)

        # Инициализируем менеджер таймеров
        self.timer_manager = TimerManager()

        # Настраиваем стили
        self._setup_style()

        # Создаём и размещаем виджеты
        self._create_widgets()

        # Запускаем обновление списка таймеров
        self._update_timers_list()

    def _setup_style(self):
        """Настройка стиля для ttk-виджетов"""
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use(style.theme_use())

        # Стиль для заголовков LabelFrame
        style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 12, "bold"),
            foreground="#444444"
        )

        # Стиль для обычных меток
        style.configure(
            "TLabel",
            font=("Segoe UI", 10),
            foreground="#333333"
        )

        # Стиль для кнопок
        style.configure(
            "TButton",
            font=("Segoe UI", 11),
            padding=(8, 4)
        )

        # Стиль для Treeview
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            foreground="#222222"
        )
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=24
        )

    def _create_widgets(self):
        """Создание и расположение всех виджетов окна"""
        # Основной контейнер с отступами
        container = ttk.Frame(self, padding=15)
        container.grid(sticky="nsew")

        # Адаптивность контейнера
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)
        container.columnconfigure(1, weight=1)

        # ---- Заголовок окна ----
        header = ttk.Label(
            container,
            text="Таймер",
            font=("Segoe UI", 16, "bold"),
            foreground="#2E4053"
        )
        header.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # ---- Верхняя часть: Настройка времени ----
        time_frame = ttk.LabelFrame(container, text="Установите время")
        time_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        for i in range(6):
            time_frame.columnconfigure(i, weight=1)

        # Метка и поле "Часы"
        ttk.Label(time_frame, text="Часы:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.hours_var = tk.IntVar(value=0)
        self.hours_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=24,
            width=5,
            textvariable=self.hours_var
        )
        self.hours_spin.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Метка и поле "Минуты"
        ttk.Label(time_frame, text="Минуты:").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        self.minutes_var = tk.IntVar(value=0)
        self.minutes_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.minutes_var
        )
        self.minutes_spin.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Метка и поле "Секунды"
        ttk.Label(time_frame, text="Секунды:").grid(
            row=0, column=4, sticky="w", padx=5, pady=5
        )
        self.seconds_var = tk.IntVar(value=0)
        self.seconds_spin = ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.seconds_var
        )
        self.seconds_spin.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        # ---- Средняя часть: Сообщение для таймера ----
        ttk.Label(container, text="Сообщение:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.message_entry = ttk.Entry(container)
        self.message_entry.grid(
            row=2, column=1, sticky="ew", padx=5, pady=5
        )

        # ---- Кнопка запуска таймера ----
        start_btn = ttk.Button(
            container,
            text="Запустить таймер",
            command=self._start_timer
        )
        start_btn.grid(row=3, column=0, columnspan=2, pady=(10, 15))

        # ---- Нижняя часть: Список активных таймеров ----
        timers_frame = ttk.LabelFrame(container, text="Активные таймеры")
        timers_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        timers_frame.rowconfigure(0, weight=1)
        timers_frame.columnconfigure(0, weight=1)

        columns = ("id", "time_left", "message")
        self.timers_list = ttk.Treeview(
            timers_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=8
        )

        # Заголовки и настройки колонок
        self.timers_list.heading("id", text="ID")
        self.timers_list.heading("time_left", text="Осталось времени")
        self.timers_list.heading("message", text="Сообщение")

        self.timers_list.column("id", width=50, anchor="center")
        self.timers_list.column("time_left", width=120, anchor="center")
        self.timers_list.column("message", width=380)

        # Вертикальный скроллбар
        scroll_y = ttk.Scrollbar(
            timers_frame, orient="vertical", command=self.timers_list.yview
        )
        self.timers_list.configure(yscrollcommand=scroll_y.set)

        self.timers_list.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # ---- Кнопка отмены таймера ----
        cancel_btn = ttk.Button(
            container,
            text="Отменить выбранный таймер",
            command=self._cancel_timer
        )
        cancel_btn.grid(row=5, column=0, columnspan=2, pady=(0, 10))

    def _start_timer(self):
        """Запуск нового таймера"""
        try:
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

            # Запускаем таймер в менеджере
            self.timer_manager.start_timer(total_seconds, message)

            # Обновляем список таймеров
            self._update_timers_list()

            # Очищаем поля
            self.hours_var.set(0)
            self.minutes_var.set(0)
            self.seconds_var.set(0)
            self.message_entry.delete(0, tk.END)

        except Exception:
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
        # Очищаем текущий список
        for item in self.timers_list.get_children():
            self.timers_list.delete(item)

        # Заполняем новыми данными
        for timer in self.timer_manager.get_active_timers():
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

        # Повторяем обновление каждую секунду
        self.after(1000, self._update_timers_list)
