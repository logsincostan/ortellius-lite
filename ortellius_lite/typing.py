"""typeguards and stuff."""

from collections.abc import Set as AbstractSet
from typing import TypeGuard, cast, overload


@overload
def is_set[T](x: object, t: type[T]) -> TypeGuard[AbstractSet[T]]: ...
@overload
def is_set(x: object) -> TypeGuard[AbstractSet[object]]: ...
def is_set(x: object, t: type[object] = object) -> bool:
    """Check if a set is a set of a certain type."""
    if not isinstance(x, AbstractSet):
        return False
    if t is object:
        return True

    s = cast("AbstractSet[object]", x)
    return all(isinstance(y, t) for y in s)


@overload
def is_list[T](x: object, t: type[T]) -> TypeGuard[list[T]]: ...
@overload
def is_list(x: object) -> TypeGuard[list[object]]: ...
def is_list(x: object, t: type[object] = object) -> bool:
    """Check if a list is a list of a certain type."""
    if not isinstance(x, list):
        return False
    if t is object:
        return True

    s = cast("list[object]", x)
    return all(isinstance(y, t) for y in s)
