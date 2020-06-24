#!/bin/sh

echo Running Monkey Language Tests

# Run Prymate Tests, for Linux Distros and Mac OS only.
python3 -m unittest tests.lexer_test tests.ast_test tests.parser_test tests.evaluator_test tests.objects_test