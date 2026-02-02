"""
SchemaMap - JSON Schema Transformation DSL

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

A domain-specific language for transforming JSON documents between schemas.
Supports external Python functions for custom transformation logic.
Supports JSON, CSV, XML, and Fixed Length Records (FLR) as input formats.
Supports JSON, CSV, and XML as output formats.

Example usage:
    from jsonchamp.transformation import transform, load_mapping

    # Basic transformation (dict/JSON)
    result = transform(source_data, "mapping.smap")

    # CSV input -> JSON output (default)
    from jsonchamp.transformation import transform_csv
    results = transform_csv("data.csv", "mapping.smap")

    # CSV input -> CSV output
    results = transform_csv("data.csv", "mapping.smap", output_format="csv")

    # CSV input -> XML output
    results = transform_csv("data.csv", "mapping.smap", output_format="xml")

    # Any input -> any output via pipeline
    from jsonchamp.transformation import TransformPipeline
    pipeline = TransformPipeline("mapping.smap", input_format="csv", output_format="xml")
    output_string = pipeline.run("data.csv")
"""

__version__ = "1.8.0"

from .engine.transformer import SchemaMapTransformer, TransformError
from .engine.evaluator import ExpressionEvaluator, ExternalFunctionError
from .engine.functions import BuiltinFunctions
from .engine.function_registry import (
    FunctionRegistry,
    FunctionRegistryError,
    get_global_registry,
    register_function,
    call_function
)
from .parser.lexer import SchemaMapLexer, Token, TokenType, LexerError
from .parser.parser import (
    SchemaMapParser, ParserError, MappingFile, Mapping,
    SourcePath, TargetPath, Transform, TransformChain,
    FunctionDefinition
)
from .compiler.python_gen import PythonCodeGenerator
from .utils.validation import validate_json_schema, ValidationError

# Input converters (readers)
from .converters import (
    CSVConverter, CSVPresets, csv_to_json,
    XMLConverter, XMLPresets, xml_to_json, xml_to_json_records,
    FLRConverter, FLRPresets, RecordLayout, FieldDefinition, flr_to_json
)

# Output serializers (writers)
from .serializers import (
    JSONSerializer, dict_to_json,
    CSVSerializer, dict_to_csv,
    XMLSerializer, dict_to_xml,
)

__all__ = [
    # Version
    "__version__",
    # Main classes
    "SchemaMapTransformer",
    "TransformError",
    "ExpressionEvaluator",
    "ExternalFunctionError",
    "BuiltinFunctions",
    # Function registry
    "FunctionRegistry",
    "FunctionRegistryError",
    "get_global_registry",
    "register_function",
    "call_function",
    # Parser
    "SchemaMapLexer",
    "SchemaMapParser",
    "LexerError",
    "ParserError",
    # AST nodes
    "MappingFile",
    "Mapping",
    "SourcePath",
    "TargetPath",
    "Transform",
    "TransformChain",
    "FunctionDefinition",
    "Token",
    "TokenType",
    # Compiler
    "PythonCodeGenerator",
    # Validation
    "validate_json_schema",
    "ValidationError",
    # Input converters
    "CSVConverter",
    "CSVPresets",
    "csv_to_json",
    "XMLConverter",
    "XMLPresets",
    "xml_to_json",
    "xml_to_json_records",
    "FLRConverter",
    "FLRPresets",
    "RecordLayout",
    "FieldDefinition",
    "flr_to_json",
    # Output serializers
    "JSONSerializer",
    "dict_to_json",
    "CSVSerializer",
    "dict_to_csv",
    "XMLSerializer",
    "dict_to_xml",
    # Transform Functions
    "transform",
    "load_mapping",
    "compile_mapping",
    "transform_csv",
    "transform_xml",
    "transform_flr",
    "compile_and_transform",
    "create_compiled_transformer",
    # Pipeline
    "TransformPipeline",
]


# ---------------------------------------------------------------------------
# Core helper functions
# ---------------------------------------------------------------------------

