import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
from .calendar import CalendarManager


class CalendarGUI(tk.Toplevel):
    """Окно управления календарём"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Календарь событий")
        self.geometry("650x950")
        self.minsize(600, 700)

        # Инициализируем менеджер событий
        self.calendar_manager = CalendarManager()

        # Настраиваем стили
        self._setup_style()

        # Создаём все виджеты
        self._create_widgets()

        # Заполняем список текущими событиями
        self._refresh_events_list()

    def _setup_style(self):
        """Настройка стиля для ttk-виджетов"""
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except tk.TclError:
            style.theme_use(style.theme_use())

        # Стиль для заголовка в LabelFrame
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

        # Стиль для элементов Treeview
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
        """Создаём и размещаем все виджеты окна"""
        # Основной фрейм с отступами
        container = ttk.Frame(self, padding=15)
        container.grid(sticky="nsew")

        # Для адаптивности: основной фрейм растягивается
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)

        # ---- Заголовок окна ----
        header = ttk.Label(
            container,
            text="Календарь событий",
            font=("Segoe UI", 16, "bold"),
            foreground="#2E4053"
        )
        header.grid(row=0, column=0, pady=(0, 15))

        # ---- Верхняя часть: Календарь ----
        calendar_frame = ttk.LabelFrame(container, text="Выберите дату")
        calendar_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        calendar_frame.columnconfigure(0, weight=1)

        self.calendar = Calendar(
            calendar_frame,
            selectmode="day",
            date_pattern="y-mm-dd",
            locale="ru_RU"
        )
        self.calendar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.calendar.bind("<<CalendarSelected>>", self._date_selected)

        # ---- Средняя часть: Форма добавления события ----
        form_frame = ttk.LabelFrame(container, text="Добавить новое событие")
        form_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        for i in range(2):
            form_frame.columnconfigure(i, weight=1)

        # Метка и поле "Название"
        ttk.Label(form_frame, text="Название:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Метка и поле "Описание"
        ttk.Label(form_frame, text="Описание:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.description_entry = ttk.Entry(form_frame)
        self.description_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Метка и поле "Время"
        ttk.Label(form_frame, text="Время (ЧЧ:ММ):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.time_var = tk.StringVar(value="12:00")
        self.time_entry = ttk.Entry(form_frame, textvariable=self.time_var, width=8)
        self.time_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Кнопка добавления события
        add_btn = ttk.Button(
            form_frame,
            text="Добавить событие",
            command=self._add_event
        )
        add_btn.grid(row=3, column=1, sticky="e", padx=5, pady=(10, 5))

        # ---- Нижняя часть: Список/таблица событий ----
        events_frame = ttk.LabelFrame(container, text="Список предстоящих событий")
        events_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        events_frame.rowconfigure(0, weight=1)
        events_frame.columnconfigure(0, weight=1)

        columns = ("id", "date", "time", "title", "description")
        self.events_list = ttk.Treeview(
            events_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=12
        )

        # Заголовки и колонки
        self.events_list.heading("id", text="ID")
        self.events_list.heading("date", text="Дата")
        self.events_list.heading("time", text="Время")
        self.events_list.heading("title", text="Название")
        self.events_list.heading("description", text="Описание")

        self.events_list.column("id", width=50, anchor="center")
        self.events_list.column("date", width=100, anchor="center")
        self.events_list.column("time", width=80, anchor="center")
        self.events_list.column("title", width=180)
        self.events_list.column("description", width=250)

        # Вертикальный скролл
        scroll_y = ttk.Scrollbar(
            events_frame, orient="vertical", command=self.events_list.yview
        )
        self.events_list.configure(yscrollcommand=scroll_y.set)

        self.events_list.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # Кнопка удаления ниже таблицы
        delete_btn = ttk.Button(
            container,
            text="Удалить выбранное событие",
            command=self._delete_event
        )
        delete_btn.grid(row=4, column=0, sticky="e", padx=5, pady=(0, 10))

    def _date_selected(self, event):
        pass

    def _add_event(self):
        """Добавление нового события"""
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        selected_date = self.calendar.get_date()

        if not title:
            messagebox.showerror("Ошибка", "Введите название события!")
            return

        try:
            # Парсим дату и время
            event_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
            event_time = datetime.datetime.strptime(self.time_var.get(), "%H:%M").time()
            event_datetime = datetime.datetime.combine(event_date, event_time)

            # Проверяем, что событие в будущем
            if event_datetime < datetime.datetime.now():
                messagebox.showerror("Ошибка", "Нельзя добавлять события в прошлом!")
                return

            # Добавляем событие в менеджер
            self.calendar_manager.add_event(title, description, event_datetime)
            self._refresh_events_list()

            # Очищаем поля
            self.title_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.time_var.set("12:00")

        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Некорректный формат времени!\nИспользуйте ЧЧ:ММ"
            )

    def _delete_event(self):
        """Удаление выбранного события из таблицы и БД"""
        selected = self.events_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите событие для удаления!")
            return

        # Получаем ID из выбранной строки
        event_id = int(self.events_list.item(selected[0], "values")[0])
        self.calendar_manager.delete_event(event_id)
        self._refresh_events_list()

    def _refresh_events_list(self):
        """Обновление списка (таблицы) событий"""
        # Удаляем всё из текущей таблицы
        for item in self.events_list.get_children():
            self.events_list.delete(item)

        # Заполняем новыми значениями
        for event in self.calendar_manager.get_all_events():
            event_date = event.event_datetime.strftime("%d.%m.%Y")
            event_time = event.event_datetime.strftime("%H:%M")

            self.events_list.insert(
                "",
                tk.END,
                values=(
                    event.id,
                    event_date,
                    event_time,
                    event.title,
                    event.description
                )
            )
