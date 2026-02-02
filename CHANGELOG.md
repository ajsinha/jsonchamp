
## [1.4.1] - 2026-01-30

### Added
- Comprehensive Word document: SchemaMap_Showcase_Complete_Guide.docx
- Complete documentation for Simple Showcase and E-Commerce examples
- Field-by-field analysis with transformation explanations
- Custom function documentation with signatures and examples
- Performance benchmarks and best practices guide
- Troubleshooting section with common errors and solutions

### Documentation
- 30+ page comprehensive guide covering all SchemaMap features
- Step-by-step transformation breakdowns
- Code examples with expected inputs and outputs

## [1.4.2] - 2026-01-30

### Added
- SHOWCASE_EXAMPLES.md: Comprehensive Markdown documentation for showcase examples
- Enhanced SCHEMAMAP.md with complete syntax reference covering all supported features

### Documentation
- Complete syntax reference with all operators, directives, and functions
- Field-by-field transformation explanations
- Path notation reference (arrays, nested, optional fields)
- All transform functions with examples
- Quick reference card for rapid lookup

### Changed
- Removed Word document format in favor of Markdown for better version control
- Version updated to 1.4.2

## [1.5.0] - 2026-01-30

### Changed
- **Project Renamed**: jsontools → jsonchamp
- All module imports updated to use jsonchamp
- CLI commands now use jsonchamp prefix
- Package name updated across all configuration files

### Documentation
- Updated all documentation to reflect new name
- Updated code examples with new import paths

## [1.6.0] - 2026-01-30

### Added
- **CSV Support**: Transform CSV files using SchemaMap DSL
  - New `transform_csv.py` main script
  - CSVConverter class with full options (delimiter, encoding, type inference)
  - CSVPresets for common formats (excel, tsv, pipe, semicolon)
  - Batch transformation of CSV records
  
- **XML Support**: Transform XML files using SchemaMap DSL
  - New `transform_xml.py` main script
  - XMLConverter class with full options (attribute prefix, namespaces, arrays)
  - XMLPresets for common formats (standard, soap, data_records)
  - Support for extracting multiple records from XML
  - Automatic handling of XML attributes (@attr) and text content (#text)

- **Converter Module**: `jsonchamp.transformation.converters`
  - `csv_to_json()` - Convert CSV to JSON
  - `xml_to_json()` - Convert XML to JSON
  - `xml_to_json_records()` - Extract records from XML
  - `transform_csv()` - One-step CSV transformation
  - `transform_xml()` - One-step XML transformation

### Documentation
- Updated SCHEMAMAP.md with CSV and XML transformation sections
- Added examples for CSV and XML in examples/transformation/

### Examples
- `examples/transformation/csv/customers.csv` - Sample CSV data
- `examples/transformation/csv/customer_mapping.smap` - CSV mapping example
- `examples/transformation/xml/order.xml` - Sample XML data
- `examples/transformation/xml/order_mapping.smap` - XML mapping example

## [1.7.0] - 2026-01-30

### Added
- **Fixed Length Record (FLR) Support**: Transform mainframe-style fixed-width files
  - New `transform_flr.py` main script
  - `FLRConverter` class with full type inference (string, integer, decimal, date, boolean)
  - `RecordLayout` class for defining field positions and lengths
  - `FieldDefinition` dataclass for individual field specifications
  - Support for JSON and simple text layout file formats
  - COBOL-style position numbering (1-based)
  - Implied decimal handling (common in COBOL)
  - Date format conversion (YYYYMMDD, MMDDYYYY, etc.)
  - Layout validation for overlap/gap detection
  - Presets for mainframe, COBOL, and ASCII formats
  
- **Dictionary Transformation Script**: `transform_dict.py`
  - Unified interface for dict/JSON transformation
  - Support for both interpreted and compiled modes
  - Inline JSON data support with `--data` flag
  - Batch transformation with `--batch` flag
  - Built-in benchmarking with `--benchmark` flag

- **Compiled Transformer Functions**:
  - `create_compiled_transformer()` - Create reusable compiled transformer
  - `compile_and_transform()` - One-step compile and transform
  - Works with all input formats (JSON, CSV, XML, FLR)
  - 5-10x faster than interpreted mode

- **New Convenience Functions**:
  - `transform_flr()` - One-step FLR transformation
  - `flr_to_json()` - Convert FLR to JSON without transformation

### Documentation
- Updated SCHEMAMAP.md with FLR transformation sections
- Added comprehensive FLR layout file format documentation
- Added compiled transformation documentation
- Added examples for FLR in `examples/transformation/flr/`

### Examples
- `examples/transformation/flr/customers.dat` - Sample FLR data
- `examples/transformation/flr/customer_layout.json` - JSON layout file
- `examples/transformation/flr/customer_layout.txt` - Simple text layout file
- `examples/transformation/flr/customer_mapping.smap` - FLR mapping example

## [1.8.0] - 2026-02-02

### Added
- **Multi-Format Output Support**: Transform results can now be serialized to JSON, CSV, or XML
  - New `--output-format` / `-of` flag on all CLI scripts (json, csv, xml)
  - `CSVSerializer` – flattens nested dicts to dot-notation CSV columns
  - `XMLSerializer` – converts dicts to well-formed XML with attribute support
  - `JSONSerializer` – configurable JSON output with wrap/sort options
  - Convenience functions: `dict_to_csv()`, `dict_to_xml()`, `dict_to_json()`

- **TransformPipeline Class**: Unified read → transform → write pipeline
  - Supports any combination of input/output formats
  - `pipeline.run("file.csv")` – file-based execution
  - `pipeline.run_data(dict_list)` – in-memory execution
  - `pipeline.run_to_file("input.csv", "output.xml")` – file-to-file
  - Works with both interpreted and compiled transformers

- **Unified Pipeline CLI**: `transform_pipeline.py`
  - Single script for any-to-any format transformation
  - CSV/XML/FLR input with full options
  - CSV/XML/JSON output with full options
  - `--compiled` flag for production performance

- **Updated transform_csv.py**: Now supports `--output-format csv|xml|json`
  - CSV output options: `--out-delimiter`, `--no-out-header`, `--out-columns`
  - XML output options: `--root-tag`, `--record-tag`, `--no-xml-declaration`

- **Output Serializers Module**: `jsonchamp/transformation/serializers/`
  - `csv_serializer.py` – nested dict flattening, configurable delimiters
  - `xml_serializer.py` – attribute support, pretty printing
  - `json_serializer.py` – wrap key, sort keys, compact mode

### Changed
- `transform_csv()`, `transform_xml()`, `transform_flr()` now accept
  `output_format` and `output_options` parameters
- All format-specific transform functions return native dicts for JSON output
  or formatted strings for CSV/XML output

### Examples
- `examples/transformation/multi_format/employees.csv` – multi-format test data
- `examples/transformation/multi_format/employee_mapping.smap` – mapping example
