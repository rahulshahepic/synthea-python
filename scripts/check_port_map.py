"""Check the Python port against docs/port_map.toml.

Usage:
    uv run python scripts/check_port_map.py                 # structure check (all mapped modules)
    uv run python scripts/check_port_map.py --task T05      # only modules owned by T05
    uv run python scripts/check_port_map.py --task T05 --no-stubs
                                                            # also fail if any stub remains
    uv run python scripts/check_port_map.py --stubs         # report remaining stubs per module
    uv run python scripts/check_port_map.py --skip-owners T01,T02,T03  # ignore those tasks' modules

Structure check, for every mapped module:
  * the file exists and imports cleanly;
  * every Java type (top-level and nested class/interface/enum/record) has a Python class of
    the same name somewhere in the module;
  * every Java method declared directly in a type body (and carrying a modifier) has a
    snake_case attribute on some class (or a module-level function) in the module.
    toString/equals/hashCode/compareTo may be mapped to their dunder equivalents.

A "stub" is a function whose body raises NotImplementedError. A stub whose message
contains "out of scope" is allowed by --no-stubs (see PORTING_GUIDE §8).
"""

from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DUNDER_ALIASES = {
    "to_string": {"__str__", "__repr__"},
    "equals": {"__eq__"},
    "hash_code": {"__hash__", "java_hash_code"},
    "compare_to": {"__lt__", "compare_to"},
    "iterator": {"__iter__"},
    "size": {"__len__"},
}
KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "new",
    "throw",
    "else",
    "synchronized",
    "try",
    "do",
    "super",
    "this",
    "assert",
}
# Java serialization / Object plumbing that has no Python counterpart.
IGNORED_METHODS = {"readObject", "writeObject", "readResolve", "writeReplace", "finalize"}
MODIFIERS = (
    r"(?:public|protected|private|static|final|abstract|synchronized|default|native|strictfp)"
)


