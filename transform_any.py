#!/usr/bin/env python3
"""
Universal Data Transformation Pipeline

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform data from any supported input format (JSON, CSV, XML, FLR) to any
supported output format (JSON, CSV, XML) using SchemaMap DSL.

Pipeline:  INPUT (any format) --> JSON dicts --> SchemaMap transform --> OUTPUT (any format)

Usage:
    # CSV to JSON
    python transform_any.py mapping.smap input.csv --input-format csv --output-format json

    # CSV to CSV  (transform columns/rename/filter)
    python transform_any.py mapping.smap input.csv --input-format csv --output-format csv

    # CSV to XML
    python transform_any.py mapping.smap input.csv --input-format csv --output-format xml

    # JSON to CSV
    python transform_any.py mapping.smap input.json --input-format json --output-format csv

    # XML to CSV
    python transform_any.py mapping.smap input.xml --input-format xml --output-format csv

    # FLR to XML
    python transform_any.py mapping.smap data.dat --input-format flr --output-format xml --layout layout.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Union

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import (
    load_mapping, validate_json_schema, SchemaMapParser,
    CSVConverter, CSVPresets, csv_to_json,
    XMLConverter, XMLPresets, xml_to_json, xml_to_json_records,
    FLRConverter, FLRPresets, RecordLayout, flr_to_json,
)
from jsonchamp.transformation.converters.csv_writer import CSVWriter, CSVWriterPresets
from jsonchamp.transformation.converters.xml_writer import XMLWriter, XMLWriterPresets
from jsonchamp.transformation.compiler.python_gen import PythonCodeGenerator
from jsonchamp import __version__


# ---------------------------------------------------------------------------
# Input readers
# ---------------------------------------------------------------------------

def read_json_input(path: str, batch: bool = False) -> List[Dict]:
    """Read JSON file and return list of records."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return [data]


def read_csv_input(path: str, args) -> List[Dict]:
    """Read CSV file and return list of records."""
    opts = {}
    if args.in_preset:
        opts = getattr(CSVPresets, args.in_preset)()
    if args.in_delimiter:
        opts['delimiter'] = args.in_delimiter.encode().decode('unicode_escape')
    if args.in_encoding:
        opts['encoding'] = args.in_encoding
    if args.in_no_header:
        opts['has_header'] = False
    if args.in_columns:
        opts['column_names'] = [c.strip() for c in args.in_columns.split(',')]
    if args.in_skip_rows:
        opts['skip_rows'] = args.in_skip_rows
    
    converter = CSVConverter(**opts)
    return list(converter.iterate_file(path))


def read_xml_input(path: str, args) -> List[Dict]:
    """Read XML file and return list of records."""
    opts = {}
    if args.in_preset:
        opts = getattr(XMLPresets, args.in_preset)()
    if args.in_strip_ns:
        opts['strip_namespaces'] = True
    if args.in_no_root:
        opts['preserve_root'] = False

    converter = XMLConverter(**opts)

    if args.in_records:
        return converter.convert_file_elements(path, args.in_records)
    else:
        return [converter.convert_file(path)]


def read_flr_input(path: str, args) -> List[Dict]:
    """Read FLR file and return list of records."""
    if not args.layout:
        print("Error: --layout is required for FLR input", file=sys.stderr)
        sys.exit(1)
    
    layout_path = Path(args.layout)
    if not layout_path.exists():
        print(f"Error: Layout file not found: {args.layout}", file=sys.stderr)
        sys.exit(1)
    
    if layout_path.suffix.lower() == '.json':
        layout = RecordLayout.from_json_file(layout_path)
    else:
        layout = RecordLayout.from_simple_format(layout_path)
    
    opts = {}
    if args.in_encoding:
        opts['encoding'] = args.in_encoding
    if args.in_skip_header:
        opts['header_lines'] = args.in_skip_header
    if args.in_skip_footer:
        opts['footer_lines'] = args.in_skip_footer
    
    converter = FLRConverter(layout=layout, **opts)
    return list(converter.iterate_file(path))


