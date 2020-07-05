import enum
import typing

from .objects import Object

__all__ = ["Environment"]


class IdentType(enum.Enum):
    CONSTANT = 0
    VARIABLE = 1


class Identifier(typing.TypedDict):
    value: Object
    tp: IdentType


class Environment:
    def __init__(self, **kwargs: "Environment") -> None:
        self.store: typing.Dict[str, Identifier] = {}
        self.outer = kwargs.get("outer")

    def get_var(self, name: str) -> typing.Optional[Object]:
        """Get a variable in the current environment."""

        # Get the variable from the store.
        var = self.store.get(name, None)

        # Get the variable from enclosing environment, if it is present.
        if var is None and self.outer is not None:
            var = self.outer.get_var(name)

        # Check is variable is None and return accordingly.
        value: typing.Optional[Object]
        if var is None:
            value = None
        else:
            if isinstance(var, Object):
                value = var
            else:
                value = var.get("value")

        return value

    def set_var(self, name: str, val: Object, **kwargs: bool) -> Object:
        tp = (
            IdentType.VARIABLE if not kwargs.get("const", False) else IdentType.CONSTANT
        )

        self.store[name] = {"value": val, "tp": tp}
        return val

    def reassign_var(self, name: str, val: Object) -> typing.Optional[bool]:
        if self.store.get(name, None) is None:
            return False

        tp = self.store[name].get("tp")
        if tp == IdentType.CONSTANT:
            return None

        self.store[name] = {"value": val, "tp": IdentType.VARIABLE}
        return True
