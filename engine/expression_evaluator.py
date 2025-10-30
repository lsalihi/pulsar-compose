"""
Advanced expression evaluator for Pulsar conditional execution.

Supports template variables, string operations, membership tests, and type checking.
"""

import re
import ast
import operator
from typing import Any, Dict, List, Union, Callable
from dataclasses import dataclass
from enum import Enum

class ExpressionError(Exception):
    """Custom exception for expression evaluation errors."""
    pass

class TokenType(Enum):
    """Token types for expression parsing."""
    VARIABLE = "variable"
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OPERATOR = "operator"
    FUNCTION = "function"
    PARENTHESIS = "parenthesis"
    EOF = "eof"

@dataclass
class Token:
    """Token representation."""
    type: TokenType
    value: Any
    position: int

def _raise_type_error(func_name: str, value: Any) -> None:
    raise ExpressionError(f"{func_name}() expects string, array, or object, got {type(value).__name__}")

class ExpressionParser:
    """Parser for expression language."""

    # Operator precedence (higher number = higher precedence)
    OPERATORS = {
        '||': (1, lambda a, b: a or b),
        '&&': (2, lambda a, b: a and b),
        '==': (3, lambda a, b: a == b),
        '!=': (3, lambda a, b: a != b),
        '<': (4, lambda a, b: a < b),
        '<=': (4, lambda a, b: a <= b),
        '>': (4, lambda a, b: a > b),
        '>=': (4, lambda a, b: a >= b),
        '+': (5, lambda a, b: a + b),
        '-': (5, lambda a, b: a - b),
        '*': (6, lambda a, b: a * b),
        '/': (6, lambda a, b: a / b),
        '%': (6, lambda a, b: a % b),
    }

    # Supported functions
    FUNCTIONS = {
        'contains': lambda s, substr: substr in str(s),
        'startsWith': lambda s, prefix: str(s).startswith(str(prefix)),
        'endsWith': lambda s, suffix: str(s).endswith(str(suffix)),
        'isString': lambda x: isinstance(x, str),
        'isNumber': lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        'isObject': lambda x: isinstance(x, dict),
        'isArray': lambda x: isinstance(x, list),
        'length': lambda x: len(x) if isinstance(x, (str, list, dict)) else _raise_type_error('length', x),
        'upper': lambda s: str(s).upper(),
        'lower': lambda s: str(s).lower(),
        'trim': lambda s: str(s).strip(),
    }

    def __init__(self, expression: str):
        self.expression = expression
        self.tokens = self._tokenize()
        self.current_token_index = 0

    def _tokenize(self) -> List[Token]:
        """Tokenize the expression string."""
        tokens = []
        i = 0

        while i < len(self.expression):
            char = self.expression[i]

            if char.isspace():
                i += 1
                continue

            # Handle template variables {{variable}}
            if char == '{' and i + 1 < len(self.expression) and self.expression[i + 1] == '{':
                var_match = re.match(r'\{\{([^}]+)\}\}', self.expression[i:])
                if var_match:
                    tokens.append(Token(TokenType.VARIABLE, var_match.group(1).strip(), i))
                    i += var_match.end()
                    continue

            # Handle string literals
            if char in ('"', "'"):
                start = i
                i += 1
                while i < len(self.expression) and self.expression[i] != char:
                    if self.expression[i] == '\\':
                        i += 2
                    else:
                        i += 1
                if i < len(self.expression):
                    i += 1
                tokens.append(Token(TokenType.STRING, self.expression[start:i], start))
                continue

            # Handle numbers
            if char.isdigit() or (char == '-' and i + 1 < len(self.expression) and self.expression[i + 1].isdigit()):
                start = i
                i += 1
                while i < len(self.expression) and (self.expression[i].isdigit() or self.expression[i] == '.'):
                    i += 1
                try:
                    value = float(self.expression[start:i]) if '.' in self.expression[start:i] else int(self.expression[start:i])
                    tokens.append(Token(TokenType.NUMBER, value, start))
                except ValueError:
                    raise ExpressionError(f"Invalid number: {self.expression[start:i]}")
                continue

            # Handle boolean literals
            if self.expression[i:i+4].lower() == 'true':
                tokens.append(Token(TokenType.BOOLEAN, True, i))
                i += 4
                continue
            elif self.expression[i:i+5].lower() == 'false':
                tokens.append(Token(TokenType.BOOLEAN, False, i))
                i += 5
                continue

            # Handle null literal
            if self.expression[i:i+4].lower() == 'null':
                tokens.append(Token(TokenType.VARIABLE, None, i))  # Treat null as a special variable
                i += 4
                continue

            # Handle operators (longest match first)
            operator_found = False
            for op in sorted(self.OPERATORS.keys(), key=len, reverse=True):
                if self.expression[i:i+len(op)] == op:
                    tokens.append(Token(TokenType.OPERATOR, op, i))
                    i += len(op)
                    operator_found = True
                    break
            if operator_found:
                continue

            # Handle 'in' and 'not in'
            if self.expression[i:i+6] == 'not in':
                tokens.append(Token(TokenType.OPERATOR, 'not in', i))
                i += 6
                continue
            elif self.expression[i:i+2] == 'in':
                tokens.append(Token(TokenType.OPERATOR, 'in', i))
                i += 2
                continue

            # Handle 'not'
            if self.expression[i:i+3] == 'not':
                tokens.append(Token(TokenType.OPERATOR, 'not', i))
                i += 3
                continue

            # Handle brackets for arrays
            if char in '[]':
                tokens.append(Token(TokenType.PARENTHESIS, char, i))
                i += 1
                continue

            # Handle parentheses
            if char in '()':
                tokens.append(Token(TokenType.PARENTHESIS, char, i))
                i += 1
                continue

            # Handle commas (for array/function arguments)
            if char == ',':
                tokens.append(Token(TokenType.OPERATOR, ',', i))
                i += 1
                continue

            # Handle function calls and identifiers
            if char.isalpha() or char == '_':
                start = i
                while i < len(self.expression) and (self.expression[i].isalnum() or self.expression[i] == '_'):
                    i += 1
                identifier = self.expression[start:i]

                # Check if it's a function
                if identifier in self.FUNCTIONS:
                    tokens.append(Token(TokenType.FUNCTION, identifier, start))
                else:
                    # Assume it's a variable
                    tokens.append(Token(TokenType.VARIABLE, identifier, start))
                continue

            raise ExpressionError(f"Unexpected character '{char}' at position {i}")

        tokens.append(Token(TokenType.EOF, None, i))
        return tokens

    def _current_token(self) -> Token:
        """Get current token."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return self.tokens[-1]  # EOF token

    def _consume_token(self, expected_type: TokenType = None) -> Token:
        """Consume and return current token."""
        token = self._current_token()
        if expected_type and token.type != expected_type:
            raise ExpressionError(f"Expected {expected_type.value}, got {token.type.value} at position {token.position}")
        self.current_token_index += 1
        return token

    def parse(self) -> 'ExpressionNode':
        """Parse the expression and return the AST root."""
        try:
            result = self._parse_or_expression()
            if self._current_token().type != TokenType.EOF:
                raise ExpressionError(f"Unexpected token after expression: {self._current_token().value}")
            return result
        except Exception as e:
            if isinstance(e, ExpressionError):
                raise
            raise ExpressionError(f"Parse error: {str(e)}")

    def _parse_or_expression(self) -> 'ExpressionNode':
        """Parse OR expressions (lowest precedence)."""
        left = self._parse_and_expression()

        while self._current_token().type == TokenType.OPERATOR and self._current_token().value == '||':
            operator = self._consume_token().value
            right = self._parse_and_expression()
            left = BinaryOpNode(left, operator, right)

        return left

    def _parse_and_expression(self) -> 'ExpressionNode':
        """Parse AND expressions."""
        left = self._parse_comparison_expression()

        while self._current_token().type == TokenType.OPERATOR and self._current_token().value == '&&':
            operator = self._consume_token().value
            right = self._parse_comparison_expression()
            left = BinaryOpNode(left, operator, right)

        return left

    def _parse_comparison_expression(self) -> 'ExpressionNode':
        """Parse comparison expressions."""
        left = self._parse_additive_expression()

        if self._current_token().type == TokenType.OPERATOR:
            op = self._current_token().value
            if op in ('==', '!=', '<', '<=', '>', '>=', 'in', 'not in'):
                self._consume_token()
                right = self._parse_additive_expression()
                return BinaryOpNode(left, op, right)

        return left

    def _parse_additive_expression(self) -> 'ExpressionNode':
        """Parse additive expressions (+, -)."""
        left = self._parse_multiplicative_expression()

        while self._current_token().type == TokenType.OPERATOR and self._current_token().value in ('+', '-'):
            operator = self._consume_token().value
            right = self._parse_multiplicative_expression()
            left = BinaryOpNode(left, operator, right)

        return left

    def _parse_multiplicative_expression(self) -> 'ExpressionNode':
        """Parse multiplicative expressions (*, /, %)."""
        left = self._parse_unary_expression()

        while self._current_token().type == TokenType.OPERATOR and self._current_token().value in ('*', '/', '%'):
            operator = self._consume_token().value
            right = self._parse_unary_expression()
            left = BinaryOpNode(left, operator, right)

        return left

    def _parse_unary_expression(self) -> 'ExpressionNode':
        """Parse unary expressions (not)."""
        if self._current_token().type == TokenType.OPERATOR and self._current_token().value == 'not':
            self._consume_token()
            return UnaryOpNode('not', self._parse_unary_expression())

        return self._parse_primary_expression()

    def _parse_primary_expression(self) -> 'ExpressionNode':
        """Parse primary expressions (literals, variables, function calls, parentheses, arrays)."""
        token = self._current_token()

        if token.type == TokenType.NUMBER:
            self._consume_token()
            return LiteralNode(token.value)

        elif token.type == TokenType.STRING:
            self._consume_token()
            # Remove quotes
            value = token.value[1:-1] if len(token.value) >= 2 else token.value
            return LiteralNode(value)

        elif token.type == TokenType.BOOLEAN:
            self._consume_token()
            return LiteralNode(token.value)

        elif token.type == TokenType.VARIABLE:
            var_token = self._consume_token()
            # Handle null literal
            if var_token.value is None:
                return LiteralNode(None)
            # Handle array indexing after variable
            variable_node = VariableNode(var_token.value)
            return self._parse_array_access(variable_node)

        elif token.type == TokenType.FUNCTION:
            return self._parse_function_call()

        elif token.type == TokenType.PARENTHESIS and token.value == '(':
            self._consume_token(TokenType.PARENTHESIS)
            expr = self._parse_or_expression()
            self._consume_token(TokenType.PARENTHESIS)  # Should be ')'
            return expr

        elif token.type == TokenType.PARENTHESIS and token.value == '[':
            return self._parse_array_literal()

        else:
            raise ExpressionError(f"Unexpected token: {token.type.value} '{token.value}' at position {token.position}")

    def _parse_array_access(self, variable_node: 'VariableNode') -> 'ExpressionNode':
        """Parse array access after a variable (e.g., var[0])."""
        if self._current_token().type == TokenType.PARENTHESIS and self._current_token().value == '[':
            self._consume_token()  # consume '['
            index_expr = self._parse_or_expression()
            self._consume_token(TokenType.PARENTHESIS)  # consume ']'
            
            # Create a special node for array access
            array_access_node = ArrayAccessNode(variable_node, index_expr)
            # Allow chaining: var[0][1]
            return self._parse_array_access(array_access_node)
        else:
            return variable_node

    def _parse_array_literal(self) -> 'ArrayLiteralNode':
        """Parse array literals like [1, 2, 'hello']."""
        self._consume_token(TokenType.PARENTHESIS)  # Should be '['

        elements = []
        if self._current_token().type != TokenType.PARENTHESIS or self._current_token().value != ']':
            elements.append(self._parse_or_expression())
            while self._current_token().type == TokenType.OPERATOR and self._current_token().value == ',':
                self._consume_token()
                elements.append(self._parse_or_expression())

        self._consume_token(TokenType.PARENTHESIS)  # Should be ']'
        return ArrayLiteralNode(elements)

    def _parse_function_call(self) -> 'FunctionCallNode':
        """Parse function calls."""
        func_name = self._consume_token(TokenType.FUNCTION).value
        self._consume_token(TokenType.PARENTHESIS)  # Should be '('

        args = []
        if self._current_token().type != TokenType.PARENTHESIS or self._current_token().value != ')':
            args.append(self._parse_or_expression())
            while self._current_token().type == TokenType.OPERATOR and self._current_token().value == ',':
                self._consume_token()
                args.append(self._parse_or_expression())

        self._consume_token(TokenType.PARENTHESIS)  # Should be ')'
        return FunctionCallNode(func_name, args)

# AST Node classes
class ExpressionNode:
    """Base class for expression AST nodes."""
    pass

@dataclass
class LiteralNode(ExpressionNode):
    """Literal value node."""
    value: Any

@dataclass
class VariableNode(ExpressionNode):
    """Variable reference node."""
    name: str

@dataclass
class BinaryOpNode(ExpressionNode):
    """Binary operation node."""
    left: ExpressionNode
    operator: str
    right: ExpressionNode

@dataclass
class UnaryOpNode(ExpressionNode):
    """Unary operation node."""
    operator: str
    operand: ExpressionNode

@dataclass
class FunctionCallNode(ExpressionNode):
    """Function call node."""
    function_name: str
    arguments: List[ExpressionNode]

@dataclass
class ArrayLiteralNode(ExpressionNode):
    """Array literal node."""
    elements: List[ExpressionNode]

@dataclass
class ArrayAccessNode(ExpressionNode):
    """Array access node (e.g., arr[0])."""
    array: ExpressionNode
    index: ExpressionNode

class ExpressionEvaluator:
    """Evaluator for parsed expressions."""

    def __init__(self, state: Dict[str, Any]):
        self.state = state

    def evaluate(self, node: ExpressionNode) -> Any:
        """Evaluate an expression node."""
        if isinstance(node, LiteralNode):
            return node.value

        elif isinstance(node, VariableNode):
            return self._resolve_variable(node.name)

        elif isinstance(node, ArrayLiteralNode):
            return [self.evaluate(element) for element in node.elements]

        elif isinstance(node, ArrayAccessNode):
            array_value = self.evaluate(node.array)
            index_value = self.evaluate(node.index)
            
            if not isinstance(array_value, list):
                raise ExpressionError(f"Cannot index into non-array value: {type(array_value)}")
            
            try:
                index_int = int(index_value)
                return array_value[index_int]
            except (ValueError, IndexError) as e:
                raise ExpressionError(f"Invalid array access: {e}")

        elif isinstance(node, BinaryOpNode):
            return self._evaluate_binary_op(node)

        elif isinstance(node, UnaryOpNode):
            return self._evaluate_unary_op(node)

        elif isinstance(node, FunctionCallNode):
            return self._evaluate_function_call(node)

        else:
            raise ExpressionError(f"Unknown node type: {type(node)}")

    def _resolve_variable(self, name: str) -> Any:
        """Resolve a variable from state using dot notation and array indexing."""
        # Handle array indexing like items[0]
        array_match = re.match(r'^([^[\]]+)\[(\d+)\]$', name)
        if array_match:
            var_name = array_match.group(1)
            index = int(array_match.group(2))

            if var_name not in self.state:
                raise ExpressionError(f"Variable '{var_name}' not found in state")
            var_value = self.state[var_name]

            if not isinstance(var_value, list):
                raise ExpressionError(f"Variable '{var_name}' is not a list")
            if index >= len(var_value):
                raise ExpressionError(f"Index {index} out of bounds for '{var_name}' (length {len(var_value)})")

            return var_value[index]

        # Handle dot notation
        parts = name.split('.')
        current = self.state

        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    raise ExpressionError(f"Variable '{name}' not found in state (missing '{part}')")
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    raise ExpressionError(f"Invalid list index '{part}' in variable '{name}'")
            else:
                raise ExpressionError(f"Cannot access property '{part}' on {type(current).__name__}")

        return current

    def _evaluate_binary_op(self, node: BinaryOpNode) -> Any:
        """Evaluate binary operations."""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if node.operator == '||':
            return left or right
        elif node.operator == '&&':
            return left and right
        elif node.operator == '==':
            return left == right
        elif node.operator == '!=':
            return left != right
        elif node.operator == '<':
            return left < right
        elif node.operator == '<=':
            return left <= right
        elif node.operator == '>':
            return left > right
        elif node.operator == '>=':
            return left >= right
        elif node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise ExpressionError("Division by zero")
            return left / right
        elif node.operator == '%':
            return left % right
        elif node.operator == 'in':
            return left in right
        elif node.operator == 'not in':
            return left not in right
        else:
            raise ExpressionError(f"Unknown binary operator: {node.operator}")

    def _evaluate_unary_op(self, node: UnaryOpNode) -> Any:
        """Evaluate unary operations."""
        operand = self.evaluate(node.operand)

        if node.operator == 'not':
            return not operand
        else:
            raise ExpressionError(f"Unknown unary operator: {node.operator}")

    def _evaluate_function_call(self, node: FunctionCallNode) -> Any:
        """Evaluate function calls."""
        if node.function_name not in ExpressionParser.FUNCTIONS:
            raise ExpressionError(f"Unknown function: {node.function_name}")

        func = ExpressionParser.FUNCTIONS[node.function_name]
        args = [self.evaluate(arg) for arg in node.arguments]

        try:
            return func(*args)
        except Exception as e:
            raise ExpressionError(f"Function '{node.function_name}' error: {str(e)}")

def evaluate_expression(expression: str, state: Dict[str, Any]) -> Any:
    """
    Evaluate an expression with the given state.

    Args:
        expression: Expression string to evaluate
        state: State dictionary for variable resolution

    Returns:
        Result of the expression evaluation

    Raises:
        ExpressionError: If expression is invalid or evaluation fails
    """
    parser = ExpressionParser(expression)
    ast = parser.parse()
    evaluator = ExpressionEvaluator(state)
    return evaluator.evaluate(ast)

def validate_expression(expression: str) -> bool:
    """
    Validate that an expression can be parsed without errors.

    Args:
        expression: Expression string to validate

    Returns:
        True if expression is valid, False otherwise
    """
    try:
        parser = ExpressionParser(expression)
        parser.parse()
        return True
    except ExpressionError:
        return False