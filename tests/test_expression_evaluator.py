"""
Comprehensive tests for the advanced expression evaluator.
"""

import pytest
from engine.expression_evaluator import (
    evaluate_expression,
    validate_expression,
    ExpressionError,
    ExpressionParser,
    ExpressionEvaluator
)

class TestExpressionEvaluator:
    """Test suite for expression evaluation."""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        state = {}

        assert evaluate_expression("5 + 3", state) == 8
        assert evaluate_expression("10 - 4", state) == 6
        assert evaluate_expression("6 * 7", state) == 42
        assert evaluate_expression("15 / 3", state) == 5.0
        assert evaluate_expression("17 % 5", state) == 2

    def test_comparison_operators(self):
        """Test comparison operations."""
        state = {}

        assert evaluate_expression("5 > 3", state) == True
        assert evaluate_expression("3 > 5", state) == False
        assert evaluate_expression("5 >= 5", state) == True
        assert evaluate_expression("5 < 3", state) == False
        assert evaluate_expression("3 <= 5", state) == True
        assert evaluate_expression("5 == 5", state) == True
        assert evaluate_expression("5 != 3", state) == True

    def test_logical_operators(self):
        """Test logical operations."""
        state = {}

        assert evaluate_expression("true && true", state) == True
        assert evaluate_expression("true && false", state) == False
        assert evaluate_expression("false || true", state) == True
        assert evaluate_expression("false || false", state) == False
        assert evaluate_expression("not true", state) == False
        assert evaluate_expression("not false", state) == True

    def test_complex_expressions(self):
        """Test complex expressions with multiple operators."""
        state = {"score": 85, "attempts": 2}

        # Test the example from requirements
        assert evaluate_expression("{{score}} > 80 && {{attempts}} < 3", state) == True
        assert evaluate_expression("{{score}} > 90 && {{attempts}} < 3", state) == False

    def test_membership_operators(self):
        """Test membership operations."""
        state = {"user": {"role": "admin"}, "tags": ["urgent", "important"]}

        assert evaluate_expression("{{user.role}} in ['admin', 'editor']", state) == True
        assert evaluate_expression("{{user.role}} in ['user', 'guest']", state) == False
        assert evaluate_expression("'urgent' in {{tags}}", state) == True
        assert evaluate_expression("'low' in {{tags}}", state) == False
        assert evaluate_expression("'normal' not in {{tags}}", state) == True

    def test_string_operations(self):
        """Test string operation functions."""
        state = {"title": "Hello World", "content": "This is a test"}

        assert evaluate_expression("contains({{title}}, 'World')", state) == True
        assert evaluate_expression("contains({{title}}, 'Universe')", state) == False
        assert evaluate_expression("startsWith({{title}}, 'Hello')", state) == True
        assert evaluate_expression("startsWith({{title}}, 'World')", state) == False
        assert evaluate_expression("endsWith({{content}}, 'test')", state) == True
        assert evaluate_expression("endsWith({{content}}, 'example')", state) == False

    def test_type_checking_functions(self):
        """Test type checking functions."""
        state = {
            "name": "John",
            "age": 30,
            "active": True,
            "profile": {"city": "NYC"},
            "tags": ["a", "b", "c"]
        }

        assert evaluate_expression("isString({{name}})", state) == True
        assert evaluate_expression("isString({{age}})", state) == False
        assert evaluate_expression("isNumber({{age}})", state) == True
        assert evaluate_expression("isNumber({{name}})", state) == False
        assert evaluate_expression("isObject({{profile}})", state) == True
        assert evaluate_expression("isObject({{name}})", state) == False
        assert evaluate_expression("isArray({{tags}})", state) == True
        assert evaluate_expression("isArray({{name}})", state) == False

    def test_variable_resolution(self):
        """Test variable resolution with dot notation."""
        state = {
            "user": {
                "name": "Alice",
                "profile": {
                    "age": 28,
                    "city": "Boston"
                }
            },
            "items": ["apple", "banana", "cherry"],
            "score": 95
        }

        assert evaluate_expression("{{user.name}}", state) == "Alice"
        assert evaluate_expression("{{user.profile.age}}", state) == 28
        assert evaluate_expression("{{user.profile.city}}", state) == "Boston"
        assert evaluate_expression("{{items[0]}}", state) == "apple"
        assert evaluate_expression("{{items[2]}}", state) == "cherry"
        assert evaluate_expression("{{score}}", state) == 95

    def test_function_calls(self):
        """Test various function calls."""
        state = {"text": "  Hello World  ", "items": ["a", "b", "c"]}

        assert evaluate_expression("length({{text}})", state) == 15  # includes spaces
        assert evaluate_expression("length({{items}})", state) == 3
        assert evaluate_expression("upper({{text}})", state) == "  HELLO WORLD  "
        assert evaluate_expression("lower('HELLO')", state) == "hello"
        assert evaluate_expression("trim({{text}})", state) == "Hello World"

    def test_literal_values(self):
        """Test literal values."""
        state = {}

        assert evaluate_expression('"hello world"', state) == "hello world"
        assert evaluate_expression("'single quotes'", state) == "single quotes"
        assert evaluate_expression("42", state) == 42
        assert evaluate_expression("3.14", state) == 3.14
        assert evaluate_expression("true", state) == True
        assert evaluate_expression("false", state) == False

    def test_operator_precedence(self):
        """Test operator precedence."""
        state = {}

        assert evaluate_expression("2 + 3 * 4", state) == 14  # multiplication before addition
        assert evaluate_expression("(2 + 3) * 4", state) == 20  # parentheses override
        assert evaluate_expression("true || false && false", state) == True  # && before ||
        assert evaluate_expression("(true || false) && false", state) == False

    def test_error_handling(self):
        """Test error handling for invalid expressions."""
        state = {}

        # Invalid syntax
        with pytest.raises(ExpressionError):
            evaluate_expression("5 + ", state)

        with pytest.raises(ExpressionError):
            evaluate_expression("invalid syntax +++", state)

        # Undefined variables
        with pytest.raises(ExpressionError):
            evaluate_expression("{{undefined_var}}", state)

        # Invalid function calls
        with pytest.raises(ExpressionError):
            evaluate_expression("unknownFunction(1)", state)

        # Division by zero
        with pytest.raises(ExpressionError):
            evaluate_expression("5 / 0", state)

        # Type errors in operations
        with pytest.raises(ExpressionError):
            evaluate_expression("length(123)", state)  # number doesn't have length

    def test_complex_real_world_examples(self):
        """Test complex real-world expression examples."""
        state = {
            "user": {
                "role": "admin",
                "permissions": ["read", "write", "delete"],
                "login_attempts": 2
            },
            "content": {
                "priority": "high",
                "tags": ["urgent", "review"],
                "word_count": 1500
            },
            "system": {
                "maintenance_mode": False,
                "max_attempts": 3
            }
        }

        # Complex permission check
        expr1 = "{{user.role}} in ['admin', 'editor'] && 'write' in {{user.permissions}}"
        assert evaluate_expression(expr1, state) == True

        # Content filtering
        expr2 = "{{content.priority}} == 'high' || 'urgent' in {{content.tags}}"
        assert evaluate_expression(expr2, state) == True

        # Login attempt check
        expr3 = "{{user.login_attempts}} < {{system.max_attempts}} && not {{system.maintenance_mode}}"
        assert evaluate_expression(expr3, state) == True

        # Content length validation
        expr4 = "{{content.word_count}} >= 1000 && {{content.word_count}} <= 2000"
        assert evaluate_expression(expr4, state) == True

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        state = {
            "empty_string": "",
            "zero": 0,
            "empty_list": [],
            "empty_object": {},
            "nested": {"deep": {"value": None}}
        }

        # Empty values
        assert evaluate_expression("length({{empty_string}})", state) == 0
        assert evaluate_expression("length({{empty_list}})", state) == 0
        assert evaluate_expression("{{zero}} == 0", state) == True
        assert evaluate_expression("isObject({{empty_object}})", state) == True

        # None values
        assert evaluate_expression("{{nested.deep.value}} == null", state) == True

        # String operations on empty strings
        assert evaluate_expression("contains({{empty_string}}, '')", state) == True
        assert evaluate_expression("startsWith({{empty_string}}, '')", state) == True

