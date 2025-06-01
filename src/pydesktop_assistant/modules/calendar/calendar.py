import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from plyer import notification


@dataclass
class CalendarEvent:
    id: int
    title: str
    description: str
    event_datetime: datetime
    notified: bool = False


class CalendarManager:
    """Менеджер календарных событий с уведомлениями"""

    def __init__(self, db_path: str = "calendar.db"):
        self.db_path = Path(db_path)
        self.events = []
        self._init_db()
        self._load_events()
        self._start_notification_thread()

    def _init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    event_datetime TEXT NOT NULL,
                    notified BOOLEAN DEFAULT FALSE
                )
            """)

    def _load_events(self):
        """Загрузка событий из базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, event_datetime, notified FROM events")
            self.events = [
                CalendarEvent(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    event_datetime=datetime.fromisoformat(row[3]),
                    notified=bool(row[4])
                ) for row in cursor.fetchall()
            ]

    def add_event(self, title: str, description: str, event_datetime: datetime) -> CalendarEvent:
        """Добавление нового события"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Поиск минимального доступного ID
            cursor.execute("SELECT id FROM events ORDER BY id")
            existing_ids = {row[0] for row in cursor.fetchall()}
            event_id = 1
            while event_id in existing_ids:
                event_id += 1

            cursor.execute(
                """
                INSERT INTO events (id, title, description, event_datetime)
                VALUES (?, ?, ?, ?)
                """,
                (event_id, title, description, event_datetime.isoformat())
            )

            event = CalendarEvent(
                id=event_id,
                title=title,
                description=description,
                event_datetime=event_datetime
            )
            self.events.append(event)
            return event

    def delete_event(self, event_id: int):
        """Удаление события по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))

        # Удаление из кеша
        self.events = [e for e in self.events if e.id != event_id]

    def get_all_events(self) -> list[CalendarEvent]:
        """Получение всех событий, отсортированных по дате"""
        return sorted(self.events, key=lambda e: e.event_datetime)

    def _start_notification_thread(self):
        """Запуск фонового потока для проверки событий"""
        self.running = True
        self.thread = threading.Thread(target=self._check_events, daemon=True)
        self.thread.start()

    def stop_notifications(self):
        """Остановка фонового потока"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _check_events(self):
        """Проверка событий и отправка уведомлений"""
        while self.running:
            now = datetime.now()

            for event in self.events:
                if not event.notified and event.event_datetime <= now:
                    self._send_notification(event)
                    event.notified = True
                    self._mark_as_notified(event.id)

            time.sleep(30)  # Проверка каждые 30 секунд

    def _send_notification(self, event: CalendarEvent):
        """Отправка системного уведомления"""
        try:
            notification.notify(
                title=f"Событие: {event.title}",
                message=event.description,
                app_name="PyDesktop Assistant",
                timeout=10
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")

    def _mark_as_notified(self, event_id: int):
        """Помечает событие как уведомлённое в БД"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE events SET notified = TRUE WHERE id = ?",
                (event_id,)
            )
