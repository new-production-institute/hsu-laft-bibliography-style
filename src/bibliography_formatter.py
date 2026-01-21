#!/usr/bin/env python3
"""
Bibliography Formatter CLI

Transforms bibliography entries from:
    [2025] 1. Author (2025) Title...
    [2024] 2. Author (2024) Title...

To year-grouped format:
    2025
    1. Author (2025) Title...

    2024
    1. Author (2024) Title...
"""

import argparse
import re
import sys
from typing import Optional


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Format bibliography entries with year headers and reset numbering.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.txt                    Read from file, print to stdout
  %(prog)s input.txt -o output.txt      Read from file, write to file
  %(prog)s -                            Read from stdin, print to stdout
  cat bib.txt | %(prog)s -              Pipe input
        """,
    )
    parser.add_argument(
        "input",
        help="Input file path or '-' for stdin",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)",
        default=None,
    )
    return parser


def read_from_stdin() -> str:
    """Read all content from standard input."""
    return sys.stdin.read()


def read_from_file(filepath: str) -> str:
    """Read all content from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def read_input(source: str) -> str:
    """Read input from file or stdin based on source argument."""
    if source == "-":
        return read_from_stdin()
    return read_from_file(source)


def write_to_file(filepath: str, content: str) -> None:
    """Write content to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def write_output(destination: Optional[str], content: str) -> None:
    """Write content to file or stdout based on destination."""
    if destination is None:
        print(content)
    else:
        write_to_file(destination, content)


def extract_year_and_content(line: str) -> Optional[tuple[str, str]]:
    """
    Extract year and entry content from a bibliography line.
    
    Returns None if line doesn't match expected format.
    """
    pattern = r"^\[(\d{4})\]\s*\d+\.\s*(.+)$"
    match = re.match(pattern, line.strip())
    if match:
        return (match.group(1), match.group(2))
    return None


def split_into_lines(text: str) -> list[str]:
    """Split text into non-empty lines."""
    return [line for line in text.strip().split("\n") if line.strip()]


def parse_entries(lines: list[str]) -> list[tuple[str, str]]:
    """Parse lines into list of (year, content) tuples."""
    entries = []
    for line in lines:
        parsed = extract_year_and_content(line)
        if parsed:
            entries.append(parsed)
    return entries


def group_by_year(entries: list[tuple[str, str]]) -> dict[str, list[str]]:
    """Group entry contents by year."""
    groups: dict[str, list[str]] = {}
    for year, content in entries:
        if year not in groups:
            groups[year] = []
        groups[year].append(content)
    return groups


def sort_years_descending(years: list[str]) -> list[str]:
    """Sort year strings in descending order."""
    return sorted(years, reverse=True)


def format_year_section(year: str, entries: list[str]) -> str:
    """Format a single year section with header and numbered entries."""
    lines = [year]
    for i, entry in enumerate(entries, start=1):
        lines.append(f"{i}. {entry}")
    return "\n".join(lines)


def format_all_sections(groups: dict[str, list[str]]) -> str:
    """Format all year sections into final output."""
    sorted_years = sort_years_descending(list(groups.keys()))
    sections = [format_year_section(year, groups[year]) for year in sorted_years]
    return "\n\n".join(sections)


def process_bibliography(text: str) -> str:
    """Main processing pipeline: text -> formatted bibliography."""
    lines = split_into_lines(text)
    entries = parse_entries(lines)
    groups = group_by_year(entries)
    return format_all_sections(groups)


def main() -> int:
    """CLI entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        input_text = read_input(args.input)
        result = process_bibliography(input_text)
        write_output(args.output, result)
        return 0
    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e.filename}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
