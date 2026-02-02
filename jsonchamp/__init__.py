"""
JsonSchemaCodeGen - Commercial Grade JSON Schema to Python Code Generator
=========================================================================

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

LEGAL NOTICE:
This software is proprietary and confidential. Unauthorized copying,
distribution, modification, or use is strictly prohibited without
explicit written permission from the copyright holder. This software
is provided "as is" without warranty of any kind, either expressed or implied.

Patent Pending: Certain architectural patterns and implementations
described herein may be subject to patent applications.

=========================================================================

A comprehensive library for working with JSON Schema in Python:
- Generate Python dataclass models from JSON Schema
- Generate sample JSON data from schemas
- Handle complex schemas with $ref, allOf, anyOf, oneOf
- Support for remote and local schema references
- Generate complete Python modules from schema folders
- Full JSON Schema Draft-07 support

Usage:
    from jsonchamp import SchemaProcessor, generate_code, generate_samples

    # Quick start with single schema
    processor = SchemaProcessor(schema)
    code = processor.generate_code()
    samples = processor.generate_samples(count=5)
    
    # Generate complete module from schema folder
    from jsonchamp import generate_module
    generate_module("schemas/", "myapp/models")
"""

__version__ = "1.8.0"
__author__ = "Ashutosh Sinha"
__email__ = "ajsinha@gmail.com"

from .core.schema_parser import SchemaParser
from .core.reference_resolver import ReferenceResolver
from .core.type_mapper import TypeMapper
from .core.validator import SchemaValidator
from .core.schema_processor import SchemaProcessor

from .generators.sample_generator import SampleGenerator, generate_samples
from .generators.class_generator import ClassGenerator, generate_classes
from .generators.code_generator import CodeGenerator, generate_code

from .models.base import BaseModel, JsonSerializable

from .module_generator import ModuleGenerator, generate_module

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core
    "SchemaParser",
    "ReferenceResolver", 
    "TypeMapper",
    "SchemaValidator",
    "SchemaProcessor",
    
    # Generators
    "SampleGenerator",
    "ClassGenerator",
    "CodeGenerator",
    
    # Module Generator
    "ModuleGenerator",
    
    # Convenience functions
    "generate_samples",
    "generate_classes",
    "generate_code",
    "generate_module",
    
    # Models
    "BaseModel",
    "JsonSerializable",
]
