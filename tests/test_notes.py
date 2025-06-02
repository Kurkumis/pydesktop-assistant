import os
import sqlite3
import pytest
from src.pydesktop_assistant.modules.notes.notes import NoteManager


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    """Фикстура для создания временной базы данных"""
    path = tmp_path_factory.mktemp("data") / "test_notes.db"
    if os.path.exists(path):
        os.remove(path)
    return str(path)


def test_create_note(db_path):
    """Тест создания заметки"""
    manager = NoteManager(db_path)

    note = manager.create_note("Test Note", "This is a test content")

    assert note.id == 1
    assert note.title == "Test Note"
    assert note.content == "This is a test content"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = 1")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 1
        assert row[1] == "Test Note"
        assert row[2] == "This is a test content"
    manager.delete_note(note.id)


def test_delete_note(db_path):
    """Тест удаления заметки"""
    manager = NoteManager(db_path)

    note = manager.create_note("To Delete", "Delete me")
    manager.delete_note(note.id)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note.id,))
        assert cursor.fetchone() is None


def test_get_all_notes(db_path):
    """Тест получения всех заметок"""
    manager = NoteManager(db_path)

    note1 = manager.create_note("Note 1", "Content 1")
    note2 = manager.create_note("Note 2", "Content 2")
    note3 = manager.create_note("Note 3", "Content 3")

    notes = manager.get_all_notes()

    assert len(notes) == 3
    assert {n.id for n in notes} == {note1.id, note2.id, note3.id}
    assert {n.title for n in notes} == {"Note 1", "Note 2", "Note 3"}
    assert {n.content for n in notes} == {"Content 1", "Content 2", "Content 3"}

    manager.delete_note(note1.id)
    manager.delete_note(note2.id)
    manager.delete_note(note3.id)


def test_unique_ids(db_path):
    """Тест проверки уникальных id заметок"""
    manager = NoteManager(db_path)

    note1 = manager.create_note("Temp 1", "Delete me")
    note2 = manager.create_note("Temp 2", "Delete me")

    assert note1.id == 1
    assert note2.id == 2

    manager.delete_note(note1.id)

    note3 = manager.create_note("New 1", "Content")
    assert note3.id == 1

    manager.delete_note(note2.id)
    manager.delete_note(note3.id)
