import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from .task_manager import TaskManager, Task


class TaskManagerGUI(tk.Toplevel):
    """Окно управления задачами"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Менеджер задач")
        self.geometry("800x500")
        self.task_manager = TaskManager()
        self._create_widgets()
        self._refresh_tasks_list()

    def _create_widgets(self):
        """Создание элементов интерфейса"""
        # Фрейм для ввода
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        # Поля ввода
        ttk.Label(input_frame, text="Задача:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Приоритет:").grid(row=1, column=0, sticky=tk.W)
        self.priority_var = tk.StringVar()
        self.priority_combobox = ttk.Combobox(
            input_frame,
            textvariable=self.priority_var,
            values=list(TaskManager.PRIORITIES.values()),
            state="readonly"
        )
        self.priority_combobox.grid(row=1, column=1, padx=5)
        self.priority_combobox.current(1)

        ttk.Label(input_frame, text="Срок выполнения:").grid(row=2, column=0, sticky=tk.W)
        self.due_date_entry = DateEntry(input_frame)
        self.due_date_entry.grid(row=2, column=1, padx=5, sticky=tk.W)

        self.time_var = tk.StringVar(value="12:00")
        self.time_entry = ttk.Entry(input_frame, textvariable=self.time_var, width=8)
        self.time_entry.grid(row=2, column=1, padx=5, sticky=tk.E)

        ttk.Button(
            input_frame,
            text="Добавить задачу",
            command=self._add_task
        ).grid(row=3, column=1, pady=5, sticky=tk.E)

        # Список задач
        columns = ("id", "title", "priority", "due_date", "status")
        self.tasks_list = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tasks_list.heading("id", text="ID")
        self.tasks_list.heading("title", text="Задача")
        self.tasks_list.heading("priority", text="Приоритет")
        self.tasks_list.heading("due_date", text="Срок")
        self.tasks_list.heading("status", text="Статус")

        self.tasks_list.column("id", width=50, anchor=tk.CENTER)
        self.tasks_list.column("title", width=200)
        self.tasks_list.column("priority", width=120)
        self.tasks_list.column("due_date", width=150)
        self.tasks_list.column("status", width=100)

        self.tasks_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопки управления
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Удалить задачу",
            command=self._delete_task
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Пометить выполненной",
            command=self._toggle_status
        ).pack(side=tk.LEFT, padx=5)

    def _parse_datetime(self) -> datetime:
        """Парсит дату и время из полей ввода"""
        date = self.due_date_entry.get_date()
        time_str = self.time_var.get()
        return datetime.combine(date, datetime.strptime(time_str, "%H:%M").time())

    def _add_task(self):
        """Добавление новой задачи"""
        title = self.title_entry.get().strip()
        priority_key = next(
            k for k, v in TaskManager.PRIORITIES.items()
            if v == self.priority_var.get()
        )

        if not title:
            messagebox.showerror("Ошибка", "Введите название задачи!")
            return

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

        task_id = self.tasks_list.item(selected[0], "values")[0]
        self.task_manager.delete_task(task_id)
        self._refresh_tasks_list()

    def _toggle_status(self):
        selected = self.tasks_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите задачу!")
            return

        task_id = self.tasks_list.item(selected[0], "values")[0]
        self.task_manager.toggle_task_status(int(task_id))
        self._refresh_tasks_list()

    def _refresh_tasks_list(self):
        """Обновление списка задач"""
        for item in self.tasks_list.get_children():
            self.tasks_list.delete(item)

        # Сортируем задачи по ID перед отображением
        tasks = sorted(
            self.task_manager.get_all_tasks(),
            key=lambda x: x.id
        )

        for task in tasks:
            due_date = task.due_date.strftime("%d.%m.%Y %H:%M")
            if task.is_completed:
                status = "✅ Выполнена"
            elif task.due_date < datetime.now():
                status = "❌ Просрочено"
            else:
                status = "⏳ В работе"
            priority = TaskManager.PRIORITIES[task.priority]

            item = self.tasks_list.insert("", tk.END, values=(
                task.id,
                task.title,
                priority,
                due_date,
                status
            ))

            # Динамическая проверка просрочки
            if not task.is_completed and task.due_date < datetime.now():
                self.tasks_list.item(item, tags=("overdue",))
