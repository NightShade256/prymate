@echo off

echo Running Monkey Language Tests
python -m unittest tests.lexer_test tests.ast_test tests.parser_test tests.evaluator_test tests.objects_test