"""Canonical Gson dumps for the Config/SimpleCSV area (T05).

The ConfigProbe hashes CSV rows by writing each one as a Gson
``JsonObject`` (``toString``) followed by a newline and hashing the UTF-8
bytes. Gson 2.9's ``JsonWriter`` (as used by ``JsonObject.toString``,
html-safe off) escapes only the double quote, the backslash, the named
control characters (\\b \\t \\n \\f \\r), other characters below U+0020
(as lowercase ``\\uXXXX``) and U+2028/U+2029; everything else, including
``<>&='`` and non-ASCII text, is written raw. That is NOT what Python's
``json.dumps`` produces, so the exact escaping is reproduced here.
"""

from __future__ import annotations

import hashlib

_NAMED_ESCAPES = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def gson_escape(value: str) -> str:
    """Escape one string exactly as Gson's JsonWriter writes it."""
    out: list[str] = []
    for ch in value:
        named = _NAMED_ESCAPES.get(ch)
        if named is not None:
            out.append(named)
        elif ord(ch) < 0x20 or ord(ch) in (0x2028, 0x2029):
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    return "".join(out)


def gson_row_dump(row: dict[str, str]) -> str:
    """Dump one row as a Gson JsonObject string, keys in row order."""
    parts = [f'"{gson_escape(key)}":"{gson_escape(value)}"' for key, value in row.items()]
    return "{" + ",".join(parts) + "}"


def rows_sha256(rows: list[dict[str, str]]) -> str:
    """SHA-256 of the probe's canonical dump: each row dump plus "\\n"."""
    digest = hashlib.sha256()
    for row in rows:
        digest.update((gson_row_dump(row) + "\n").encode("utf-8"))
    return digest.hexdigest()
