import tkinter as tk
from tkinter import ttk, messagebox
from .notes import NoteManager


class NotesGUI(tk.Toplevel):
    """Окно управления заметками"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Заметки")
        self.geometry("650x450")
        self.minsize(600, 400)

        # Инициализируем менеджер заметок
        self.note_manager = NoteManager()

        # Настраиваем стили
        self._setup_style()

        # Создаём и размещаем виджеты
        self._create_widgets()

        # Заполняем таблицу текущими заметками
        self._refresh_notes_list()

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

        # Стиль для меток
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

        # Для адаптивности: контейнер растягивается при изменении размера окна
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)  # область с таблицей растягивается
        container.columnconfigure(0, weight=1)

        # ---- Заголовок окна ----
        header = ttk.Label(
            container,
            text="Менеджер заметок",
            font=("Segoe UI", 16, "bold"),
            foreground="#2E4053"
        )
        header.grid(row=0, column=0, pady=(0, 15))

        # ---- Верхняя часть: Форма ввода новой заметки ----
        form_frame = ttk.LabelFrame(container, text="Добавить новую заметку")
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        form_frame.columnconfigure(1, weight=1)

        # Метка и поле "Заголовок"
        ttk.Label(form_frame, text="Заголовок:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Метка и поле "Описание"
        ttk.Label(form_frame, text="Описание:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.content_entry = ttk.Entry(form_frame)
        self.content_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Кнопка добавления заметки
        add_btn = ttk.Button(
            form_frame,
            text="Добавить",
            command=self._add_note
        )
        add_btn.grid(row=2, column=1, sticky="e", padx=5, pady=(10, 5))

        # ---- Нижняя часть: Список заметок ----
        notes_frame = ttk.LabelFrame(container, text="Список заметок")
        notes_frame.grid(row=2, column=0, sticky="nsew")
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(0, weight=1)

        columns = ("id", "title", "content")
        self.notes_list = ttk.Treeview(
            notes_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=12
        )

        # Заголовки и настройки колонок
        self.notes_list.heading("id", text="ID")
        self.notes_list.heading("title", text="Заголовок")
        self.notes_list.heading("content", text="Описание")

        self.notes_list.column("id", width=50, anchor="center")
        self.notes_list.column("title", width=200)
        self.notes_list.column("content", width=330)

        # Вертикальный скроллбар
        scroll_y = ttk.Scrollbar(
            notes_frame, orient="vertical", command=self.notes_list.yview
        )
        self.notes_list.configure(yscrollcommand=scroll_y.set)

        self.notes_list.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        # ---- Кнопка удаления заметки ----
        delete_btn = ttk.Button(
            container,
            text="Удалить выбранную заметку",
            command=self._delete_note
        )
        delete_btn.grid(row=3, column=0, sticky="e", padx=5, pady=(10, 0))

    def _refresh_notes_list(self):
        """Обновление списка заметок в таблице"""
        # Удаляем все элементы из Treeview
        for item in self.notes_list.get_children():
            self.notes_list.delete(item)

        # Заполняем новыми данными
        for note in self.note_manager.get_all_notes():
            self.notes_list.insert(
                "",
                tk.END,
                values=(note.id, note.title, note.content)
            )

    def _add_note(self):
        """Обработка добавления новой заметки"""
        title = self.title_entry.get().strip()
        content = self.content_entry.get().strip()

        if not title or not content:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        # Создаём заметку в менеджере
        self.note_manager.create_note(title, content)

        # Очищаем поля ввода
        self.title_entry.delete(0, tk.END)
        self.content_entry.delete(0, tk.END)

        # Обновляем таблицу
        self._refresh_notes_list()

    def _delete_note(self):
        """Обработка удаления выбранной заметки"""
        selected = self.notes_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите заметку для удаления!")
            return

        note_id = self.notes_list.item(selected[0], "values")[0]
        self.note_manager.delete_note(note_id)
        self._refresh_notes_list()
