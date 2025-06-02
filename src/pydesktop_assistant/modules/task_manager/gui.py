import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from .task_manager import TaskManager


class TaskManagerGUI(tk.Toplevel):
    """Окно управления задачами"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Менеджер задач")
        self.geometry("850x550")
        self.minsize(800, 500)

        # Инициализируем менеджер задач
        self.task_manager = TaskManager()

        # Настраиваем стили
        self._setup_style()

        # Создаём и размещаем виджеты
        self._create_widgets()

        # Заполняем таблицу текущими задачами
        self._refresh_tasks_list()

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
        container.rowconfigure(2, weight=1)  # область с таблицей растягивается
        container.columnconfigure(0, weight=1)

        # ---- Заголовок окна ----
        header = ttk.Label(
            container,
            text="Менеджер задач",
            font=("Segoe UI", 16, "bold"),
            foreground="#2E4053"
        )
        header.grid(row=0, column=0, pady=(0, 15))

        # ---- Верхняя часть: Форма ввода новой задачи ----
        form_frame = ttk.LabelFrame(container, text="Добавить новую задачу")
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        # Настраиваем колонки формы: метка (col 0), поля ввода (col 1 и 2)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)

        # Метка и поле "Задача"
        ttk.Label(form_frame, text="Задача:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Метка и Combobox "Приоритет"
        ttk.Label(form_frame, text="Приоритет:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.priority_var = tk.StringVar()
        self.priority_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.priority_var,
            values=list(TaskManager.PRIORITIES.values()),
            state="readonly"
        )
        self.priority_combobox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.priority_combobox.current(1)  # по умолчанию средний приоритет

        # Метка и DateEntry "Срок выполнения"
        ttk.Label(form_frame, text="Срок выполнения (дата):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.due_date_entry = DateEntry(form_frame, date_pattern="y-mm-dd", locale="ru_RU")
        self.due_date_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Метка и поле "Время"
        ttk.Label(form_frame, text="Время (ЧЧ:ММ):").grid(
            row=2, column=2, sticky="w", padx=5, pady=5
        )
        self.time_var = tk.StringVar(value="12:00")
        self.time_entry = ttk.Entry(form_frame, textvariable=self.time_var, width=8)
        self.time_entry.grid(row=2, column=2, sticky="e", padx=5, pady=5)

        # Кнопка добавления задачи
        add_btn = ttk.Button(
            form_frame,
            text="Добавить задачу",
            command=self._add_task
        )
        add_btn.grid(row=3, column=2, sticky="e", padx=5, pady=(10, 5))

        # ---- Нижняя часть: Список (таблица) задач ----
        tasks_frame = ttk.LabelFrame(container, text="Список задач")
        tasks_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        tasks_frame.rowconfigure(0, weight=1)
        tasks_frame.columnconfigure(0, weight=1)

        columns = ("id", "title", "priority", "due_date", "status")
        self.tasks_list = ttk.Treeview(
            tasks_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=12
        )

        # Заголовки и настройки колонок
        self.tasks_list.heading("id", text="ID")
        self.tasks_list.heading("title", text="Задача")
        self.tasks_list.heading("priority", text="Приоритет")
        self.tasks_list.heading("due_date", text="Срок")
        self.tasks_list.heading("status", text="Статус")

        self.tasks_list.column("id", width=50, anchor="center")
        self.tasks_list.column("title", width=250)
        self.tasks_list.column("priority", width=120, anchor="center")
        self.tasks_list.column("due_date", width=180, anchor="center")
        self.tasks_list.column("status", width=120, anchor="center")

        # Вертикальный скроллбар
        scroll_y = ttk.Scrollbar(
            tasks_frame, orient="vertical", command=self.tasks_list.yview
        )
        self.tasks_list.configure(yscrollcommand=scroll_y.set)

        self.tasks_list.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # ---- Кнопки управления задачами ----
        button_frame = ttk.Frame(container)
        button_frame.grid(row=3, column=0, sticky="e", padx=5, pady=(0, 5))

        delete_btn = ttk.Button(
            button_frame,
            text="Удалить задачу",
            command=self._delete_task
        )
        delete_btn.pack(side="left", padx=5)

        toggle_btn = ttk.Button(
            button_frame,
            text="Пометить выполненной",
            command=self._toggle_status
        )
        toggle_btn.pack(side="left", padx=5)

    def _parse_datetime(self) -> datetime:
        """Парсит дату и время из полей ввода"""
        date = self.due_date_entry.get_date()
        time_obj = datetime.strptime(self.time_var.get(), "%H:%M").time()
        return datetime.combine(date, time_obj)

    def _add_task(self):
        """Добавление новой задачи"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Введите название задачи!")
            return

        # Получаем ключ приоритета по выбранному значению
        priority_key = next(
            k for k, v in TaskManager.PRIORITIES.items()
            if v == self.priority_var.get()
        )

        try:
            due_date = self._parse_datetime()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат времени!\nИспользуйте ЧЧ:ММ")
            return

        self.task_manager.create_task(title, priority_key, due_date)
        self.title_entry.delete(0, tk.END)
        self._refresh_tasks_list()

    def _delete_task(self):
        """Удаление выбранной задачи"""
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите задачу для удаления!")
            return

        task_id = int(self.tasks_list.item(selected[0], "values")[0])
        self.task_manager.delete_task(task_id)
        self._refresh_tasks_list()

    def _toggle_status(self):
        """Переключение статуса задачи (выполнена/не выполнена)"""
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите задачу!")
            return

        task_id = int(self.tasks_list.item(selected[0], "values")[0])
        self.task_manager.toggle_task_status(task_id)
        self._refresh_tasks_list()

    def _refresh_tasks_list(self):
        """Обновление списка задач в таблице"""
        # Очищаем текущий список
        for item in self.tasks_list.get_children():
            self.tasks_list.delete(item)

        # Получаем все задачи и сортируем их по ID
        tasks = sorted(
            self.task_manager.get_all_tasks(),
            key=lambda x: x.id
        )

        for task in tasks:
            due_date_str = task.due_date.strftime("%d.%m.%Y %H:%M")
            if task.is_completed:
                status = "✅ Выполнена"
            elif task.due_date < datetime.now():
                status = "❌ Просрочено"
            else:
                status = "⏳ В работе"

            priority = TaskManager.PRIORITIES[task.priority]

            item = self.tasks_list.insert(
                "",
                tk.END,
                values=(
                    task.id,
                    task.title,
                    priority,
                    due_date_str,
                    status
                )
            )

            # Если задача не выполнена и просрочена, подсвечиваем строку тегом
            if not task.is_completed and task.due_date < datetime.now():
                self.tasks_list.item(item, tags=("overdue",))

        # Настройка тегов (например, красный фон для просроченных)
        self.tasks_list.tag_configure("overdue", background="#F8D7DA")
