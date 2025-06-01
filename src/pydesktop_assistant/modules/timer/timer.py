import threading
import time
from plyer import notification


class TimerManager:
    """Менеджер таймеров с уведомлениями"""

    def __init__(self):
        self.timers = {}  # Словарь активных таймеров: id -> threading.Timer
        self.next_id = 1  # Счетчик для ID таймеров

    def start_timer(self, seconds: int, message: str) -> int:
        """Запускает новый таймер, возвращает ID таймера"""
        timer_id = self.next_id
        self.next_id += 1

        # Создаем и запускаем таймер
        timer = threading.Timer(seconds, self._timer_completed, args=[timer_id, message])
        timer.start()

        self.timers[timer_id] = {
            "timer": timer,
            "message": message,
            "end_time": time.time() + seconds
        }

        return timer_id

    def cancel_timer(self, timer_id: int):
        """Отменяет таймер по ID"""
        if timer_id in self.timers:
            self.timers[timer_id]["timer"].cancel()
            del self.timers[timer_id]

    def _timer_completed(self, timer_id: int, message: str):
        """Обработчик завершения таймера"""
        # Показать уведомление
        self._show_notification("Таймер завершен!", message)

        # Удалить таймер из словаря
        if timer_id in self.timers:
            del self.timers[timer_id]

    def _show_notification(self, title: str, message: str):
        """Показывает системное уведомление"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="PyDesktop Assistant",
                timeout=10  # Уведомление видно 10 секунд
            )
        except:
            # Fallback для систем без поддержки уведомлений
            print(f"Уведомление: {title} - {message}")

    def get_active_timers(self) -> list:
        """Возвращает список активных таймеров"""
        return [
            {
                "id": tid,
                "message": data["message"],
                "remaining": max(0, int(data["end_time"] - time.time()))
            }
            for tid, data in self.timers.items()
        ]
