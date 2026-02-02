#!/usr/bin/env python3
"""
Unified Transformation Pipeline CLI

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Transform data from any supported input format to any supported output format
using SchemaMap DSL.

  Input formats : JSON, CSV, XML, FLR (Fixed Length Record), Dict
  Output formats: JSON, CSV, XML

Usage:
    python transform_pipeline.py mapping.smap input.csv --input-format csv --output-format json
    python transform_pipeline.py mapping.smap input.csv -if csv -of xml -o result.xml
    python transform_pipeline.py mapping.smap input.dat -if flr --layout layout.json -of csv
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsonchamp.transformation import TransformPipeline
from jsonchamp import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Transform data between formats using SchemaMap DSL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CSV → JSON (default output)
  %(prog)s mapping.smap customers.csv -if csv

  # CSV → CSV  (re-map columns, rename, compute fields)
  %(prog)s mapping.smap customers.csv -if csv -of csv -o output.csv

  # CSV → XML
  %(prog)s mapping.smap customers.csv -if csv -of xml -o output.xml

  # JSON → CSV
  %(prog)s mapping.smap data.json -if json -of csv

  # XML → CSV
  %(prog)s mapping.smap orders.xml -if xml --records "order" -of csv

  # FLR → JSON
  %(prog)s mapping.smap data.dat -if flr --layout layout.json

  # FLR → XML
  %(prog)s mapping.smap data.dat -if flr --layout layout.json -of xml

  # Inline JSON → CSV
  %(prog)s mapping.smap --data '[{"name":"A"},{"name":"B"}]' -of csv

  # With compiled transformer (5-10x faster)
  %(prog)s mapping.smap input.csv -if csv -of xml --compiled

  # With custom delimiter for CSV input
  %(prog)s mapping.smap data.tsv -if csv --delimiter $'\\t' -of json

  # With custom XML output options
  %(prog)s mapping.smap data.csv -if csv -of xml --root-tag customers --record-tag customer
        """
    )

    parser.add_argument("mapping", help="Path to SchemaMap DSL file (.smap)")
    parser.add_argument("input", nargs="?", help="Path to input file")
    parser.add_argument("--data", "-d", help="Inline JSON data (instead of input file)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--functions", "-f", help="Python file with custom functions")

    # Format selection
    fmt = parser.add_argument_group("Format Options")
    fmt.add_argument("--input-format", "-if",
                     choices=["json", "csv", "xml", "flr"],
                     default="json",
                     help="Input format (default: json)")
    fmt.add_argument("--output-format", "-of",
                     choices=["json", "csv", "xml"],
                     default="json",
                     help="Output format (default: json)")

    # CSV input options
    csv_in = parser.add_argument_group("CSV Input Options")
    csv_in.add_argument("--delimiter", default=",",
                        help="CSV delimiter (default: ',')")
    csv_in.add_argument("--quotechar", default='"',
                        help="CSV quote character (default: '\"')")
    csv_in.add_argument("--no-header", action="store_true",
                        help="CSV has no header row")
    csv_in.add_argument("--encoding", default="utf-8",
                        help="Input file encoding (default: utf-8)")

    # XML input options
    xml_in = parser.add_argument_group("XML Input Options")
    xml_in.add_argument("--records", "-r",
                        help="XPath to repeating record elements")
    xml_in.add_argument("--strip-namespaces", action="store_true",
                        help="Remove namespace prefixes from XML")

    # FLR input options
    flr_in = parser.add_argument_group("FLR Input Options")
    flr_in.add_argument("--layout", "-l",
                        help="Path to FLR layout file (JSON or text)")
    flr_in.add_argument("--skip-header", type=int, default=0,
                        help="Number of FLR header lines to skip")
    flr_in.add_argument("--skip-footer", type=int, default=0,
                        help="Number of FLR footer lines to skip")

    # CSV output options
    csv_out = parser.add_argument_group("CSV Output Options")
    csv_out.add_argument("--out-delimiter", default=",",
                         help="Output CSV delimiter (default: ',')")
    csv_out.add_argument("--no-out-header", action="store_true",
                         help="Omit header row in CSV output")
    csv_out.add_argument("--columns",
                         help="Comma-separated list of output columns (for CSV output)")
    csv_out.add_argument("--flatten-sep", default=".",
                         help="Separator for flattening nested keys (default: '.')")

    # XML output options
    xml_out = parser.add_argument_group("XML Output Options")
    xml_out.add_argument("--root-tag", default="root",
                         help="XML root element tag (default: 'root')")
    xml_out.add_argument("--record-tag", default="record",
                         help="XML record element tag (default: 'record')")
    xml_out.add_argument("--no-xml-declaration", action="store_true",
                         help="Omit <?xml?> declaration")

    # JSON output options
    json_out = parser.add_argument_group("JSON Output Options")
    json_out.add_argument("--compact", action="store_true",
                          help="Compact JSON output (no indentation)")
    json_out.add_argument("--wrap-key",
                          help="Wrap JSON array in object under this key")

    # General options
    gen = parser.add_argument_group("General Options")
    gen.add_argument("--compiled", "-c", action="store_true",
                     help="Use compiled transformer (5-10x faster)")
    gen.add_argument("--verbose", "-v", action="store_true",
                     help="Verbose output")
    gen.add_argument("--quiet", action="store_true",
                     help="Suppress status messages")
    gen.add_argument("--version", action="version",
                     version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    # Validate
    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
        sys.exit(1)

    if not args.data and not args.input:
        print("Error: Either --data or an input file is required", file=sys.stderr)
        sys.exit(1)

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

    if args.input_format == "flr" and not args.layout:
        print("Error: --layout is required for FLR input", file=sys.stderr)
        sys.exit(1)

    try:
        # Build input options
        input_options = {}
        if args.input_format == "csv":
            input_options['delimiter'] = args.delimiter
            input_options['quotechar'] = args.quotechar
            input_options['encoding'] = args.encoding
            if args.no_header:
                input_options['has_header'] = False
        elif args.input_format == "xml":
            input_options['encoding'] = args.encoding
            if args.strip_namespaces:
                input_options['strip_namespaces'] = True
        elif args.input_format == "flr":
            input_options['encoding'] = args.encoding
            input_options['header_lines'] = args.skip_header
            input_options['footer_lines'] = args.skip_footer

        # Build output options
        output_options = {}
        if args.output_format == "csv":
            output_options['delimiter'] = args.out_delimiter
            output_options['include_header'] = not args.no_out_header
            output_options['flatten_separator'] = args.flatten_sep
            if args.columns:
                output_options['columns'] = [c.strip() for c in args.columns.split(',')]
        elif args.output_format == "xml":
            output_options['root_tag'] = args.root_tag
            output_options['record_tag'] = args.record_tag
            output_options['xml_declaration'] = not args.no_xml_declaration
        elif args.output_format == "json":
            output_options['indent'] = None if args.compact else 2
            if args.wrap_key:
                output_options['wrap_key'] = args.wrap_key

        # Load external functions
        functions = None
        if args.functions:
            func_path = Path(args.functions)
            if func_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("custom_functions", str(func_path))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                functions = {name: getattr(mod, name)
                             for name in dir(mod)
                             if not name.startswith('_') and callable(getattr(mod, name))}
                if args.verbose:
                    print(f"Loaded {len(functions)} functions from {args.functions}")
            else:
                print(f"Warning: Functions file not found: {args.functions}",
                      file=sys.stderr)

        # Build pipeline
        pipeline = TransformPipeline(
            mapping_file=str(mapping_path),
            input_format=args.input_format if not args.data else "dict",
            output_format=args.output_format,
            input_options=input_options,
            output_options=output_options,
            layout=args.layout,
            element_path=args.records,
            functions=functions,
            compiled=args.compiled,
        )

        if args.verbose:
            mode = "compiled" if args.compiled else "interpreted"
            print(f"Pipeline: {args.input_format.upper()} → SchemaMap ({mode}) → {args.output_format.upper()}")

        # Run
        if args.data:
            source_data = json.loads(args.data)
            output = pipeline.run_data(source_data)
        else:
            output = pipeline.run(str(input_path))

        # Serialize JSON lists for file/stdout output
        if isinstance(output, (dict, list)):
            indent = None if args.compact else 2
            output_text = json.dumps(output, indent=indent, default=str)
        else:
            output_text = output

        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            if not args.quiet:
                print(f"✓ Output written to: {args.output}")
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