INPUT_READERS = {
    'json': read_json_input,
    'csv':  read_csv_input,
    'xml':  read_xml_input,
    'flr':  read_flr_input,
}


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_json_output(records: List[Dict], path: str, args):
    """Write records as JSON."""
    indent = None if args.compact else 2
    if len(records) == 1 and not args.force_array:
        payload = records[0]
    else:
        if args.wrap_key:
            payload = {args.wrap_key: records, "count": len(records)}
        else:
            payload = records
    
    content = json.dumps(payload, indent=indent, default=str, ensure_ascii=False)
    
    if path:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(content)


def write_csv_output(records: List[Dict], path: str, args):
    """Write records as CSV."""
    opts = {}
    if args.out_preset:
        opts = getattr(CSVWriterPresets, args.out_preset)()
    if args.out_delimiter:
        opts['delimiter'] = args.out_delimiter.encode().decode('unicode_escape')
    if args.out_no_header:
        opts['include_header'] = False
    if args.out_columns:
        opts['columns'] = [c.strip() for c in args.out_columns.split(',')]
    if args.out_flatten_arrays:
        opts['flatten_arrays'] = True
    
    writer = CSVWriter(**opts)
    if path:
        writer.write_file(records, path)
    else:
        print(writer.write_string(records), end='')


def write_xml_output(records: List[Dict], path: str, args):
    """Write records as XML."""
    opts = {}
    if args.out_preset:
        opts = getattr(XMLWriterPresets, args.out_preset)()
    if args.out_root:
        opts['root_element'] = args.out_root
    if args.out_record:
        opts['record_element'] = args.out_record
    if args.out_no_declaration:
        opts['xml_declaration'] = False
    if args.compact:
        opts['pretty_print'] = False
    if len(records) == 1 and not args.force_array:
        opts['single_record_mode'] = True
    
    writer = XMLWriter(**opts)
    if path:
        writer.write_file(records, path)
    else:
        print(writer.write_string(records), end='')


OUTPUT_WRITERS = {
    'json': write_json_output,
    'csv':  write_csv_output,
    'xml':  write_xml_output,
}


# ---------------------------------------------------------------------------
# Format inference from file extension
# ---------------------------------------------------------------------------

INPUT_EXT_MAP = {
    '.json': 'json',
    '.csv': 'csv', '.tsv': 'csv', '.txt': 'csv',
    '.xml': 'xml', '.soap': 'xml',
    '.dat': 'flr', '.flr': 'flr', '.fixed': 'flr',
}

OUTPUT_EXT_MAP = {
    '.json': 'json',
    '.csv': 'csv', '.tsv': 'csv',
    '.xml': 'xml',
}


def infer_format(file_path: str, ext_map: dict, kind: str) -> str:
    """Infer format from file extension."""
    ext = Path(file_path).suffix.lower()
    fmt = ext_map.get(ext)
    if not fmt:
        print(f"Warning: Cannot infer {kind} format from extension '{ext}'. "
              f"Defaulting to 'json'. Use --{kind}-format to specify.", file=sys.stderr)
        return 'json'
    return fmt


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog='transform_any.py',
        description="Universal data transformation: any input format → SchemaMap → any output format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported Format Combinations:
  Input:  json, csv, xml, flr
  Output: json, csv, xml

Formats are auto-detected from file extensions (.json, .csv, .xml, .dat, etc.)
or can be specified explicitly with --input-format / --output-format.

