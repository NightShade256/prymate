import unittest

from prymate.ast import Identifier, LetStatement, Program
from prymate.token import Token, TokenType


class TestLexer(unittest.TestCase):
    def test_string(self):
        stmts = []
        let_stmt = LetStatement(Token(TokenType.LET, "let"))
        let_stmt.name = Identifier(Token(TokenType.IDENT, "myVar"), "myVar")
        let_stmt.value = Identifier(Token(TokenType.IDENT, "anotherVar"), "anotherVar")
        stmts.append(let_stmt)
        program = Program()
        program.statements = stmts
        self.assertEqual(
            str(program),
            "let myVar = anotherVar;",
            f"str(program) wrong got {str(program)}",
        )


if __name__ == "__main__":
    unittest.main()
