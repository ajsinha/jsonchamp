# JsonChamp v1.8.0

```
+==============================================================================+
|                                                                              |
|                           JsonChamp v1.8.0                                   |
|                                                                              |
|            Commercial Grade JSON Schema to Python Code Generator             |
|                      with SchemaMap Transformation DSL                       |
|       Supports JSON, CSV, XML, FLR Inputs → JSON, CSV, XML Outputs          |
|                                                                              |
|                  Copyright (C) 2025-2030, All Rights Reserved                |
|                      Ashutosh Sinha (ajsinha@gmail.com)                      |
|                                                                              |
+==============================================================================+
```

---

## Copyright and Legal Notice

**Copyright (C) 2025-2030, All Rights Reserved**  
**Ashutosh Sinha**  
**Email: ajsinha@gmail.com**

---

## Overview

**JsonChamp** is a comprehensive, commercial-grade Python library for working with JSON Schema. It provides powerful, production-ready tools for:

- **Schema Parsing**: Parse and analyze JSON Schema documents with full Draft-07 support
- **Code Generation**: Generate Python dataclasses from JSON Schema
- **Sample Data Generation**: Create realistic test data with Faker integration
- **Validation**: Validate schemas and data with detailed error reporting
- **Reference Resolution**: Handle complex `$ref` references including remote schemas
- **Module Generation**: Generate complete Python modules from schema folders
- **SchemaMap Transformation**: Transform JSON between schemas using a declarative DSL
- **Multi-Format Input**: Support for JSON, CSV, XML, and Fixed Length Records (FLR)
- **External Python Functions**: Call custom Python functions from SchemaMap DSL
- **Code Compilation**: Compile SchemaMap to optimized Python code (5-10x faster!)

---

## What's New in v1.8.0

### Multi-Format Output

Transform results can now be serialized to **JSON**, **CSV**, or **XML**:

```bash
# CSV → JSON (default)
python transform_csv.py mapping.smap data.csv

# CSV → CSV (re-map columns, rename, compute new fields)
python transform_csv.py mapping.smap data.csv -of csv -o output.csv

# CSV → XML
python transform_csv.py mapping.smap data.csv -of xml -o output.xml
```

**Python API:**
```python
from jsonchamp.transformation import transform_csv, dict_to_csv, dict_to_xml

# CSV → JSON (default)
results = transform_csv("data.csv", "mapping.smap")

# CSV → CSV with output_format
csv_text = transform_csv("data.csv", "mapping.smap", output_format="csv")

# CSV → XML with custom tags
xml_text = transform_csv("data.csv", "mapping.smap",
                         output_format="xml",
                         output_options={"root_tag": "customers"})

# Convenience: serialize any dict list
dict_to_csv(results, file_path="out.csv")
dict_to_xml(results, file_path="out.xml", root_tag="data")
```

### Transform Pipeline

Unified any-to-any transformation in one call:

```python
from jsonchamp.transformation import TransformPipeline

# FLR mainframe → XML in one pipeline
pipeline = TransformPipeline(
    mapping_file="mapping.smap",
    input_format="flr",
    output_format="xml",
    layout="layout.json",
    compiled=True  # 5-10x faster
)
xml_string = pipeline.run("mainframe.dat")
pipeline.run_to_file("mainframe.dat", "output.xml")
```

```bash
# CLI: any format → any format
python transform_pipeline.py mapping.smap data.csv -if csv -of xml -o out.xml
python transform_pipeline.py mapping.smap data.dat -if flr --layout l.json -of csv
```

### Format Support Matrix

| Input ↓ / Output → | JSON | CSV | XML |
|---------------------|------|-----|-----|
| **JSON / Dict**     | ✓    | ✓   | ✓   |
| **CSV**             | ✓    | ✓   | ✓   |
| **XML**             | ✓    | ✓   | ✓   |
| **FLR**             | ✓    | ✓   | ✓   |

### Fixed Length Record (FLR) Support

Transform mainframe-style fixed-width files using SchemaMap DSL:

```bash
# Transform FLR with JSON layout
python transform_flr.py mapping.smap customers.dat --layout layout.json

# EBCDIC encoded mainframe file
python transform_flr.py mapping.smap mainframe.dat --layout layout.json --encoding cp037
```

**Layout Definition (JSON):**
```json
{
  "fields": [
    {"name": "id", "start": 1, "length": 10, "data_type": "integer"},
    {"name": "name", "start": 11, "length": 30},
    {"name": "amount", "start": 41, "length": 12, "data_type": "decimal", "decimal_places": 2}
  ]
}
```

