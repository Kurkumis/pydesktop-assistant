import os
import sqlite3
from datetime import datetime, timedelta
import pytest
from src.pydesktop_assistant.modules.calendar.calendar import CalendarManager


@pytest.fixture(scope="module")
def db_path():
    path = "test_calendar.db"
    if os.path.exists(path):
        os.remove(path)
    yield path


def test_add_event(db_path):
    """Тест добавления события"""
    manager = CalendarManager(db_path)

    event_datetime = datetime.now() + timedelta(days=1)
    event = manager.add_event("Test Event", "Description", event_datetime)

    assert event.id == 1
    assert event.title == "Test Event"
    assert event.description == "Description"
    assert event.event_datetime == event_datetime
    assert not event.notified

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
    """Тест удаления события"""
    manager = CalendarManager(db_path)

    event_datetime = datetime.now() + timedelta(days=1)
    event = manager.add_event("Test Event", "Description", event_datetime)

    manager.delete_event(event.id)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = 1")
        row = cursor.fetchone()
        assert row is None


def test_get_all_events(db_path):
    """Тест получения всех событий"""
    manager = CalendarManager(db_path)

    now = datetime.now()
    event1 = manager.add_event("Event 1", "Desc 1", now + timedelta(days=2))
    event2 = manager.add_event("Event 2", "Desc 2", now + timedelta(days=1))
    event3 = manager.add_event("Event 3", "Desc 3", now + timedelta(days=3))

    events = manager.get_all_events()

    assert len(events) == 3
    assert events[0].id == event2.id
    assert events[1].id == event1.id
    assert events[2].id == event3.id

    manager.delete_event(event1.id)
    manager.delete_event(event2.id)
    manager.delete_event(event3.id)


def test_unique_ids(db_path):
    """Тест проверки уникальных id событий"""
    manager = CalendarManager(db_path)

    event1 = manager.add_event("Event 1", "Desc 1", datetime.now())
    event2 = manager.add_event("Event 2", "Desc 2", datetime.now())

    assert event1.id == 1
    assert event2.id == 2

    manager.delete_event(event1.id)

    event3 = manager.add_event("Event 3", "Desc 3", datetime.now())
    assert event3.id == 1

    manager.delete_event(event2.id)
    manager.delete_event(event3.id)
