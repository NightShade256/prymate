#!/bin/sh

echo Running Monkey Language Tests

# Run Prymate tests, only supports windows with git bash.
python -m unittest tests.lexer_test tests.ast_test tests.parser_test tests.evaluator_test tests.objects_test