def transform(source_data: dict, mapping_file: str, validate_schema: str = None,
              functions: dict = None) -> dict:
    """
    Transform source JSON data using a SchemaMap DSL file.

    Args:
        source_data: The source JSON data as a dictionary
        mapping_file: Path to the .smap mapping file
        validate_schema: Optional path to JSON Schema to validate output
        functions: Optional dictionary of external functions to register

    Returns:
        Transformed JSON data as a dictionary
    """
    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)
    result = transformer.transform(source_data)
    if validate_schema:
        validate_json_schema(result, validate_schema)
    return result


def load_mapping(mapping_file: str) -> SchemaMapTransformer:
    """Load a SchemaMap mapping file and return a transformer."""
    return SchemaMapTransformer.from_file(mapping_file)


def compile_mapping(mapping_file: str, output_format: str = "python",
                    class_name: str = "GeneratedTransformer") -> str:
    """Compile a SchemaMap mapping file to executable Python code."""
    parser = SchemaMapParser()
    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()
    ast = parser.parse(content, filename=mapping_file)
    if output_format == "python":
        generator = PythonCodeGenerator(class_name=class_name)
        return generator.generate(ast)
    raise ValueError(f"Unsupported output format: {output_format}")


# ---------------------------------------------------------------------------
# Format-specific transform helpers
# ---------------------------------------------------------------------------

def transform_csv(csv_file: str, mapping_file: str,
                  csv_options: dict = None, functions: dict = None,
                  output_format: str = "json", output_options: dict = None) -> any:
    """
    Transform CSV data using a SchemaMap DSL file.

    Args:
        csv_file: Path to the CSV file
        mapping_file: Path to the .smap mapping file
        csv_options: Optional dict of CSVConverter options (delimiter, encoding …)
        functions: Optional dictionary of external functions
        output_format: Output format – "json" (default), "csv", or "xml"
        output_options: Optional dict of serializer options for the chosen format

    Returns:
        list[dict] when output_format="json"
        str (CSV text) when output_format="csv"
        str (XML text) when output_format="xml"
    """
    csv_opts = csv_options or {}
    converter = CSVConverter(**csv_opts)
    records = converter.convert_file(csv_file)

    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)

    results = [transformer.transform(record) for record in records]
    return _serialize_output(results, output_format, output_options)


def transform_xml(xml_file: str, mapping_file: str,
                  xml_options: dict = None, element_path: str = None,
                  functions: dict = None,
                  output_format: str = "json", output_options: dict = None) -> any:
    """
    Transform XML data using a SchemaMap DSL file.

    Args:
        xml_file: Path to the XML file
        mapping_file: Path to the .smap mapping file
        xml_options: Optional dict of XMLConverter options
        element_path: Optional path to record elements for batch processing
        functions: Optional dictionary of external functions
        output_format: Output format – "json" (default), "csv", or "xml"
        output_options: Optional dict of serializer options

    Returns:
        dict or list[dict] when output_format="json"
        str when output_format="csv" or "xml"
    """
    xml_opts = xml_options or {}
    converter = XMLConverter(**xml_opts)

    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)

    if element_path:
        records = converter.convert_file_elements(xml_file, element_path)
        results = [transformer.transform(record) for record in records]
    else:
        data = converter.convert_file(xml_file)
        results = transformer.transform(data)

    return _serialize_output(results, output_format, output_options)


