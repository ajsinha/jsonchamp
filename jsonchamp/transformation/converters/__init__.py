"""
Data Format Converters for SchemaMap

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Provides converters to transform various data formats (CSV, XML, FLR) to JSON
for processing by the SchemaMap transformation engine.
"""

from .csv_converter import (
    CSVConverter,
    CSVPresets,
    csv_to_json
)

from .xml_converter import (
    XMLConverter,
    XMLPresets,
    xml_to_json,
    xml_to_json_records
)

from .flr_converter import (
    FLRConverter,
    FLRPresets,
    RecordLayout,
    FieldDefinition,
    flr_to_json
)

__all__ = [
    # CSV Input
    'CSVConverter',
    'CSVPresets',
    'csv_to_json',

    # XML Input
    'XMLConverter',
    'XMLPresets',
    'xml_to_json',
    'xml_to_json_records',

    # FLR Input
    'FLRConverter',
    'FLRPresets',
    'RecordLayout',
    'FieldDefinition',
    'flr_to_json',
]
