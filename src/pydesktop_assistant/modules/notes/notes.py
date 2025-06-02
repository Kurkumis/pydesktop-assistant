import sqlite3
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Note:
    id: int
    title: str
    content: str


class NoteManager:
    """Менеджер заметок с использованием SQLite"""

    def __init__(self, db_path: str = "notes.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)

    def create_note(self, title: str, content: str) -> Note:
        """Создание заметки с минимальным доступным ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            note_id = self._get_available_id()

            cursor.execute(
                "INSERT INTO notes (id, title, content) VALUES (?, ?, ?)",
                (note_id, title, content)
            )
            return Note(id=note_id, title=title, content=content)

    def delete_note(self, note_id: int):
        """Удаление заметки по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    def get_all_notes(self) -> list[Note]:
        """Получение всех заметок"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM notes")
            return [Note(*row) for row in cursor.fetchall()]

    def _get_available_id(self) -> int:
        """Находит минимальный доступный ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Получаем все существующие ID
            cursor.execute("SELECT id FROM notes ORDER BY id")
            existing_ids = [row[0] for row in cursor.fetchall()]

            # Ищем первую "дыру" в последовательности
            expected_id = 1
            for id in existing_ids:
                if id > expected_id:
                    return expected_id
                expected_id = id + 1
            return expected_id