**Python API:**
```python
from jsonchamp.transformation import transform_flr, RecordLayout

# With JSON layout file
results = transform_flr("customers.dat", "mapping.smap", "layout.json")

# Build layout programmatically
layout = RecordLayout()
layout.add_field("id", 1, 10, data_type="integer")
layout.add_field("name", 11, 30)
results = transform_flr("data.dat", "mapping.smap", layout)
```

### Compiled Transformers for All Formats

Use compiled transformers (5-10x faster) with any input format:

```python
from jsonchamp.transformation import create_compiled_transformer, csv_to_json, flr_to_json

# Create compiled transformer once
transformer = create_compiled_transformer("mapping.smap")

# Use with any format
result = transformer.transform({"name": "John"})           # Dict
results = [transformer.transform(r) for r in csv_to_json("data.csv")]  # CSV
results = [transformer.transform(r) for r in flr_to_json("data.dat", "layout.json")]  # FLR
```

### CSV and XML Input Support

Transform CSV and XML files using the same SchemaMap DSL:

```bash
# Transform CSV
python transform_csv.py mapping.smap customers.csv --output result.json

# Transform XML
python transform_xml.py mapping.smap orders.xml --output result.json

# Extract multiple records from XML
python transform_xml.py mapping.smap orders.xml --records "order" --output results.json
```

**Python API:**
```python
from jsonchamp.transformation import transform_csv, transform_xml

# CSV transformation
results = transform_csv("customers.csv", "mapping.smap")

# XML transformation (single document)
result = transform_xml("order.xml", "mapping.smap")

# XML transformation (multiple records)
results = transform_xml("orders.xml", "mapping.smap", element_path="orders/order")
```

### Compiled Transformations (5-10x Faster!)

SchemaMap can now compile `.smap` files to standalone Python code:

```bash
# Compile to Python
python transform.py --compile mapping.smap -o transformer.py

# Benchmark interpreted vs compiled
python transform.py --benchmark mapping.smap input.json
```

**Benchmark Results:**
```
  Interpreted Transformer:
    Ops/second:     7,927
    μs/operation:   126.15

  Compiled Transformer:
    Ops/second:     41,236
    μs/operation:   24.25

  SPEEDUP: 5.2x faster with compiled code!
```

The generated code is:
- **Standalone** - No SchemaMap runtime dependency
- **Optimized** - Transforms inlined, no function lookups
- **Type-hinted** - Full IDE support
- **Production-ready** - Use directly in your applications

---

## Quick Start

### Install

```bash
pip install .
```

### Generate Python Module from JSON Schemas

```bash
python -m jsonchamp generate-module \
    --schema-dir ./schemas \
    --output-dir ./generated \
    --module-name my_models
```

### Transform JSON Data

```bash
# Interpreted (flexible, good for development)
python transform.py mapping.smap input.json

# Compiled (fast, good for production)
python transform.py --compile mapping.smap -o transformer.py
python transformer.py input.json
```

### Python API

```python
from jsonchamp.transformation import transform, load_mapping

# Simple transformation
result = transform(source_data, "mapping.smap")

# With custom functions
transformer = load_mapping("mapping.smap")
transformer.register_function("calc_tax", lambda x, r: round(x * r, 2))
result = transformer.transform(data)
```

---

## SchemaMap Transformation DSL

SchemaMap is a declarative DSL for transforming JSON between schemas.

### Example Mapping File

```
@config {
    null_handling : omit
}

@lookups {
    status_codes : { "A": "ACTIVE", "I": "INACTIVE" }
}

# Simple mappings
user.id                                 : userId
user.email                              : email | lowercase | trim

# Concatenation
user.first + " " + user.last            : fullName | titlecase

# Coalescing
user.mobile ?? user.phone               : primaryPhone

# Lookups
user.status                             : status | lookup(@status_codes)

# Computed fields
@compute(sum(items[*].price))           : total
@now                                    : processedAt
@uuid                                   : transactionId

# External functions
@compute(calculate_tax(subtotal, 0.08)) : tax
```

### Run Transformation

```bash
# Interpret (development)
python transform.py mapping.smap input.json

# Compile (production)
python transform.py --compile mapping.smap -o transformer.py

# Benchmark
python transform.py --benchmark mapping.smap input.json --iterations 10000
```

### Key Features

- **Multi-Format Input**: Transform JSON, CSV, XML, and Fixed Length Record files
- **Multi-Format Output**: Serialize results to JSON, CSV, or XML
- **Transform Pipeline**: Unified any-to-any format transformation
- **90+ Built-in Functions**: String, numeric, date, array transforms
- **External Python Functions**: Call custom functions from DSL
- **Aliases**: Define reusable transform chains
- **Lookups**: Map codes to values
- **Array Support**: Transform arrays element-by-element
- **Computed Fields**: Generate values with expressions
- **Schema Validation**: Validate output against JSON Schema
- **Code Compilation**: Generate optimized Python code (5-10x faster)