Examples:
  # CSV → JSON
  %(prog)s mapping.smap customers.csv -o customers.json

  # CSV → CSV (restructure / rename columns)
  %(prog)s mapping.smap legacy.csv -o modern.csv

  # CSV → XML
  %(prog)s mapping.smap customers.csv -o customers.xml

  # JSON → CSV
  %(prog)s mapping.smap orders.json -o orders.csv

  # XML → CSV
  %(prog)s mapping.smap orders.xml --in-records order -o orders.csv

  # FLR → JSON (mainframe data)
  %(prog)s mapping.smap mainframe.dat --layout layout.json -o output.json

  # FLR → CSV
  %(prog)s mapping.smap data.dat --layout layout.json -o data.csv

  # Explicit formats (override auto-detection)
  %(prog)s mapping.smap data.txt --input-format csv --output-format xml -o out.xml

  # Compiled transformer (5-10x faster)
  %(prog)s mapping.smap data.csv -o out.json --compiled

  # Custom CSV delimiters for input and output
  %(prog)s mapping.smap data.csv -o out.csv --in-delimiter ";" --out-delimiter "|"

  # Custom XML element names
  %(prog)s mapping.smap data.csv -o out.xml --out-root "customers" --out-record "customer"
        """
    )
    
    # Positional arguments
    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", help="Path to input data file")
    parser.add_argument("--output", "-o", help="Output path (format inferred from extension)")
    
    # Format selection
    fmt_group = parser.add_argument_group("Format Selection")
    fmt_group.add_argument("--input-format", "-I",
                          choices=['json', 'csv', 'xml', 'flr'],
                          help="Input format (auto-detected from extension)")
    fmt_group.add_argument("--output-format", "-O",
                          choices=['json', 'csv', 'xml'],
                          help="Output format (auto-detected from extension)")
    
    # Transformer options
    xfm_group = parser.add_argument_group("Transformer Options")
    xfm_group.add_argument("--compiled", "-c", action="store_true",
                          help="Use compiled transformer (5-10x faster)")
    xfm_group.add_argument("--functions", "-f", help="Python file with custom functions")
    xfm_group.add_argument("--schema", "-s", help="JSON Schema for output validation")
    
    # Input: CSV options
    in_csv = parser.add_argument_group("Input CSV Options")
    in_csv.add_argument("--in-delimiter", help="Input CSV delimiter (default: ',')")
    in_csv.add_argument("--in-no-header", action="store_true", help="Input CSV has no header")
    in_csv.add_argument("--in-columns", help="Input column names (comma-separated, for --in-no-header)")
    in_csv.add_argument("--in-skip-rows", type=int, default=0, help="Skip N rows at start of input")
    in_csv.add_argument("--in-preset", help="Input CSV preset (excel, tsv, pipe, semicolon)")
    in_csv.add_argument("--in-encoding", help="Input file encoding")
    
    # Input: XML options
    in_xml = parser.add_argument_group("Input XML Options")
    in_xml.add_argument("--in-records", help="XPath to record elements in input XML")
    in_xml.add_argument("--in-strip-ns", action="store_true", help="Strip namespaces from input XML")
    in_xml.add_argument("--in-no-root", action="store_true", help="Don't preserve root in input XML")
    
    # Input: FLR options
    in_flr = parser.add_argument_group("Input FLR Options")
    in_flr.add_argument("--layout", "-l", help="FLR layout file (JSON or text)")
    in_flr.add_argument("--in-skip-header", type=int, default=0, help="Skip N header lines in FLR")
    in_flr.add_argument("--in-skip-footer", type=int, default=0, help="Skip N footer lines in FLR")
    
    # Output: JSON options
    out_json = parser.add_argument_group("Output JSON Options")
    out_json.add_argument("--compact", action="store_true", help="Compact JSON / no XML indent")
    out_json.add_argument("--force-array", action="store_true",
                         help="Always output array even for single record")
    out_json.add_argument("--wrap-key", help='Wrap array in object with this key (e.g. "records")')
    
    # Output: CSV options
    out_csv = parser.add_argument_group("Output CSV Options")
    out_csv.add_argument("--out-delimiter", help="Output CSV delimiter (default: ',')")
    out_csv.add_argument("--out-no-header", action="store_true", help="Omit header in output CSV")
    out_csv.add_argument("--out-columns", help="Output CSV column list and order (comma-separated)")
    out_csv.add_argument("--out-flatten-arrays", action="store_true",
                        help="Flatten arrays using pipe in output CSV")
    out_csv.add_argument("--out-preset", help="Output CSV preset (standard, tsv, pipe, excel, flat)")
    
    # Output: XML options
    out_xml = parser.add_argument_group("Output XML Options")
    out_xml.add_argument("--out-root", help='Root element name (default: "records")')
    out_xml.add_argument("--out-record", help='Record element name (default: "record")')
    out_xml.add_argument("--out-no-declaration", action="store_true",
                        help="Omit XML declaration")
    out_xml.add_argument("--out-preset", help="Output XML preset (standard, data_feed, compact)")
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress status messages")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    # ------- validation -------
    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
        sys.exit(1)
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Infer formats
    in_fmt = args.input_format or infer_format(args.input, INPUT_EXT_MAP, 'input')
    if args.output:
        out_fmt = args.output_format or infer_format(args.output, OUTPUT_EXT_MAP, 'output')
    else:
        out_fmt = args.output_format or 'json'
    
    if in_fmt not in INPUT_READERS:
        print(f"Error: Unsupported input format: {in_fmt}", file=sys.stderr)
        sys.exit(1)
    if out_fmt not in OUTPUT_WRITERS:
        print(f"Error: Unsupported output format: {out_fmt}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # ----- STEP 1: Read input -----
        if args.verbose:
            print(f"[1] Reading {in_fmt.upper()} input: {args.input}")
        
        reader = INPUT_READERS[in_fmt]
        if in_fmt == 'json':
            records = reader(str(input_path))
        else:
            records = reader(str(input_path), args)
        
        if args.verbose:
            print(f"    Records loaded: {len(records)}")
        
        if not records:
            print("Warning: No records found in input file", file=sys.stderr)
            sys.exit(0)
        
        # ----- STEP 2: Create transformer -----
        if args.verbose:
            mode = "compiled" if args.compiled else "interpreted"
            print(f"[2] Loading SchemaMap transformer ({mode}): {args.mapping}")
        
        if args.compiled:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                content = f.read()
            sparser = SchemaMapParser()
            mapping_file = sparser.parse(content, filename=str(mapping_path))
            generator = PythonCodeGenerator(class_name="CompiledTransformer")
            code = generator.generate(mapping_file)
            exec_globals = {}
            exec(code, exec_globals)
            transformer = exec_globals["CompiledTransformer"]()
        else:
            transformer = load_mapping(str(mapping_path))
        
        # Register external functions
        if args.functions:
            func_path = Path(args.functions)
            if func_path.exists():
                transformer.register_file(str(func_path))
                if args.verbose:
                    print(f"    Loaded functions: {args.functions}")
        
        # ----- STEP 3: Transform -----
        if args.verbose:
            print(f"[3] Transforming {len(records)} record(s)...")
        
        transformed = [transformer.transform(rec) for rec in records]
        
        if args.verbose:
            print(f"    Transformation complete")
        
        # ----- STEP 4: Validate (optional) -----
        if args.schema:
            schema_path = Path(args.schema)
            if schema_path.exists():
                for rec in transformed:
                    validate_json_schema(rec, str(schema_path))
                if args.verbose:
                    print(f"[4] Schema validation passed ✓")
        
        # ----- STEP 5: Write output -----
        if args.verbose:
            target = args.output or "stdout"
            print(f"[5] Writing {out_fmt.upper()} output: {target}")
        
        writer = OUTPUT_WRITERS[out_fmt]
        writer(transformed, args.output, args)
        
        if not args.quiet and args.output:
            print(f"✓ Transformed {len(transformed)} record(s): "
                  f"{in_fmt.upper()} → {out_fmt.upper()} → {args.output}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
