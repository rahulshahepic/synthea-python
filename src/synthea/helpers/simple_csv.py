"""Java API skeleton: SimpleCSV.java."""

from __future__ import annotations

from collections.abc import Iterator


class SimpleCSV:
    """Java: SimpleCSV; pending T05."""

    def __init__(self) -> None:
        """Java: SimpleCSV#SimpleCSV.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: SimpleCSV#SimpleCSV — pending T05")

    @staticmethod
    def parse(csv_data: str, field_separator: str | None = None) -> list[dict[str, str]]:
        """Java: SimpleCSV#parse.

        Java overloads:
        (String csvData)
        (String csvData, char fieldSeparator)
        """
        raise NotImplementedError("Java: SimpleCSV#parse — pending T05")

    @staticmethod
    def parse_line_by_line(csv_data: str) -> Iterator[dict[str, str]]:
        """Java: SimpleCSV#parseLineByLine.

        Java overloads:
        (String csvData)
        """
        raise NotImplementedError("Java: SimpleCSV#parseLineByLine — pending T05")

    @staticmethod
    def unparse(data: list[dict[str, str]], separator: str | None = None) -> str:
        """Java: SimpleCSV#unparse.

        Java overloads:
        (List data)
        (List data, char separator)
        """
        raise NotImplementedError("Java: SimpleCSV#unparse — pending T05")

    @staticmethod
    def is_valid(csv_data: str, separator: str | None = None) -> bool:
        """Java: SimpleCSV#isValid.

        Java overloads:
        (String csvData)
        (String csvData, char separator)
        """
        raise NotImplementedError("Java: SimpleCSV#isValid — pending T05")
