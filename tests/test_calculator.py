from src.pydesktop_assistant.modules.calculator.calculator import Calculator
import math


def test_addition():
    calc = Calculator()
    result = calc.calculate("2 + 3")
    assert result == 5.0
    assert calc.error_message is None


def test_subtraction():
    calc = Calculator()
    result = calc.calculate("5 - 2")
    assert result == 3.0
    assert calc.error_message is None


def test_multiplication():
    calc = Calculator()
    result = calc.calculate("4 * 2")
    assert result == 8.0
    assert calc.error_message is None


def test_division():
    calc = Calculator()
    result = calc.calculate("10 / 2")
    assert result == 5.0
    assert calc.error_message is None


def test_exponentiation():
    calc = Calculator()
    result = calc.calculate("2 ^ 3")
    assert result == 8.0
    assert calc.error_message is None

    result = calc.calculate("2 ** 3")
    assert result == 8.0
    assert calc.error_message is None


def test_division_by_zero():
    calc = Calculator()
    result = calc.calculate("10 / 0")
    assert math.isnan(result)
    assert calc.error_message == "Деление на ноль"


def test_expression_with_spaces():
    calc = Calculator()
    result = calc.calculate(" 2   +   3 ")
    assert result == 5.0


def test_negative_numbers():
    calc = Calculator()
    result = calc.calculate("-2 + 3")
    assert result == 1.0
    result = calc.calculate("2 + -3")
    assert result == -1.0


def test_floating_point_numbers():
    calc = Calculator()
    result = calc.calculate("2.5 * 2")
    assert result == 5.0
    result = calc.calculate("10 / 3")
    assert abs(result - 3.3333333333333335) < 1e-10
