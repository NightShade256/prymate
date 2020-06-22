import typing

from prymate import ast, objects

from .builtins import BUILTINS

SINGLETONS = {
    "NULL": objects.Null(),
    "TRUE": objects.Boolean(True),
    "FALSE": objects.Boolean(False),
}


def evaluate(node: ast.Node, env: objects.Environment) -> objects.Object:
    if isinstance(node, ast.Program):
        return eval_program(node.statements, env)
    elif isinstance(node, ast.ExpressionStatement):
        return evaluate(node.expression, env)
    elif isinstance(node, ast.IntegerLiteral):
        return objects.Integer(node.value)
    elif isinstance(node, ast.BooleanLiteral):
        if node.value:
            return SINGLETONS["TRUE"]

        return SINGLETONS["FALSE"]
    elif isinstance(node, ast.StringLiteral):
        return objects.String(node.value)
    elif isinstance(node, ast.PrefixExpression):
        right = evaluate(node.right, env)
        if is_error(right):
            return right

        return eval_prefix_exp(node.operator, right)
    elif isinstance(node, ast.InfixExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            return left

        right = evaluate(node.right, env)
        if is_error(right):
            return right

        return eval_infix_exp(node.operator, left, right)
    elif isinstance(node, ast.BlockStatement):
        return eval_block_statements(node, env)
    elif isinstance(node, ast.IfExpression):
        return eval_if_exp(node, env)
    elif isinstance(node, ast.ReturnStatement):
        val = evaluate(node.return_value, env)
        if is_error(val):
            return val

        return objects.ReturnValue(val)
    elif isinstance(node, ast.LetStatement):
        val = evaluate(node.value, env)
        if is_error(val):
            return val

        env.set_var(node.name.value, val)
    elif isinstance(node, ast.Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return objects.Function(params, body, env)
    elif isinstance(node, ast.CallExpression):
        function = evaluate(node.function, env)
        if is_error(function):
            return function

        args = eval_exps(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]

        return apply_function(function, args)
    elif isinstance(node, ast.ArrayLiteral):
        elements = eval_exps(node.elements, env)
        if len(elements) == 1 and is_error(elements[0]):
            return elements[0]

        return objects.Array(elements)
    elif isinstance(node, ast.IndexExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            return left

        index = evaluate(node.index, env)
        if is_error(index):
            return index

        return eval_index_expression(left, index)
    elif isinstance(node, ast.DictionaryLiteral):
        return eval_dictionary_literal(node, env)

    return None


def eval_program(stmts: list, env: objects.Environment) -> objects.Object:
    result: objects.Object = None

    for statement in stmts:
        result = evaluate(statement, env)
        if isinstance(result, objects.ReturnValue):
            return result.value
        elif isinstance(result, objects.Error):
            return result

    return result


def eval_prefix_exp(operator: str, right: objects.Object) -> objects.Object:
    if operator == "!":
        return eval_bang_operator_exp(right)
    elif operator == "-":
        return eval_minus_preoperator_exp(right)
    else:
        return objects.Error(f"unknown operator: {operator}{right.tp().value}")


def eval_bang_operator_exp(right: objects.Object) -> objects.Object:
    if right is SINGLETONS["TRUE"]:
        return SINGLETONS["FALSE"]
    elif right is SINGLETONS["FALSE"]:
        return SINGLETONS["TRUE"]
    elif right is SINGLETONS["NULL"]:
        return SINGLETONS["TRUE"]
    else:
        return SINGLETONS["FALSE"]


def eval_minus_preoperator_exp(right: objects.Object) -> objects.Object:
    if right.tp() != objects.ObjectType.INTEGER:
        return objects.Error(f"unknown operator: -{right.tp().value}")

    value = right.value
    return objects.Integer(-value)


def eval_infix_exp(operator: str, left: objects.Object, right: objects.Object):
    if (
        left.tp() == objects.ObjectType.INTEGER
        and right.tp() == objects.ObjectType.INTEGER
    ):
        return eval_int_infix_exp(operator, left, right)
    elif (
        left.tp() == objects.ObjectType.BOOLEAN
        and right.tp() == objects.ObjectType.BOOLEAN
    ):
        return eval_bool_infix_exp(operator, left, right)
    elif (
        left.tp() == objects.ObjectType.STRING
        and right.tp() == objects.ObjectType.STRING
    ):
        return eval_string_infix_exp(operator, left, right)
    elif operator == "==":
        return to_boolean_singleton(left is right)
    elif operator == "!=":
        return to_boolean_singleton(left is not right)
    elif left.tp() != right.tp():
        return objects.Error(
            f"type mismatch: {left.tp().value} {operator} {right.tp().value}"
        )
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_int_infix_exp(
    operator: str, left: objects.Integer, right: objects.Integer
) -> typing.Union[objects.Integer, objects.Boolean, objects.Error]:
    left_val = left.value
    right_val = right.value

    if operator == "+":
        return objects.Integer(left_val + right_val)
    elif operator == "-":
        return objects.Integer(left_val - right_val)
    elif operator == "*":
        return objects.Integer(left_val * right_val)
    elif operator == "/":
        return objects.Integer(int(left_val / right_val))
    elif operator == "<":
        return to_boolean_singleton(left_val < right_val)
    elif operator == ">":
        return to_boolean_singleton(left_val > right_val)
    elif operator == "==":
        return to_boolean_singleton(left_val == right_val)
    elif operator == "!=":
        return to_boolean_singleton(left_val != right_val)
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_bool_infix_exp(
    operator: str, left: objects.Boolean, right: objects.Boolean
) -> objects.Object:
    if operator == "==":
        return to_boolean_singleton(left is right)
    elif operator == "!=":
        return to_boolean_singleton(left is not right)
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_string_infix_exp(
    operator: str, left: objects.String, right: objects.String
) -> objects.Object:
    if operator == "+":
        return objects.String(left.value + right.value)
    elif operator == "==":
        return to_boolean_singleton(left.value == right.value)
    elif operator == "!=":
        return to_boolean_singleton(left.value != right.value)
    else:
        return objects.Error(
            f"unknown operator: {left.tp().value} {operator} {right.tp().value}"
        )


def eval_if_exp(exp: ast.IfExpression, env: objects.Environment) -> objects.Object:
    condition = evaluate(exp.condition, env)
    if is_error(condition):
        return condition

    if is_truthy(condition):
        return evaluate(exp.consequence, env)
    elif exp.alternative is not None:
        return evaluate(exp.alternative, env)
    else:
        return SINGLETONS["NULL"]


def eval_block_statements(block: ast.BlockStatement, env: objects.Environment):
    result: objects.Object = None

    for stmt in block.statements:
        result = evaluate(stmt, env)

        if result is not None:
            tp = result.tp()
            if tp == objects.ObjectType.RETURN_VALUE or tp == objects.ObjectType.ERROR:
                return result

    return result


def eval_identifier(node: ast.Identifier, env: objects.Environment) -> objects.Object:
    val = env.get_var(node.value)
    if val is not None:
        return val

    val = BUILTINS.get(node.value, None)
    if val is not None:
        return val

    return objects.Error(f"identifier not found: {node.value}")


def eval_dictionary_literal(node: ast.DictionaryLiteral, env: objects.Environment):
    pairs = {}

    for keynode, valnode in node.pairs.items():
        key = evaluate(keynode, env)
        if is_error(key):
            return key

        if not isinstance(key, objects.Hashable):
            return objects.Error(f"unusable as hash key: {key.tp().value}")

        value = evaluate(valnode, env)
        if is_error(value):
            return value

        hashed = key.hashkey()
        pairs[hashed] = objects.HashPair(key, value)

    return objects.Dictionary(pairs)


def eval_exps(exps: list, env: objects.Environment) -> list:
    result = []

    for exp in exps:
        evaluated = evaluate(exp, env)
        if is_error(evaluated):
            return [evaluated]

        result.append(evaluated)

    return result


def apply_function(fn: objects.Object, args: list) -> objects.Object:
    if isinstance(fn, objects.Function):
        extended_env = extend_function_env(fn, args)
        evaluated = evaluate(fn.body, extended_env)
        return unwrap_return_value(evaluated)
    elif isinstance(fn, objects.Builtin):
        return fn.function(args)
    else:
        return objects.Error(f"not a function: {fn.tp()}")


def extend_function_env(fn: objects.Function, args: list) -> objects.Environment:
    env = objects.Environment(outer=fn.env)

    for count, param in enumerate(fn.parameters):
        env.set_var(param.value, args[count])

    return env


def unwrap_return_value(obj: objects.Object) -> objects.Object:
    if isinstance(obj, objects.ReturnValue):
        return obj.value

    return obj


def eval_index_expression(
    left: objects.Object, index: objects.Object
) -> objects.Object:
    if (
        left.tp() == objects.ObjectType.ARRAY
        and index.tp() == objects.ObjectType.INTEGER
    ):
        return eval_array_index_exp(left, index)
    elif left.tp() == objects.ObjectType.DICTIONARY:
        return eval_dict_index_exp(left, index)
    else:
        return objects.Error(f"index operator not supported: {left.tp().value}")


def eval_array_index_exp(
    array: objects.Array, index: objects.Integer
) -> objects.Object:
    idx = index.value
    max_len = len(array.elements) - 1

    if idx < 0 or idx > max_len:
        return SINGLETONS["NULL"]

    return array.elements[idx]


def eval_dict_index_exp(dictl: objects.Object, index: objects.Object) -> objects.Object:

    if not isinstance(index, objects.Hashable):
        return objects.Error(f"unusable as dictionary key: {index.tp().value}")

    pair = dictl.pairs.get(index.hashkey(), None)
    if pair is None:
        return SINGLETONS["NULL"]

    return pair.value


def to_boolean_singleton(case: bool) -> objects.Boolean:
    if case:
        return SINGLETONS["TRUE"]

    return SINGLETONS["FALSE"]


def is_truthy(obj: objects.Object) -> bool:
    if obj is SINGLETONS["NULL"]:
        return False
    elif obj is SINGLETONS["TRUE"]:
        return True
    elif obj is SINGLETONS["FALSE"]:
        return False
    else:
        return True


def is_error(obj: objects.Object) -> bool:
    if obj is not None:
        return obj.tp() == objects.ObjectType.ERROR

    return False
