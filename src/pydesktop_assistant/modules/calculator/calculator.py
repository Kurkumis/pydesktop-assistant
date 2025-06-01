class Calculator:
    """Класс калькулятора"""

    def __init__(self):
        self.error_message = None
        self.operations = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else self._handle_error("Деление на ноль"),
            '^': lambda a, b: a ** b,
            '**': lambda a, b: a ** b
        }

    def calculate(self, expression: str) -> float:
        """Вычисляет математическое выражение"""
        self.error_message = None
        try:
            a, op, b = self._parse_expression(expression)
            operation = self.operations.get(op)

            if not operation:
                return self._handle_error(f"Неподдерживаемый оператор: {op}")

            return operation(a, b)
        except ValueError as e:
            return self._handle_error(str(e))
        except Exception as e:
            return self._handle_error(f"Ошибка вычисления: {str(e)}")

    def _parse_expression(self, expr: str) -> tuple[float, str, float]:
        """Парсит выражение на операнды и оператор"""
        expr = expr.strip().replace(' ', '')

        # Список поддерживаемых операторов в порядке приоритета распознавания
        operators = ['**', '^', '*', '/', '+', '-']

        for op in operators:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    return float(parts[0]), op, float(parts[1])

        raise ValueError("Не удалось распознать выражение")

    def _handle_error(self, message: str) -> float:
        """Обработка ошибок с сохранением сообщения"""
        self.error_message = message
        return float('nan')  # Возвращаем NaN при ошибке
