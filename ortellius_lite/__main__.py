"""Map SVD files to memory map."""

import argparse
import logging
from collections.abc import Callable, Iterable, Mapping
from inspect import getdoc, signature

from .actions import rank_shadow_jaccard


def _add_subparsers(
    parser: argparse.ArgumentParser,
    funcs: Iterable[Callable[..., None]],
    default_args: Mapping[str, type] | None = None,
) -> None:
    if default_args is None:
        default_args = {}

    subparsers = parser.add_subparsers(required=True)
    for func in funcs:
        subparser = subparsers.add_parser(func.__name__, help=getdoc(func))
        subparser.set_defaults(func=func)

        params = dict(signature(func, eval_str=True).parameters)
        for arg, typ in default_args.items():
            if arg not in params:
                msg = f"function {func.__name__} has no parameter {arg}"
                raise ValueError(msg)
            if params[arg].annotation != typ:
                msg = (
                    f"parameter {arg} of {func.__name__} "
                    f"has wrong type {params[arg].annotation!r} != {typ!r}"
                )
                raise TypeError(msg)
            del params[arg]

        for param in params.values():
            if param.annotation == param.empty:
                msg = (
                    f"Parameter {param.name} of {func.__name__} has no type annotation"
                )
                raise TypeError(msg)
            if param.default == param.empty:
                subparser.add_argument(param.name, type=param.annotation)
                continue
            subparser.add_argument(
                param.name,
                type=param.annotation,
                default=param.default,
                nargs="?",
            )


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify connected device by its register reset values.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="verbose output",
        default=False,
    )
    _add_subparsers(
        parser,
        [
            rank_shadow_jaccard,
        ],
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format=f"{args.func.__name__} %(asctime)s %(message)s",
    )

    params = vars(args).copy()
    del params["func"]
    del params["verbose"]
    args.func(**params)


_main()
