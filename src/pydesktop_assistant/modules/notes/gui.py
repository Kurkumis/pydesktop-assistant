import tkinter as tk
from tkinter import ttk, messagebox
from .notes import NoteManager


class NotesGUI(tk.Toplevel):
    """Окно управления заметками"""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Заметки")
        self.geometry("600x400")
        self.note_manager = NoteManager()
        self._create_widgets()
        self._refresh_notes_list()

    def _create_widgets(self):
        """Создание элементов интерфейса"""
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(input_frame, text="Заголовок:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W)
        self.content_entry = ttk.Entry(input_frame, width=40)
        self.content_entry.grid(row=1, column=1, padx=5)

        ttk.Button(
            input_frame,
            text="Добавить",
            command=self._add_note
        ).grid(row=2, column=1, pady=5, sticky=tk.E)

        # Список заметок
        self.notes_list = ttk.Treeview(
            self,
            columns=("id", "title", "content"),
            show="headings"
        )
        self.notes_list.heading("id", text="ID")
        self.notes_list.heading("title", text="Заголовок")
        self.notes_list.heading("content", text="Описание")
        self.notes_list.column("id", width=50, anchor=tk.CENTER)
        self.notes_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопка удаления
        ttk.Button(
            self,
            text="Удалить выбранную",
            command=self._delete_note
        ).pack(pady=10)

    def _refresh_notes_list(self):
        """Обновление списка заметок"""
        for item in self.notes_list.get_children():
            self.notes_list.delete(item)

        for note in self.note_manager.get_all_notes():
            self.notes_list.insert("", tk.END, values=(note.id, note.title, note.content))

    def _add_note(self):
        """Добавление новой заметки"""
        title = self.title_entry.get().strip()
        content = self.content_entry.get().strip()

        if not title or not content:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        self.note_manager.create_note(title, content)
        self.title_entry.delete(0, tk.END)
        self.content_entry.delete(0, tk.END)
        self._refresh_notes_list()

    def _delete_note(self):
        """Удаление выбранной заметки"""
        selected = self.notes_list.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите заметку для удаления!")
            return

        note_id = self.notes_list.item(selected[0], "values")[0]
        self.note_manager.delete_note(note_id)
        self._refresh_notes_list()
