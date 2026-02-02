"""
JSON Output Serializer

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Serializes transformed dictionaries to JSON format.
"""

import json
from typing import Dict, List, Any, Union
from pathlib import Path


class JSONSerializer:
    """
    Serializes dictionaries to JSON.

    Options:
        indent: Number of spaces for indentation (None for compact)
        sort_keys: Sort keys alphabetically
        ensure_ascii: Escape non-ASCII characters
        wrap_key: Wrap output list in an object under this key
    """

    def __init__(
        self,
        indent: int = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        wrap_key: str = None,
        encoding: str = 'utf-8'
    ):
        self.indent = indent
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        self.wrap_key = wrap_key
        self.encoding = encoding

    def serialize(self, data: Union[Dict, List[Dict]]) -> str:
        """Serialize dict or list of dicts to JSON string."""
        output = self._wrap(data)
        return json.dumps(
            output, indent=self.indent,
            sort_keys=self.sort_keys,
            ensure_ascii=self.ensure_ascii,
            default=str
        )

    def serialize_to_file(self, data: Union[Dict, List[Dict]], file_path: Union[str, Path]):
        """Serialize and write to file."""
        content = self.serialize(data)
        with open(file_path, 'w', encoding=self.encoding) as f:
            f.write(content)

    def _wrap(self, data):
        if self.wrap_key and isinstance(data, list):
            return {self.wrap_key: data, "count": len(data)}
        return data


def dict_to_json(
    data: Union[Dict, List[Dict]],
    file_path: Union[str, Path] = None,
    **kwargs
) -> str:
    """
    Convenience function to serialize dicts to JSON.

    Args:
        data: Dictionary or list of dictionaries
        file_path: Optional output file path
        **kwargs: Arguments passed to JSONSerializer

    Returns:
        JSON string
    """
    serializer = JSONSerializer(**kwargs)
    if file_path:
        serializer.serialize_to_file(data, file_path)
    return serializer.serialize(data)
