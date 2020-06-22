import typing

from prymate.objects import Object


class Environment:
    def __init__(self, **kwargs) -> None:
        self.store = {}
        self.outer = kwargs.get("outer", None)

    def get_var(self, name: str) -> typing.Optional[Object]:
        obj = self.store.get(name, None)
        if obj is None and self.outer is not None:
            obj = self.outer.get_var(name)

        return obj

    def set_var(self, name: str, val: Object) -> Object:
        self.store[name] = val
        return val