class TestExpressionValidation:
    """Test expression validation."""

    def test_valid_expressions(self):
        """Test that valid expressions pass validation."""
        valid_expressions = [
            "{{score}} > 80",
            "{{user.role}} in ['admin', 'editor']",
            "contains({{title}}, 'test')",
            "isString({{name}})",
            "{{count}} >= 0 && {{count}} < 100",
            "not {{disabled}}",
            "length({{items}}) > 0"
        ]

        for expr in valid_expressions:
            assert validate_expression(expr), f"Expression should be valid: {expr}"

    def test_invalid_expressions(self):
        """Test that invalid expressions fail validation."""
        invalid_expressions = [
            "{{score} > 80",  # Missing closing brace
            "{{user.role}} in ['admin', ",  # Incomplete array
            "contains({{title}}",  # Missing closing parenthesis
            "unknownFunction(1)",  # Unknown function
            "{{score} && {{count}",  # Multiple syntax errors
            "5 + ",  # Incomplete expression
        ]

        for expr in invalid_expressions:
            assert not validate_expression(expr), f"Expression should be invalid: {expr}"

class TestExpressionParser:
    """Test the expression parser directly."""

    def test_tokenization(self):
        """Test tokenization of expressions."""
        parser = ExpressionParser("{{score}} > 80 && {{attempts}} < 3")

        tokens = parser.tokens
        # Should have variables, operators, numbers, and EOF
        assert len(tokens) > 5
        assert tokens[-1].type.name == "EOF"

    def test_parsing(self):
        """Test parsing produces valid AST."""
        parser = ExpressionParser("{{score}} > 80 && {{attempts}} < 3")

        ast = parser.parse()
        assert ast is not None
        # Should be a binary operation (&&) with comparisons on both sides

if __name__ == "__main__":
    pytest.main([__file__])