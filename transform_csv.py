#!/usr/bin/env python3
"""
CSV Transformation Runner

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform CSV data using SchemaMap DSL.
Output can be JSON, CSV, or XML.

Usage:
    python transform_csv.py mapping.smap input.csv
    python transform_csv.py mapping.smap input.csv --output-format csv -o result.csv
    python transform_csv.py mapping.smap input.csv --output-format xml -o result.xml
    python transform_csv.py mapping.smap input.csv --delimiter ";" --no-header
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import load_mapping, validate_json_schema
from jsonchamp.transformation.converters import CSVConverter, CSVPresets
from jsonchamp.transformation.serializers import CSVSerializer, XMLSerializer
from jsonchamp import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Transform CSV data using SchemaMap DSL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CSV → JSON (default)
  %(prog)s mapping.smap customers.csv

  # CSV → CSV (re-map columns, compute fields)
  %(prog)s mapping.smap customers.csv -of csv -o customers_out.csv

  # CSV → XML
  %(prog)s mapping.smap customers.csv -of xml -o customers.xml

  # Custom delimiter (semicolon)
  %(prog)s mapping.smap data.csv --delimiter ";"

  # Tab-separated values
  %(prog)s mapping.smap data.tsv --delimiter "\\t"

  # Use preset format
  %(prog)s mapping.smap data.tsv --preset tsv

  # CSV → XML with custom tags
  %(prog)s mapping.smap data.csv -of xml --root-tag customers --record-tag customer
        """
    )

    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", help="Path to input CSV file")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")
    parser.add_argument("--schema", "-s", help="JSON Schema for output validation")

    # CSV input options
    csv_group = parser.add_argument_group("CSV Input Options")
    csv_group.add_argument("--delimiter", "-d", default=",",
                          help="Field delimiter (default: ',')")
    csv_group.add_argument("--quotechar", "-q", default='"',
                          help="Quote character (default: '\"')")
    csv_group.add_argument("--no-header", action="store_true",
                          help="CSV has no header row")
    csv_group.add_argument("--columns",
                          help="Column names (comma-separated, for --no-header)")
    csv_group.add_argument("--skip-rows", type=int, default=0,
                          help="Skip N rows at start")
    csv_group.add_argument("--encoding", default="utf-8",
                          help="File encoding (default: utf-8)")
    csv_group.add_argument("--no-infer-types", action="store_true",
                          help="Keep all values as strings")
    csv_group.add_argument("--no-strip", action="store_true",
                          help="Don't strip whitespace from values")
    csv_group.add_argument("--preset", choices=["excel", "tsv", "pipe", "semicolon"],
                          help="Use preset CSV format")

    # Output format
    out_fmt = parser.add_argument_group("Output Format")
    out_fmt.add_argument("--output-format", "-of",
                         choices=["json", "csv", "xml"], default="json",
                         help="Output format (default: json)")

    # JSON output options
    json_out = parser.add_argument_group("JSON Output Options")
    json_out.add_argument("--single", action="store_true",
                          help="Output single object (first row only)")
    json_out.add_argument("--wrap-array", action="store_true",
                          help="Wrap output in {\"records\": [...]} object")
    json_out.add_argument("--pretty", action="store_true", default=True,
                          help="Pretty-print JSON output (default)")
    json_out.add_argument("--compact", action="store_true",
                          help="Compact JSON output (no indentation)")

    # CSV output options
    csv_out = parser.add_argument_group("CSV Output Options")
    csv_out.add_argument("--out-delimiter", default=",",
                         help="Output CSV delimiter (default: ',')")
    csv_out.add_argument("--no-out-header", action="store_true",
                         help="Omit header row in CSV output")
    csv_out.add_argument("--out-columns",
                         help="Explicit output columns (comma-separated)")

    # XML output options
    xml_out = parser.add_argument_group("XML Output Options")
    xml_out.add_argument("--root-tag", default="root",
                         help="XML root element tag (default: 'root')")
    xml_out.add_argument("--record-tag", default="record",
                         help="XML record element tag (default: 'record')")
    xml_out.add_argument("--no-xml-declaration", action="store_true",
                         help="Omit <?xml?> declaration")

    # General options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress status messages")
    parser.add_argument("--version", action="version",
                       version=f"%(prog)s {__version__}")

    args = parser.parse_args()
    
    # Validate files exist
    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
        sys.exit(1)
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Build CSV options
        if args.preset:
            preset_func = getattr(CSVPresets, args.preset)
            csv_options = preset_func()
        else:
            csv_options = {}
        
        # Override with explicit options
        csv_options['delimiter'] = args.delimiter.encode().decode('unicode_escape')  # Handle \t
        csv_options['quotechar'] = args.quotechar
        csv_options['has_header'] = not args.no_header
        csv_options['skip_rows'] = args.skip_rows
        csv_options['encoding'] = args.encoding
        csv_options['infer_types'] = not args.no_infer_types
        csv_options['strip_whitespace'] = not args.no_strip
        
        if args.columns:
            csv_options['column_names'] = [c.strip() for c in args.columns.split(',')]
        
        # Convert CSV to JSON
        if args.verbose:
            print(f"Reading CSV: {args.input}")
            print(f"  Delimiter: {repr(csv_options['delimiter'])}")
            print(f"  Has header: {csv_options['has_header']}")
        
        converter = CSVConverter(**csv_options)
        records = list(converter.iterate_file(input_path))
        
        if args.verbose:
            print(f"  Records found: {len(records)}")
        
        if not records:
            print("Warning: No records found in CSV file", file=sys.stderr)
            sys.exit(0)
        
        # Load transformer
        if args.verbose:
            print(f"Loading mapping: {args.mapping}")
        
        transformer = load_mapping(str(mapping_path))
        
        # Register external functions
        if args.functions:
            func_path = Path(args.functions)
            if func_path.exists():
                transformer.register_file(str(func_path))
                if args.verbose:
                    print(f"Loaded functions from: {args.functions}")
            else:
                print(f"Warning: Functions file not found: {args.functions}", 
                      file=sys.stderr)
        
        # Transform records
        if args.verbose:
            print("Transforming records...")
        
        if args.single:
            results = transformer.transform(records[0])
        else:
            results = [transformer.transform(record) for record in records]
        
        # Wrap in object if requested
        if args.wrap_array and not args.single:
            results = {"records": results, "count": len(results)}
        
        # Validate if schema provided
        if args.schema:
            schema_path = Path(args.schema)
            if schema_path.exists():
                if isinstance(results, list):
                    for i, result in enumerate(results):
                        validate_json_schema(result, str(schema_path))
                else:
                    validate_json_schema(results, str(schema_path))
                if args.verbose:
                    print("✓ Schema validation passed")
        
        # Output in requested format
        out_fmt = args.output_format

        if out_fmt == 'json':
            indent = None if args.compact else 2
            output_text = json.dumps(results, indent=indent, default=str)
        elif out_fmt == 'csv':
            csv_out_opts = {
                'delimiter': args.out_delimiter,
                'include_header': not args.no_out_header,
            }
            if args.out_columns:
                csv_out_opts['columns'] = [c.strip() for c in args.out_columns.split(',')]
            serializer = CSVSerializer(**csv_out_opts)
            data_for_csv = results if isinstance(results, list) else [results]
            output_text = serializer.serialize(data_for_csv)
        elif out_fmt == 'xml':
            xml_opts = {
                'root_tag': args.root_tag,
                'record_tag': args.record_tag,
                'xml_declaration': not args.no_xml_declaration,
            }
            serializer = XMLSerializer(**xml_opts)
            data_for_xml = results if isinstance(results, list) else [results]
            output_text = serializer.serialize(data_for_xml)
        else:
            output_text = json.dumps(results, indent=2, default=str)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            if not args.quiet:
                count = len(results) if isinstance(results, list) else 1
                print(f"✓ Transformed {count} record(s) → {out_fmt.upper()}: {args.output}")
        else:
            print(output_text)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
