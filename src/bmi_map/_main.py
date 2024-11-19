import argparse
import re
import sys
import tomllib
from collections.abc import Sequence
from functools import partial
from typing import Any

from bmi_map.bmi_map import bmi_map

try:
    import pygments
    import pygments.lexers
    from pygments.formatters import TerminalTrueColorFormatter

    with_pygments = True
except ImportError:
    with_pygments = False


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--to",
        help="language for which to generate mappings",
        choices=("c", "c++", "fortran", "python", "sidl"),
        default="sidl",
    )
    parser.add_argument("--include", default=".*", help="Functions to include")
    parser.add_argument(
        "--color",
        choices=("always", "auto", "never"),
        default="auto",
        help="When to use syntax highlighting.",
    )

    args = parser.parse_args(argv)

    color = args.color if with_pygments else "never"

    funcs = _filter_keys(tomllib.load(sys.stdin.buffer)["bmi"], include=args.include)

    mapped_funcs = bmi_map(funcs, to=args.to)

    if color == "always" or (color == "auto" and sys.stdout.isatty()):
        highlight = Highlighter(args.to)
        mapped_funcs = [highlight(mapped_func) for mapped_func in mapped_funcs]

    print("\n".join(mapped_funcs))

    return 0


def _filter_keys(d: dict[str, Any], include: str = ".*") -> dict[str, Any]:
    pattern = re.compile(include)
    return {k: v for k, v in d.items() if pattern.search(k)}


class Highlighter:
    def __init__(self, language: str):
        if language == "sidl":
            language = "java"

        self._highlight = partial(
            pygments.highlight,
            lexer=pygments.lexers.find_lexer_class_by_name(language)(ensurenl=False),
            formatter=TerminalTrueColorFormatter(),
        )

    def __call__(self, line: str) -> str:
        return self._highlight(line)


if __name__ == "__main__":
    SystemExit(main())