See [docs/SCHEMAMAP.md](docs/SCHEMAMAP.md) for full documentation.

---

## CLI Reference

### Transform JSON Data

```bash
python transform.py mapping.smap input.json
python transform.py mapping.smap input.json --output result.json
python transform.py mapping.smap input.json --schema target_schema.json
python transform.py mapping.smap input.json --functions custom_funcs.py
```

### Transform CSV Data

```bash
python transform_csv.py mapping.smap input.csv
python transform_csv.py mapping.smap input.csv --output result.json
python transform_csv.py mapping.smap input.csv --delimiter ";" --encoding utf-8
python transform_csv.py mapping.smap input.tsv --preset tsv
```

### Transform XML Data

```bash
python transform_xml.py mapping.smap input.xml
python transform_xml.py mapping.smap input.xml --output result.json
python transform_xml.py mapping.smap data.xml --records "items/item"
python transform_xml.py mapping.smap data.xml --strip-namespaces --no-root
```

### Transform Fixed Length Record (FLR) Data

```bash
python transform_flr.py mapping.smap data.dat --layout layout.json
python transform_flr.py mapping.smap data.dat --layout layout.txt --output result.json
python transform_flr.py mapping.smap mainframe.dat --layout layout.json --encoding cp037
python transform_flr.py mapping.smap data.dat --layout layout.json --skip-header 1
```

### Transform Dict/JSON with Compiled Mode

```bash
python transform_dict.py mapping.smap input.json
python transform_dict.py mapping.smap input.json --compiled    # 5-10x faster
python transform_dict.py mapping.smap --data '{"name": "John"}'
python transform_dict.py mapping.smap input.json --benchmark
```

### Unified Pipeline (Any Format → Any Format)

```bash
python transform_pipeline.py mapping.smap data.csv -if csv -of json
python transform_pipeline.py mapping.smap data.csv -if csv -of csv -o out.csv
python transform_pipeline.py mapping.smap data.csv -if csv -of xml -o out.xml
python transform_pipeline.py mapping.smap data.dat -if flr --layout layout.json -of csv
python transform_pipeline.py mapping.smap data.xml -if xml --records "item" -of csv
python transform_pipeline.py mapping.smap data.csv -if csv -of xml --compiled
```

### Compile to Python

```bash
python transform.py --compile mapping.smap
python transform.py --compile mapping.smap -o my_transformer.py
python transform.py --compile mapping.smap -o transformer.py --class-name CustomerTransformer
```

### Benchmark Performance

```bash
python transform.py --benchmark mapping.smap input.json
python transform.py --benchmark mapping.smap input.json --iterations 50000
```

---

## Project Structure

```
jsonchamp/
├── jsonchamp/                   # Main package
│   ├── __init__.py              # Public API
│   ├── cli.py                   # CLI implementation
│   ├── module_generator.py      # Module generation
│   ├── core/                    # Core processing
│   ├── generators/              # Code generators
│   ├── models/                  # Data models
│   ├── utils/                   # Utilities
│   └── transformation/          # SchemaMap module
│       ├── parser/              # Lexer, parser, AST
│       ├── engine/              # Transformer, evaluator
│       ├── compiler/            # Python code generator
│       ├── converters/          # Input: CSV/XML/FLR → JSON
│       └── serializers/         # Output: JSON → CSV/XML/JSON
├── examples/
│   ├── schemas/                 # 22+ JSON schemas
│   └── transformation/          # SchemaMap examples
│       ├── source_data/         # Input JSON files
│       ├── mappings/            # .smap files
│       ├── compiled/            # Generated Python code
│       ├── csv/                 # CSV examples
│       ├── xml/                 # XML examples
│       ├── flr/                 # Fixed Length Record examples
│       └── multi_format/        # Multi-format I/O examples
├── docs/                        # Documentation
├── transform.py                 # JSON transformation CLI
├── transform_csv.py             # CSV transformation CLI
├── transform_xml.py             # XML transformation CLI
├── transform_flr.py             # FLR transformation CLI
├── transform_dict.py            # Dict transformation CLI (compiled support)
├── transform_pipeline.py        # Unified any-to-any pipeline CLI
└── README.md
```

---

## Dependencies

### Required
- **Python 3.8+**
- No external dependencies (pure Python core)

### Optional
- **faker**: Realistic sample data
- **requests**: Remote schema fetching
- **jsonschema**: Enhanced validation

---

## License

This software is proprietary and confidential. See [LICENSE](LICENSE) for full terms.

**Copyright (C) 2025-2030, All Rights Reserved**  
**Ashutosh Sinha - ajsinha@gmail.com**