def transform_flr(flr_file: str, mapping_file: str, layout: any,
                  flr_options: dict = None, functions: dict = None,
                  output_format: str = "json", output_options: dict = None) -> any:
    """
    Transform Fixed Length Record (FLR) data using a SchemaMap DSL file.

    Args:
        flr_file: Path to the FLR data file
        mapping_file: Path to the .smap mapping file
        layout: RecordLayout object, path to layout JSON/text file, or dict
        flr_options: Optional dict of FLRConverter options
        functions: Optional dictionary of external functions
        output_format: Output format – "json" (default), "csv", or "xml"
        output_options: Optional dict of serializer options

    Returns:
        list[dict] when output_format="json"
        str when output_format="csv" or "xml"
    """
    from pathlib import Path

    if isinstance(layout, RecordLayout):
        record_layout = layout
    elif isinstance(layout, dict):
        record_layout = RecordLayout.from_dict(layout)
    elif isinstance(layout, (str, Path)):
        layout_path = Path(layout)
        if layout_path.suffix.lower() == '.json':
            record_layout = RecordLayout.from_json_file(layout)
        else:
            record_layout = RecordLayout.from_simple_format(layout)
    else:
        raise ValueError(f"Invalid layout type: {type(layout)}")

    flr_opts = flr_options or {}
    converter = FLRConverter(layout=record_layout, **flr_opts)
    records = converter.convert_file(flr_file)

    transformer = SchemaMapTransformer.from_file(mapping_file)
    if functions:
        transformer.register_functions(functions)

    results = [transformer.transform(record) for record in records]
    return _serialize_output(results, output_format, output_options)


# ---------------------------------------------------------------------------
# Compiled transformer helpers
# ---------------------------------------------------------------------------

def create_compiled_transformer(mapping_file: str, class_name: str = "CompiledTransformer"):
    """Create a compiled transformer (5-10x faster) from a mapping file."""
    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()
    parser = SchemaMapParser()
    mapping = parser.parse(content, filename=mapping_file)
    generator = PythonCodeGenerator(class_name=class_name)
    code = generator.generate(mapping)
    exec_globals = {}
    exec(code, exec_globals)
    return exec_globals[class_name]()


def compile_and_transform(source_data: any, mapping_file: str,
                          functions: dict = None, validate_schema: str = None):
    """Compile a mapping and transform data in one step."""
    transformer = create_compiled_transformer(mapping_file)
    if functions:
        for name, func in functions.items():
            transformer.register_function(name, func)
    if isinstance(source_data, list):
        if hasattr(transformer, 'transform_batch'):
            results = transformer.transform_batch(source_data)
        else:
            results = [transformer.transform(item) for item in source_data]
    else:
        results = transformer.transform(source_data)
    if validate_schema:
        if isinstance(results, list):
            for result in results:
                validate_json_schema(result, validate_schema)
        else:
            validate_json_schema(results, validate_schema)
    return results


# ---------------------------------------------------------------------------
# Output serialization helper
# ---------------------------------------------------------------------------

def _serialize_output(data, output_format: str, output_options: dict = None):
    """
    Serialize transformed data into the requested output format.

    Args:
        data: dict or list[dict] of transformed data
        output_format: "json", "csv", or "xml"
        output_options: keyword arguments forwarded to the serializer

    Returns:
        list[dict] for json, str for csv/xml
    """
    fmt = (output_format or 'json').lower().strip()
    opts = output_options or {}

    if fmt == 'json':
        return data  # already native dicts

    if fmt == 'csv':
        serializer = CSVSerializer(**opts)
        return serializer.serialize(data)

    if fmt == 'xml':
        serializer = XMLSerializer(**opts)
        return serializer.serialize(data)

    raise ValueError(f"Unsupported output format: '{output_format}'. Use json, csv, or xml.")


# ---------------------------------------------------------------------------
# TransformPipeline – unified read → transform → write
# ---------------------------------------------------------------------------

