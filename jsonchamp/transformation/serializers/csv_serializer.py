"""
CSV Output Serializer

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Serializes transformed dictionaries to CSV format.
Handles nested structures by flattening them with dot-notation headers.
"""

import csv
import io
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class CSVSerializer:
    """
    Serializes a list of dictionaries to CSV format.

    Nested dictionaries are flattened using a configurable separator
    so that ``{"contact": {"email": "a@b.com"}}`` becomes the header
    ``contact.email``.
    """

    def __init__(
        self,
        delimiter: str = ',',
        quotechar: str = '"',
        quoting: int = csv.QUOTE_MINIMAL,
        include_header: bool = True,
        columns: Optional[List[str]] = None,
        flatten_separator: str = '.',
        null_value: str = '',
        encoding: str = 'utf-8',
        line_ending: str = '\n',
        bool_true: str = 'true',
        bool_false: str = 'false'
    ):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.quoting = quoting
        self.include_header = include_header
        self.columns = columns
        self.flatten_separator = flatten_separator
        self.null_value = null_value
        self.encoding = encoding
        self.line_ending = line_ending
        self.bool_true = bool_true
        self.bool_false = bool_false

    def _flatten(self, obj: Any, prefix: str = '') -> Dict[str, Any]:
        """Flatten a nested dict into dot-notation keys."""
        items = {}
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{self.flatten_separator}{key}" if prefix else key
                if isinstance(value, dict):
                    items.update(self._flatten(value, new_key))
                elif isinstance(value, list):
                    items[new_key] = self._format_list(value)
                else:
                    items[new_key] = value
        return items

    def _format_list(self, lst: list) -> str:
        """Convert a list to a string for a CSV cell."""
        parts = []
        for item in lst:
            if item is None:
                parts.append(self.null_value)
            else:
                parts.append(str(item))
        return '; '.join(parts)

    def _format_value(self, value: Any) -> str:
        """Convert a value to its CSV cell string."""
        if value is None:
            return self.null_value
        if isinstance(value, bool):
            return self.bool_true if value else self.bool_false
        if isinstance(value, list):
            return self._format_list(value)
        return str(value)

    def _discover_columns(self, records: List[Dict]) -> List[str]:
        """Discover all unique flattened column names preserving insertion order."""
        if self.columns:
            return list(self.columns)
        seen = {}
        for record in records:
            flat = self._flatten(record)
            for key in flat:
                if key not in seen:
                    seen[key] = True
        return list(seen.keys())

    def serialize(self, data: Union[Dict, List[Dict]]) -> str:
        """Serialize dict or list of dicts to a CSV string."""
        records = data if isinstance(data, list) else [data]
        if not records:
            return ''
        columns = self._discover_columns(records)
        buf = io.StringIO()
        writer = csv.writer(
            buf, delimiter=self.delimiter, quotechar=self.quotechar,
            quoting=self.quoting, lineterminator=self.line_ending
        )
        if self.include_header:
            writer.writerow(columns)
        for record in records:
            flat = self._flatten(record)
            row = [self._format_value(flat.get(col)) for col in columns]
            writer.writerow(row)
        return buf.getvalue()

    def serialize_to_file(self, data: Union[Dict, List[Dict]], file_path: Union[str, Path]):
        """Serialize and write to file."""
        content = self.serialize(data)
        with open(file_path, 'w', encoding=self.encoding, newline='') as f:
            f.write(content)


def dict_to_csv(
    data: Union[Dict, List[Dict]],
    file_path: Union[str, Path] = None,
    **kwargs
) -> str:
    """
    Convenience function to serialize dicts to CSV.

    Args:
        data: Dictionary or list of dictionaries
        file_path: Optional output file path
        **kwargs: Arguments passed to CSVSerializer
    Returns:
        CSV string
    """
    serializer = CSVSerializer(**kwargs)
    if file_path:
        serializer.serialize_to_file(data, file_path)
    return serializer.serialize(data)