def snake(name: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return s.lower()


def strip_java(src: str) -> str:
    """Remove comments, string and char literals (keeps braces honest)."""
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif src.startswith('"""', i):
            j = src.find('"""', i + 3)
            out.append('""')
            i = n if j < 0 else j + 3
        elif c in "\"'":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(c + c)
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


TYPE_RE = re.compile(r"\b(class|interface|enum|record)\s+([A-Za-z_]\w*)")
METHOD_RE = re.compile(
    r"(?:@\w+(?:\([^)]*\))?\s+)*(?:" + MODIFIERS + r"\s+)+(?:<[^>]+>\s+)?"
    r"[\w<>\[\],.?\s]+?\s+([a-zA-Z_]\w*)\s*\($"
)
IFACE_METHOD_RE = re.compile(
    r"(?:@\w+(?:\([^)]*\))?\s+)*(?:<[^>]+>\s+)?[\w<>\[\],.?\s]+?\s+([a-zA-Z_]\w*)\s*\($"
)
CTOR_RE = re.compile(r"(?:" + MODIFIERS + r"\s+)+([A-Z]\w*)\s*\($")


def java_api(path: Path) -> tuple[set[str], set[str]]:
    """Return (type names, method names) declared directly in type bodies."""
    src = strip_java(path.read_text(encoding="utf-8"))
    types: set[str] = set()
    methods: set[str] = set()
    type_depths: list[int] = []  # brace depth of each open type body
    type_kinds: list[str] = []
    pending_kind = ""
    depth = 0
    pending_type: str | None = None
    stmt = ""
    for ch in src:
        if ch == "{":
            m = TYPE_RE.search(stmt)
            if m and not re.search(r"\bnew\s", stmt):
                types.add(m.group(2))
                pending_type = m.group(2)
                pending_kind = m.group(1)
            depth += 1
            if pending_type:
                type_depths.append(depth)
                type_kinds.append(pending_kind)
                pending_type = None
            stmt = ""
        elif ch == "}":
            if type_depths and type_depths[-1] == depth:
                type_depths.pop()
                type_kinds.pop()
            depth -= 1
            stmt = ""
        elif ch == ";":
            stmt = ""
        elif ch == "(":
            in_type_body = bool(type_depths) and type_depths[-1] == depth
            head = " ".join(stmt.split()) + "("
            if in_type_body:
                m = METHOD_RE.search(head)
                if not m and type_kinds[-1] == "interface":
                    m = IFACE_METHOD_RE.search(head)
                if m and m.group(1) not in KEYWORDS and m.group(1) not in IGNORED_METHODS:
                    methods.add(m.group(1))
                elif CTOR_RE.search(head):
                    pass  # constructor -> __init__
            stmt += ch
        else:
            stmt += ch
    methods -= types  # constructors that slipped through
    return types, methods


def python_api(module: object) -> tuple[set[str], set[str]]:
    classes: set[str] = set()
    attrs: set[str] = set()

    def walk(cls: type) -> None:
        classes.add(cls.__name__)
        for name, val in vars(cls).items():
            attrs.add(name)
            if inspect.isclass(val) and val.__module__ == module.__name__:  # type: ignore[attr-defined]
                walk(val)

    for name, val in vars(module).items():
        if inspect.isclass(val) and val.__module__ == module.__name__:  # type: ignore[attr-defined]
            walk(val)
        elif inspect.isfunction(val):
            attrs.add(name)
    return classes, attrs


def stubs_in(path: Path) -> list[tuple[str, int, bool]]:
    """(function name, line, allowed) for functions whose body raises NotImplementedError."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            body = [
                b
                for b in node.body
                if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))
            ]
            if len(body) == 1 and isinstance(body[0], ast.Raise) and body[0].exc is not None:
                exc = body[0].exc
                call = exc.func if isinstance(exc, ast.Call) else exc
                if isinstance(call, ast.Name) and call.id == "NotImplementedError":
                    msg = ""
                    if (
                        isinstance(exc, ast.Call)
                        and exc.args
                        and isinstance(exc.args[0], ast.Constant)
                    ):
                        msg = str(exc.args[0].value)
                    found.append((node.name, node.lineno, "out of scope" in msg.lower()))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task")
    ap.add_argument("--no-stubs", action="store_true")
    ap.add_argument("--stubs", action="store_true")
    ap.add_argument("--existing-only", action="store_true", help="ignore modules not created yet")
    ap.add_argument("--skip-owners", default="", help="comma-separated task IDs to ignore")
    args = ap.parse_args()

    entries = tomllib.loads((ROOT / "docs/port_map.toml").read_text())["module"]
    if args.task:
        entries = [e for e in entries if args.task in e["owners"]]
        if not entries:
            print(f"no modules owned by {args.task}")
            return 1
    skip = {x for x in args.skip_owners.split(",") if x}
    entries = [e for e in entries if not (set(e["owners"]) & skip)]
    errors: list[str] = []
    for e in entries:
        py = ROOT / e["python"]
        if not py.is_file():
            if args.existing_only:
                continue
            errors.append(f"{e['python']}: missing")
            continue
        modname = e["python"].removeprefix("src/").removesuffix(".py").replace("/", ".")
        try:
            module = importlib.import_module(modname)
        except Exception as exc:
            errors.append(f"{e['python']}: import failed: {exc!r}")
            continue
        stubs = stubs_in(py)
        if args.stubs and stubs:
            print(f"{e['python']}: {len(stubs)} stub(s) [{'/'.join(e['owners'])}]")
        if args.no_stubs:
            for name, line, allowed in stubs:
                if not allowed:
                    errors.append(f"{e['python']}:{line}: stub remains: {name}")
        if not e["java"]:
            continue
        jtypes, jmethods = java_api(ROOT / e["java"])
        ptypes, pattrs = python_api(module)
        for t in sorted(jtypes - ptypes):
            errors.append(f"{e['python']}: missing class {t} (Java {Path(e['java']).name})")
        for m in sorted(jmethods):
            s = snake(m)
            if s not in pattrs and not (DUNDER_ALIASES.get(s, set()) & pattrs):
                errors.append(f"{e['python']}: missing method {s} (Java {m})")
    for err in errors:
        print("ERROR", err)
    print(f"checked {len(entries)} module(s): {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
