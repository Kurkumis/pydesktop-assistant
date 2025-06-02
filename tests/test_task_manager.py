import os
import sqlite3
import pytest
from datetime import datetime, timedelta
from src.pydesktop_assistant.modules.task_manager.task_manager import TaskManager, Task


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    """Фикстура для создания временной базы данных"""
    path = tmp_path_factory.mktemp("data") / "test_tasks.db"
    if os.path.exists(path):
        os.remove(path)
    return str(path)


@pytest.fixture
def sample_task():
    """Фикстура для создания тестовой задачи"""
    return Task(
        id=1,
        title="Test Task",
        priority="high",
        due_date=datetime.now() + timedelta(days=1),
        is_completed=False
    )


def test_create_task(db_path, sample_task):
    """Тест создания задачи"""
    manager = TaskManager(db_path)

    task = manager.create_task(
        sample_task.title,
        sample_task.priority,
        sample_task.due_date
    )

    assert task.id == 1
    assert task.title == sample_task.title
    assert task.priority == sample_task.priority
    assert task.due_date == sample_task.due_date
    assert not task.is_completed

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = 1")
        row = cursor.fetchone()

        assert row is not None
        assert row[0] == 1
        assert row[1] == sample_task.title
        assert row[2] == sample_task.priority
        assert row[3] == sample_task.due_date.isoformat()
        assert row[4] == 0

    manager.delete_task(task.id)


def test_delete_task(db_path, sample_task):
    """Тест удаления задачи"""
    manager = TaskManager(db_path)

    task = manager.create_task(
        sample_task.title,
        sample_task.priority,
        sample_task.due_date
    )

    manager.delete_task(task.id)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task.id,))
        assert cursor.fetchone() is None


def test_get_all_tasks(db_path):
    """Тест получения всех задач"""
    manager = TaskManager(db_path)

    now = datetime.now()
    task1 = manager.create_task("Task 1", "medium", now + timedelta(days=3))
    task2 = manager.create_task("Task 2", "high", now + timedelta(days=1))
    task3 = manager.create_task("Task 3", "low", now + timedelta(days=2))

    tasks = manager.get_all_tasks()

    assert len(tasks) == 3
    assert {t.id for t in tasks} == {task1.id, task2.id, task3.id}
    assert {t.title for t in tasks} == {"Task 1", "Task 2", "Task 3"}
    assert {t.priority for t in tasks} == {"medium", "high", "low"}

    manager.delete_task(task1.id)
    manager.delete_task(task2.id)
    manager.delete_task(task3.id)


def test_toggle_task_status(db_path, sample_task):
    """Тест изменения статуса задачи"""
    manager = TaskManager(db_path)

    task = manager.create_task(
        sample_task.title,
        sample_task.priority,
        sample_task.due_date
    )

    assert not task.is_completed

    manager.toggle_task_status(task.id)

    tasks = manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].is_completed

    manager.toggle_task_status(task.id)

    tasks = manager.get_all_tasks()
    assert not tasks[0].is_completed

    manager.delete_task(task.id)


def test_unique_ids(db_path):
    """Тест проверки уникальных id задач"""
    manager = TaskManager(db_path)

    task1 = manager.create_task("Task 1", "high", datetime.now())
    task2 = manager.create_task("Task 2", "medium", datetime.now())

    assert task1.id == 1
    assert task2.id == 2

    manager.delete_task(task1.id)

    task3 = manager.create_task("New Task 2", "high", datetime.now())

    assert task3.id == 1

    manager.delete_task(task2.id)
    manager.delete_task(task3.id)


def test_priority_mapping(db_path):
    """Тест корректности приоритетов"""
    manager = TaskManager(db_path)

    high_task = manager.create_task("High", "high", datetime.now())
    medium_task = manager.create_task("Medium", "medium", datetime.now())
    low_task = manager.create_task("Low", "low", datetime.now())

    assert high_task.priority == "high"
    assert medium_task.priority == "medium"
    assert low_task.priority == "low"

    assert manager.PRIORITIES["high"] == "🔥 Высокий"
    assert manager.PRIORITIES["medium"] == "⚠️ Средний"
    assert manager.PRIORITIES["low"] == "✅ Низкий"

    manager.delete_task(high_task.id)
    manager.delete_task(medium_task.id)
    manager.delete_task(low_task.id)


def test_datetime_handling(db_path):
    """Тест обработки даты и времени"""
    manager = TaskManager(db_path)

    test_datetime = datetime(2023, 12, 31, 23, 59)
    task = manager.create_task("New Year", "high", test_datetime)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT due_date FROM tasks WHERE id = ?", (task.id,))
        db_datetime_str = cursor.fetchone()[0]
        db_datetime = datetime.fromisoformat(db_datetime_str)
        assert db_datetime == test_datetime

    tasks = manager.get_all_tasks()
    assert len(tasks) == 1
    assert tasks[0].due_date == test_datetime

    manager.delete_task(task.id)


def test_task_persistence(db_path, sample_task):
    """Тест сохранения задач между сессиями"""
    # Первый экземпляр менеджера
    manager1 = TaskManager(db_path)
    task = manager1.create_task(
        sample_task.title,
        sample_task.priority,
        sample_task.due_date
    )

    # Второй экземпляр менеджера (имитация перезапуска)
    manager2 = TaskManager(db_path)
    tasks = manager2.get_all_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == task.id
    assert tasks[0].title == task.title
    assert tasks[0].priority == task.priority
    assert tasks[0].due_date == task.due_date
    assert tasks[0].is_completed == task.is_completed

    manager2.delete_task(task.id)


def test_completed_status_persistence(db_path):
    """Тест сохранения статуса выполнения между сессиями"""
    manager1 = TaskManager(db_path)
    task = manager1.create_task("Complete me", "medium", datetime.now())

    # Меняем статус
    manager1.toggle_task_status(task.id)

    # Второй экземпляр менеджера
    manager2 = TaskManager(db_path)
    tasks = manager2.get_all_tasks()

    assert tasks[0].is_completed

    manager2.delete_task(task.id)
