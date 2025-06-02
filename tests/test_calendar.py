import os
import sqlite3
from datetime import datetime, timedelta
import pytest
from src.pydesktop_assistant.modules.calendar.calendar import CalendarManager


@pytest.fixture(scope="module")
def db_path():
    path = "test_calendar.db"
    # Удаляем файл, если он существует, перед началом тестов
    if os.path.exists(path):
        os.remove(path)
    yield path


def test_add_event(db_path):
    manager = CalendarManager(db_path)

    # Добавляем событие
    event_datetime = datetime.now() + timedelta(days=1)
    event = manager.add_event("Test Event", "Description", event_datetime)

    assert event.id == 1
    assert event.title == "Test Event"
    assert event.description == "Description"
    assert event.event_datetime == event_datetime
    assert not event.notified

    # Проверяем, что событие добавлено в базу
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = 1")
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Test Event"
        assert row[2] == "Description"
        assert row[3] == event_datetime.isoformat()
        assert row[4] == 0  # notified = False

    manager.delete_event(event.id)


def test_delete_event(db_path):
    manager = CalendarManager(db_path)

    # Добавляем событие
    event_datetime = datetime.now() + timedelta(days=1)
    event = manager.add_event("Test Event", "Description", event_datetime)

    # Удаляем событие
    manager.delete_event(event.id)

    # Проверяем, что событие удалено
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = 1")
        row = cursor.fetchone()
        assert row is None


def test_get_all_events(db_path):
    manager = CalendarManager(db_path)

    # Добавляем несколько событий
    now = datetime.now()
    event1 = manager.add_event("Event 1", "Desc 1", now + timedelta(days=2))
    event2 = manager.add_event("Event 2", "Desc 2", now + timedelta(days=1))
    event3 = manager.add_event("Event 3", "Desc 3", now + timedelta(days=3))

    # Получаем все события
    events = manager.get_all_events()

    # Проверяем, что события отсортированы по дате
    assert len(events) == 3
    assert events[0].id == event2.id  # Самое раннее
    assert events[1].id == event1.id
    assert events[2].id == event3.id

    manager.delete_event(event1.id)
    manager.delete_event(event2.id)
    manager.delete_event(event3.id)


def test_unique_ids(db_path):
    manager = CalendarManager(db_path)

    # Добавляем события
    event1 = manager.add_event("Event 1", "Desc 1", datetime.now())
    event2 = manager.add_event("Event 2", "Desc 2", datetime.now())

    assert event1.id == 1
    assert event2.id == 2

    # Удаляем событие 1
    manager.delete_event(event1.id)

    # Добавляем новое событие, ID должен быть 1 (минимальный доступный)
    event3 = manager.add_event("Event 3", "Desc 3", datetime.now())
    assert event3.id == 1

    manager.delete_event(event2.id)
    manager.delete_event(event3.id)
