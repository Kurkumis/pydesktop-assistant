import sqlite3
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    priority: str
    due_date: datetime
    is_completed: bool = False


class TaskManager:
    """Менеджер задач с использованием SQLite"""

    PRIORITIES = {"high": "🔥 Высокий", "medium": "⚠️ Средний", "low": "✅ Низкий"}

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE
                )
            """)

    def _get_available_id(self) -> int:
        """Находит минимальный доступный ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Получаем все существующие ID
            cursor.execute("SELECT id FROM tasks ORDER BY id")
            existing_ids = {row[0] for row in cursor.fetchall()}

            # Ищем первую "дыру" в последовательности
            expected_id = 1
            while True:
                if expected_id not in existing_ids:
                    return expected_id
                expected_id += 1

    def toggle_task_status(self, task_id: int):
        """Изменяет статус выполнения задачи."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET is_completed = NOT is_completed WHERE id = ?",
                (task_id,)
            )

    def create_task(self, title: str, priority: str, due_date: datetime) -> Task:
        """Создание задачи с минимальным доступным ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            task_id = self._get_available_id()

            cursor.execute(
                """
                INSERT INTO tasks (id, title, priority, due_date) 
                VALUES (?, ?, ?, ?)
                """,
                (task_id, title, priority, due_date.isoformat())
            )
            return Task(
                id=task_id,
                title=title,
                priority=priority,
                due_date=due_date
            )

    def delete_task(self, task_id: int):
        """Удаление задачи по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def get_all_tasks(self) -> list[Task]:
        """Получение всех задач"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, priority, due_date, is_completed FROM tasks")
            return [
                Task(
                    id=row[0],
                    title=row[1],
                    priority=row[2],
                    due_date=datetime.fromisoformat(row[3]),
                    is_completed=bool(row[4])
                ) for row in cursor.fetchall()
            ]
