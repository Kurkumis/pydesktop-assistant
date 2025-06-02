import threading
import time
import pytest
from unittest.mock import patch, MagicMock
from src.pydesktop_assistant.modules.timer.timer import TimerManager


@pytest.fixture
def timer_manager():
    """Фикстура для создания экземпляра TimerManager"""
    return TimerManager()


def test_start_timer(timer_manager):
    """Тест запуска таймера"""
    timer_id = timer_manager.start_timer(5, "Test message")

    assert timer_id in timer_manager.timers
    assert timer_manager.timers[timer_id]["message"] == "Test message"
    assert isinstance(timer_manager.timers[timer_id]["timer"], threading.Timer)

    expected_end = time.time() + 5
    assert abs(timer_manager.timers[timer_id]["end_time"] - expected_end) < 0.1


def test_cancel_timer(timer_manager):
    """Тест отмены таймера"""
    timer_id = timer_manager.start_timer(10, "To cancel")
    timer_manager.cancel_timer(timer_id)

    assert timer_id not in timer_manager.timers


@patch('plyer.notification.notify')
def test_timer_completion(mock_notify, timer_manager):
    """Тест завершения таймера и отправки уведомления"""
    with patch('threading.Timer') as mock_timer:
        mock_timer_instance = MagicMock()
        mock_timer.return_value = mock_timer_instance

        timer_id = timer_manager.start_timer(1, "Test completion")

        timer_manager._timer_completed(timer_id, "Test completion")

    mock_notify.assert_called_once_with(
        title="Таймер завершен!",
        message="Test completion",
        app_name="PyDesktop Assistant",
        timeout=10
    )

    assert timer_id not in timer_manager.timers


def test_get_active_timers(timer_manager):
    """Тест получения списка активных таймеров"""
    timer1 = timer_manager.start_timer(10, "Timer 1")
    timer2 = timer_manager.start_timer(20, "Timer 2")

    active_timers = timer_manager.get_active_timers()

    assert len(active_timers) == 2

    timers_by_id = {t["id"]: t for t in active_timers}

    assert timers_by_id[timer1]["message"] == "Timer 1"
    assert 9 <= timers_by_id[timer1]["remaining"] <= 10

    assert timers_by_id[timer2]["message"] == "Timer 2"
    assert 19 <= timers_by_id[timer2]["remaining"] <= 20


def test_id_increment(timer_manager):
    """Тест последовательного увеличения ID"""
    id1 = timer_manager.start_timer(1, "First")
    id2 = timer_manager.start_timer(1, "Second")
    id3 = timer_manager.start_timer(1, "Third")

    assert id1 == 1
    assert id2 == 2
    assert id3 == 3


@patch('plyer.notification.notify', side_effect=Exception("Notification error"))
def test_notification_fallback(mock_notify, capsys, timer_manager):
    """Тест fallback при ошибке уведомления"""
    timer_manager._timer_completed(1, "Test error")

    captured = capsys.readouterr()
    assert "Уведомление: Таймер завершен! - Test error" in captured.out


def test_cancel_nonexistent_timer(timer_manager):
    """Тест отмены несуществующего таймера"""
    timer_manager.cancel_timer(999)

    assert len(timer_manager.timers) == 0


def test_multiple_timers(timer_manager):
    """Тест работы с несколькими таймерами одновременно"""
    ids = []
    for i in range(3):
        ids.append(timer_manager.start_timer(10 + i, f"Timer {i}"))

    assert len(timer_manager.timers) == 3

    timer_manager.cancel_timer(ids[1])
    assert len(timer_manager.timers) == 2
    assert ids[1] not in timer_manager.timers

    active_timers = timer_manager.get_active_timers()
    active_ids = [t["id"] for t in active_timers]
    assert ids[0] in active_ids
    assert ids[2] in active_ids
    assert ids[1] not in active_ids


def test_remaining_time_calculation(timer_manager):
    """Тест точности расчета оставшегося времени"""
    timer_id = timer_manager.start_timer(10, "Precision test")

    time.sleep(1.5)

    active_timers = timer_manager.get_active_timers()
    timer_info = next(t for t in active_timers if t["id"] == timer_id)

    assert 8 <= timer_info["remaining"] <= 9
