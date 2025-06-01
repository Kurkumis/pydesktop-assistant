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
        self.geometry("600x800")
        self.calendar_manager = CalendarManager()
        self._create_widgets()
        self._refresh_events_list()

    def _create_widgets(self):
        """Создание элементов интерфейса"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Календарь для выбора даты
        calendar_frame = ttk.Frame(main_frame)
        calendar_frame.pack(fill=tk.X, pady=10)

        self.calendar = Calendar(
            calendar_frame,
            selectmode="day",
            date_pattern="y-mm-dd",
            locale="ru_RU"
        )
        self.calendar.pack(pady=5)
        self.calendar.bind("<<CalendarSelected>>", self._date_selected)

        # Форма добавления события
        form_frame = ttk.LabelFrame(main_frame, text="Добавить событие")
        form_frame.pack(fill=tk.X, pady=10)

        # Название
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_entry = ttk.Entry(form_frame, width=30)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Время
        ttk.Label(form_frame, text="Время:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.time_var = tk.StringVar(value="12:00")
        self.time_entry = ttk.Entry(form_frame, textvariable=self.time_var, width=8)
        self.time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Кнопка добавления
        ttk.Button(
            form_frame,
            text="Добавить событие",
            command=self._add_event
        ).grid(row=3, column=1, pady=10, sticky=tk.E)

        # Список событий
        events_frame = ttk.LabelFrame(main_frame, text="Предстоящие события")
        events_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("id", "date", "time", "title", "description")
        self.events_list = ttk.Treeview(
            events_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.events_list.heading("id", text="ID")
        self.events_list.heading("date", text="Дата")
        self.events_list.heading("time", text="Время")
        self.events_list.heading("title", text="Название")
        self.events_list.heading("description", text="Описание")

        self.events_list.column("id", width=50, anchor=tk.CENTER)
        self.events_list.column("date", width=100)
        self.events_list.column("time", width=80)
        self.events_list.column("title", width=150)
        self.events_list.column("description", width=300)

        scroll_y = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.events_list.yview)
        self.events_list.configure(yscrollcommand=scroll_y.set)

        self.events_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка удаления
        ttk.Button(
            main_frame,
            text="Удалить выбранное событие",
            command=self._delete_event
        ).pack(pady=10)

    def _date_selected(self, event):
        """Обработчик выбора даты в календаре"""
        pass  # Можно использовать для фильтрации событий

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

            # Добавляем событие
            self.calendar_manager.add_event(title, description, event_datetime)
            self._refresh_events_list()

            # Очищаем поля
            self.title_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.time_var.set("12:00")

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат времени!\nИспользуйте ЧЧ:ММ")

    def _delete_event(self):
        """Удаление выбранного события"""
        selected = self.events_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите событие для удаления!")
            return

        event_id = int(self.events_list.item(selected[0], "values")[0])
        self.calendar_manager.delete_event(event_id)
        self._refresh_events_list()

    def _refresh_events_list(self):
        """Обновление списка событий"""
        for item in self.events_list.get_children():
            self.events_list.delete(item)

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
