class Calculator:
    """Калькулятор с обработкой математических выражений"""

    def calculate(self, expression: str) -> float:
        """Вычисляет выражение в формате 'a op b'"""
        try:
            a, op, b = self._parse_expression(expression)
            return self._perform_operation(a, op, b)
        except ValueError as e:
            raise e

    def _parse_expression(self, expr: str) -> tuple[float, str, float]:
        """Парсит выражение на операнды и оператор"""
        expr = expr.replace('^', '**')
        operators = {'+', '-', '*', '/', '**'}

        for op in sorted(operators, key=len, reverse=True):
            if op in expr:
                a, b = expr.split(op, 1)
                return float(a.strip()), op, float(b.strip())

        raise ValueError("Invalid expression")

    def _perform_operation(self, a: float, op: str, b: float) -> float:
        """Выполняет операцию через методы класса"""
        operations = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide,
            '**': self.power
        }

        if op not in operations:
            raise ValueError(f"Unsupported operator: {op}")

        return operations[op](a, b)

    def add(self, a: float, b: float) -> float:
        """Сложение"""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Вычитание"""
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """Умножение"""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """Деление с проверкой на ноль"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def power(self, a: float, b: float) -> float:
        """Возведение в степень"""
        return a ** b