class TransformPipeline:
    """
    End-to-end pipeline: read any supported format, apply SchemaMap
    transformation, and write to any supported output format.

    Supported input formats : json, csv, xml, flr, dict
    Supported output formats: json, csv, xml

    Example:
        pipeline = TransformPipeline(
            mapping_file="mapping.smap",
            input_format="csv",
            output_format="xml"
        )

        # Run against a file
        xml_string = pipeline.run("customers.csv")

        # Or run against in-memory data
        xml_string = pipeline.run_data([{"name": "John"}, {"name": "Jane"}])
    """

    def __init__(
        self,
        mapping_file: str,
        input_format: str = "json",
        output_format: str = "json",
        input_options: dict = None,
        output_options: dict = None,
        layout: any = None,
        element_path: str = None,
        functions: dict = None,
        compiled: bool = False,
    ):
        """
        Args:
            mapping_file: Path to the .smap mapping file
            input_format: "json", "csv", "xml", "flr", or "dict"
            output_format: "json", "csv", or "xml"
            input_options: Options forwarded to the input converter
            output_options: Options forwarded to the output serializer
            layout: For FLR input – RecordLayout, path, or dict
            element_path: For XML input – XPath to record elements
            functions: External functions to register
            compiled: Use compiled transformer for speed
        """
        self.mapping_file = mapping_file
        self.input_format = input_format.lower().strip()
        self.output_format = output_format.lower().strip()
        self.input_options = input_options or {}
        self.output_options = output_options or {}
        self.layout = layout
        self.element_path = element_path
        self.functions = functions
        self.compiled = compiled

        # Create transformer once
        if compiled:
            self._transformer = create_compiled_transformer(mapping_file)
        else:
            self._transformer = SchemaMapTransformer.from_file(mapping_file)

        if functions:
            if hasattr(self._transformer, 'register_functions'):
                self._transformer.register_functions(functions)
            else:
                for name, func in functions.items():
                    self._transformer.register_function(name, func)

    def _read_input(self, source) -> list:
        """Read input source into list of dicts."""
        fmt = self.input_format

        if fmt in ('json', 'dict'):
            # source is already dict or list[dict]
            import json as _json
            if isinstance(source, (dict, list)):
                data = source
            else:
                # Assume file path
                with open(source, 'r', encoding='utf-8') as f:
                    data = _json.load(f)
            return data if isinstance(data, list) else [data]

        if fmt == 'csv':
            converter = CSVConverter(**self.input_options)
            return converter.convert_file(source)

        if fmt == 'xml':
            converter = XMLConverter(**self.input_options)
            if self.element_path:
                return converter.convert_file_elements(source, self.element_path)
            data = converter.convert_file(source)
            return data if isinstance(data, list) else [data]

        if fmt == 'flr':
            from pathlib import Path as _Path
            layout = self.layout
            if isinstance(layout, RecordLayout):
                record_layout = layout
            elif isinstance(layout, dict):
                record_layout = RecordLayout.from_dict(layout)
            elif isinstance(layout, (str, _Path)):
                lp = _Path(layout)
                record_layout = (RecordLayout.from_json_file(layout)
                                 if lp.suffix.lower() == '.json'
                                 else RecordLayout.from_simple_format(layout))
            else:
                raise ValueError("FLR input requires a layout")
            converter = FLRConverter(layout=record_layout, **self.input_options)
            return converter.convert_file(source)

        raise ValueError(f"Unsupported input format: '{fmt}'")

    def _write_output(self, results):
        """Serialize results into the chosen output format."""
        return _serialize_output(results, self.output_format, self.output_options)

    def run(self, source) -> any:
        """
        Run the full pipeline: read → transform → serialize.

        Args:
            source: File path (str) for file-based input, or dict/list for dict input.

        Returns:
            list[dict] for json output, str for csv/xml output.
        """
        records = self._read_input(source)
        results = [self._transformer.transform(r) for r in records]
        return self._write_output(results)

    def run_data(self, data: any) -> any:
        """
        Run pipeline on in-memory data (dict or list of dicts).

        Convenience wrapper that forces ``input_format='dict'``.
        """
        records = data if isinstance(data, list) else [data]
        results = [self._transformer.transform(r) for r in records]
        return self._write_output(results)

    def run_to_file(self, source, output_file: str):
        """
        Run pipeline and write output to a file.

        Args:
            source: Input source (file path or data)
            output_file: Path where output is written
        """
        output = self.run(source)
        if isinstance(output, list):
            import json as _json
            content = _json.dumps(output, indent=2, default=str)
        else:
            content = output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
