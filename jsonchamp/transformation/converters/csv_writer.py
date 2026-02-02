"""
JSON to CSV Output Writer for SchemaMap Transformations

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Serializes transformed JSON dictionaries to CSV format.
Handles nested objects by flattening with configurable separators.
"""

import csv
import io
from typing import Dict, List, Any, Optional, Union, Sequence
from pathlib import Path
from collections import OrderedDict


class CSVWriter:
    """
    Writes JSON dictionaries to CSV format.
    
    Features:
    - Automatic header detection from data
    - Nested object flattening (dot-notation or custom separator)
    - Configurable delimiter, quoting, encoding
    - Explicit column ordering
    - Null value representation
    """
    
    def __init__(
        self,
        delimiter: str = ',',
        quotechar: str = '"',
        quoting: int = csv.QUOTE_MINIMAL,
        encoding: str = 'utf-8',
        line_terminator: str = '\r\n',
        flatten: bool = True,
        flatten_separator: str = '.',
        flatten_arrays: bool = False,
        array_separator: str = '|',
        columns: Optional[List[str]] = None,
        include_header: bool = True,
        null_value: str = '',
        bool_true: str = 'true',
        bool_false: str = 'false',
        date_format: Optional[str] = None
    ):
        """
        Initialize CSV writer.
        
        Args:
            delimiter: Field delimiter (default: ',')
            quotechar: Quote character (default: '"')
            quoting: CSV quoting strategy (default: QUOTE_MINIMAL)
            encoding: Output file encoding (default: 'utf-8')
            line_terminator: Line ending (default: '\\r\\n')
            flatten: Flatten nested objects (default: True)
            flatten_separator: Separator for flattened keys (default: '.')
            flatten_arrays: Flatten arrays using separator (default: False)
            array_separator: Separator for array values (default: '|')
            columns: Explicit column list and order (default: auto-detect)
            include_header: Write header row (default: True)
            null_value: String representation of null (default: '')
            bool_true: String for True values (default: 'true')
            bool_false: String for False values (default: 'false')
            date_format: Optional strftime format for date objects
        """
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.quoting = quoting
        self.encoding = encoding
        self.line_terminator = line_terminator
        self.flatten = flatten
        self.flatten_separator = flatten_separator
        self.flatten_arrays = flatten_arrays
        self.array_separator = array_separator
        self.columns = columns
        self.include_header = include_header
        self.null_value = null_value
        self.bool_true = bool_true
        self.bool_false = bool_false
        self.date_format = date_format
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten a nested dictionary using dot-notation keys."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and self.flatten:
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list) and self.flatten_arrays:
                items.append((new_key, self.array_separator.join(str(i) for i in v)))
            elif isinstance(v, list) and self.flatten:
                # For non-flattened arrays, convert to string
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _format_value(self, value: Any) -> str:
        """Format a single value for CSV output."""
        if value is None:
            return self.null_value
        if isinstance(value, bool):
            return self.bool_true if value else self.bool_false
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            if self.flatten_arrays:
                return self.array_separator.join(str(v) for v in value)
            return str(value)
        if isinstance(value, dict):
            return str(value)
        return str(value)
    
    def _detect_columns(self, records: List[Dict]) -> List[str]:
        """Detect all columns from a list of records, preserving order."""
        seen = OrderedDict()
        for record in records:
            if self.flatten:
                flat = self._flatten_dict(record, sep=self.flatten_separator)
            else:
                flat = record
            for key in flat:
                if key not in seen:
                    seen[key] = True
        return list(seen.keys())
    
    def _prepare_row(self, record: Dict, columns: List[str]) -> List[str]:
        """Prepare a single record as a list of formatted string values."""
        if self.flatten:
            flat = self._flatten_dict(record, sep=self.flatten_separator)
        else:
            flat = record
        
        return [self._format_value(flat.get(col)) for col in columns]
    
    def write_string(self, records: List[Dict]) -> str:
        """
        Write records to CSV string.
        
        Args:
            records: List of dictionaries to write
            
        Returns:
            CSV content as string
        """
        output = io.StringIO()
        self._write_to(records, output)
        return output.getvalue()
    
    def write_file(self, records: List[Dict], file_path: Union[str, Path]):
        """
        Write records to CSV file.
        
        Args:
            records: List of dictionaries to write
            file_path: Output file path
        """
        with open(file_path, 'w', encoding=self.encoding, newline='') as f:
            self._write_to(records, f)
    
    def _write_to(self, records: List[Dict], file_obj):
        """Internal method to write CSV to a file-like object."""
        if not records:
            return
        
        columns = self.columns or self._detect_columns(records)
        
        writer = csv.writer(
            file_obj,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=self.quoting,
            lineterminator=self.line_terminator
        )
        
        if self.include_header:
            writer.writerow(columns)
        
        for record in records:
            writer.writerow(self._prepare_row(record, columns))


class CSVWriterPresets:
    """Common CSV output format presets."""
    
    @staticmethod
    def standard() -> dict:
        """Standard CSV output."""
        return {
            'delimiter': ',',
            'quotechar': '"',
            'include_header': True,
            'flatten': True
        }
    
    @staticmethod
    def tsv() -> dict:
        """Tab-separated output."""
        return {
            'delimiter': '\t',
            'quotechar': '"',
            'include_header': True,
            'flatten': True
        }
    
    @staticmethod
    def pipe() -> dict:
        """Pipe-delimited output."""
        return {
            'delimiter': '|',
            'quotechar': '"',
            'include_header': True,
            'flatten': True
        }
    
    @staticmethod
    def excel() -> dict:
        """Excel-compatible CSV."""
        return {
            'delimiter': ',',
            'quotechar': '"',
            'quoting': csv.QUOTE_ALL,
            'encoding': 'utf-8-sig',
            'include_header': True,
            'flatten': True
        }
    
    @staticmethod
    def flat() -> dict:
        """Fully flattened output including arrays."""
        return {
            'delimiter': ',',
            'flatten': True,
            'flatten_arrays': True,
            'array_separator': '|',
            'include_header': True
        }
