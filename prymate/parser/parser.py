import enum
import typing

from prymate import ast
from prymate.lexer import Lexer
from prymate.token import Token, TokenType


# Precedence enumeration.
class Precedences(enum.Enum):
    LOWEST = 0
    EQUALS = 1
    LESSGREATER = 2
    SUM = 3
    PRODUCT = 4
    PREFIX = 5
    CALL = 6
    INDEX = 7


# Define precedences for the operators.
OP_PRECEDENCES = {
    TokenType.EQ: Precedences.EQUALS,
    TokenType.NOT_EQ: Precedences.EQUALS,
    TokenType.LT: Precedences.LESSGREATER,
    TokenType.GT: Precedences.LESSGREATER,
    TokenType.PLUS: Precedences.SUM,
    TokenType.MINUS: Precedences.SUM,
    TokenType.SLASH: Precedences.PRODUCT,
    TokenType.ASTERISK: Precedences.PRODUCT,
    TokenType.LPAREN: Precedences.CALL,
    TokenType.LBRACKET: Precedences.INDEX,
}


class Parser:
    def __init__(self, lexer: Lexer) -> None:

        # State variables
        self.lexer = lexer
        self.current_token: Token = None
        self.peek_token: Token = None
        self.errors = []
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}

        # Initial state configuration
        self.next_token()
        self.next_token()

        # Register Prefixes
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_integer_literal)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.TRUE, self.parse_boolean_literal)
        self.register_prefix(TokenType.FALSE, self.parse_boolean_literal)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)
        self.register_prefix(TokenType.IF, self.parse_if_expression)
        self.register_prefix(TokenType.FUNCTION, self.parse_function_literal)
        self.register_prefix(TokenType.STRING, self.parse_string_literal)
        self.register_prefix(TokenType.LBRACKET, self.parse_array_literal)
        self.register_prefix(TokenType.LBRACE, self.parse_dict_literal)

        # Register Infixes
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)
        self.register_infix(TokenType.LPAREN, self.parse_call_expression)
        self.register_infix(TokenType.LBRACKET, self.parse_index_exp)

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.current_token.tp != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()

        return program

    def parse_statement(self) -> ast.Statement:
        if self.current_token.tp == TokenType.LET:
            return self.parse_let_statement()
        elif self.current_token.tp == TokenType.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self) -> typing.Optional[ast.LetStatement]:
        stmt = ast.LetStatement(self.current_token)

        if not self.expect_peek(TokenType.IDENT):
            return None

        stmt.name = ast.Identifier(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        stmt.value = self.parse_expression(Precedences.LOWEST)

        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_return_statement(self) -> typing.Optional[ast.ReturnStatement]:
        stmt = ast.ReturnStatement(self.current_token)
        self.next_token()

        stmt.return_value = self.parse_expression(Precedences.LOWEST)

        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_expression_statement(self) -> typing.Optional[ast.ExpressionStatement]:
        stmt = ast.ExpressionStatement(self.current_token)
        stmt.expression = self.parse_expression(Precedences.LOWEST)
        if self.peek_token.tp == TokenType.SEMICOLON:
            self.next_token()

        return stmt

    def parse_expression(
        self, precedence: Precedences
    ) -> typing.Optional[ast.Expression]:

        prefix = self.prefix_parse_fns.get(self.current_token.tp, None)
        if prefix is None:
            self.prefix_parse_error(self.current_token.tp)
            return None

        left_exp = prefix()

        while (
            self.peek_token.tp != TokenType.SEMICOLON
            and precedence.value < self.peek_precedence().value
        ):
            infix = self.infix_parse_fns.get(self.peek_token.tp, None)
            if infix is None:
                return left_exp

            self.next_token()
            left_exp = infix(left_exp)

        return left_exp

    def parse_identifier(self) -> ast.Identifier:
        return ast.Identifier(self.current_token, self.current_token.literal)

    def parse_integer_literal(self) -> typing.Optional[ast.IntegerLiteral]:
        lit = ast.IntegerLiteral(self.current_token)
        try:
            value = int(self.current_token.literal)
        except ValueError:
            msg = f"Could not parse {self.current_token.literal} as integer."
            self.errors.append(msg)
            return None

        lit.value = value
        return lit

    def parse_boolean_literal(self) -> ast.BooleanLiteral:
        return ast.BooleanLiteral(
            self.current_token, TokenType.TRUE == self.current_token.tp
        )

    def parse_prefix_expression(self) -> ast.PrefixExpression:
        exp = ast.PrefixExpression(self.current_token, self.current_token.literal)
        self.next_token()
        exp.right = self.parse_expression(Precedences.PREFIX)

        return exp

    def parse_infix_expression(self, left: ast.Expression) -> ast.InfixExpression:
        exp = ast.InfixExpression(self.current_token, self.current_token.literal, left)

        precedence = self.current_precedence()
        self.next_token()
        exp.right = self.parse_expression(precedence)
        return exp

    def parse_grouped_expression(self) -> typing.Optional[ast.Expression]:
        self.next_token()
        exp = self.parse_expression(Precedences.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return exp

    def parse_if_expression(self) -> ast.IfExpression:
        exp = ast.IfExpression(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()
        exp.condition = self.parse_expression(Precedences.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        exp.consequence = self.parse_block_statement()

        if self.peek_token.tp == TokenType.ELSE:
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None

            exp.alternative = self.parse_block_statement()

        return exp

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(self.current_token)
        self.next_token()

        while (
            not self.current_token.tp == TokenType.RBRACE
            and not self.current_token.tp == TokenType.EOF
        ):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)

            self.next_token()

        return block

    def parse_function_literal(self) -> ast.FunctionLiteral:
        lit = ast.FunctionLiteral(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        lit.parameters = self.parse_function_parameters()

        if not self.expect_peek(TokenType.LBRACE):
            return None

        lit.body = self.parse_block_statement()
        return lit

    def parse_function_parameters(self) -> list:
        idents = []

        if self.peek_token.tp == TokenType.RPAREN:
            self.next_token()
            return idents

        self.next_token()
        ident = ast.Identifier(self.current_token, self.current_token.literal)
        idents.append(ident)

        while self.peek_token.tp == TokenType.COMMA:
            self.next_token()
            self.next_token()

            ident = ast.Identifier(self.current_token, self.current_token.literal)
            idents.append(ident)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return idents

    def parse_call_expression(self, function: ast.Expression) -> ast.CallExpression:
        exp = ast.CallExpression(self.current_token, function)
        exp.arguments = self.parse_exp_list(TokenType.RPAREN)
        return exp

    def parse_array_literal(self) -> ast.ArrayLiteral:
        array = ast.ArrayLiteral(self.current_token)
        array.elements = self.parse_exp_list(TokenType.RBRACKET)
        return array

    def parse_exp_list(self, end: TokenType) -> list:
        args = []

        if self.peek_token.tp == end:
            self.next_token()
            return args

        self.next_token()
        args.append(self.parse_expression(Precedences.LOWEST))

        while self.peek_token.tp == TokenType.COMMA:
            self.next_token()
            self.next_token()
            args.append(self.parse_expression(Precedences.LOWEST))

        if not self.expect_peek(end):
            return None

        return args

    def parse_string_literal(self) -> ast.StringLiteral:
        return ast.StringLiteral(self.current_token, self.current_token.literal)

    def parse_index_exp(self, left: ast.Expression) -> ast.Expression:
        exp = ast.IndexExpression(self.current_token, left)
        self.next_token()

        exp.index = self.parse_expression(Precedences.LOWEST)

        if not self.expect_peek(TokenType.RBRACKET):
            return None

        return exp

    def parse_dict_literal(self) -> ast.DictionaryLiteral:
        dictionary = ast.DictionaryLiteral(self.current_token)

        while self.peek_token.tp != TokenType.RBRACE:
            self.next_token()
            key = self.parse_expression(Precedences.LOWEST)

            if not self.expect_peek(TokenType.COLON):
                return None

            self.next_token()
            value = self.parse_expression(Precedences.LOWEST)

            dictionary.pairs[key] = value

            if self.peek_token.tp != TokenType.RBRACE and not self.expect_peek(
                TokenType.COMMA
            ):
                return None

        if not self.expect_peek(TokenType.RBRACE):
            return None

        return dictionary

    def expect_peek(self, tp: TokenType) -> bool:
        if self.peek_token.tp == tp:
            self.next_token()
            return True

        self.peek_error(tp)
        return False

    def peek_error(self, tp: TokenType) -> None:
        msg = f"Expected next token to be {tp}, instead got {self.peek_token.tp}."
        self.errors.append(msg)

    def prefix_parse_error(self, tp: TokenType):
        msg = f"Cannot parse {tp} prefix token."
        self.errors.append(msg)

    def register_prefix(self, tp: TokenType, fn: typing.Callable) -> None:
        self.prefix_parse_fns[tp] = fn

    def register_infix(self, tp: TokenType, fn: typing.Callable) -> None:
        self.infix_parse_fns[tp] = fn

    def peek_precedence(self) -> Precedences:
        return OP_PRECEDENCES.get(self.peek_token.tp, Precedences.LOWEST)

    def current_precedence(self) -> Precedences:
        return OP_PRECEDENCES.get(self.current_token.tp, Precedences.LOWEST)
