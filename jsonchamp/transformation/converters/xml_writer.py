"""
JSON to XML Output Writer for SchemaMap Transformations

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Serializes transformed JSON dictionaries to XML format.
Supports configurable root/record elements, attributes, indentation, and namespaces.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import re


class XMLWriter:
    """
    Writes JSON dictionaries to XML format.
    
    Features:
    - Configurable root and record element names
    - Support for writing values as attributes (@ prefix convention)
    - Pretty-printing with configurable indent
    - XML declaration and encoding control
    - Namespace support
    - Array handling
    """
    
    def __init__(
        self,
        root_element: str = 'records',
        record_element: str = 'record',
        attr_prefix: str = '@',
        text_key: str = '#text',
        indent: int = 2,
        xml_declaration: bool = True,
        encoding: str = 'utf-8',
        namespace: Optional[str] = None,
        namespace_prefix: Optional[str] = None,
        null_handling: str = 'omit',
        bool_true: str = 'true',
        bool_false: str = 'false',
        array_item_element: str = 'item',
        pretty_print: bool = True,
        single_record_mode: bool = False
    ):
        """
        Initialize XML writer.
        
        Args:
            root_element: Name of root XML element (default: 'records')
            record_element: Name of each record element (default: 'record')
            attr_prefix: Prefix identifying attributes in dict keys (default: '@')
            text_key: Key identifying text content (default: '#text')
            indent: Indentation spaces for pretty-printing (default: 2)
            xml_declaration: Include XML declaration (default: True)
            encoding: XML encoding attribute (default: 'utf-8')
            namespace: Optional XML namespace URI
            namespace_prefix: Optional namespace prefix
            null_handling: How to handle null values: 'omit', 'empty', 'nil' (default: 'omit')
            bool_true: String for True values (default: 'true')
            bool_false: String for False values (default: 'false')
            array_item_element: Element name for unnamed array items (default: 'item')
            pretty_print: Pretty-print XML output (default: True)
            single_record_mode: If True, don't wrap in root/records (default: False)
        """
        self.root_element = root_element
        self.record_element = record_element
        self.attr_prefix = attr_prefix
        self.text_key = text_key
        self.indent = indent
        self.xml_declaration = xml_declaration
        self.encoding = encoding
        self.namespace = namespace
        self.namespace_prefix = namespace_prefix
        self.null_handling = null_handling
        self.bool_true = bool_true
        self.bool_false = bool_false
        self.array_item_element = array_item_element
        self.pretty_print = pretty_print
        self.single_record_mode = single_record_mode
    
    def _make_tag(self, name: str) -> str:
        """Create a valid XML tag name from a key."""
        # Replace invalid characters
        tag = re.sub(r'[^a-zA-Z0-9_.\-]', '_', str(name))
        # Must start with letter or underscore
        if tag and not tag[0].isalpha() and tag[0] != '_':
            tag = '_' + tag
        return tag or '_unknown'
    
    def _format_value(self, value: Any) -> str:
        """Format a value as a string for XML content."""
        if value is None:
            return ''
        if isinstance(value, bool):
            return self.bool_true if value else self.bool_false
        return str(value)
    
    def _dict_to_element(self, data: Dict, element_name: str) -> ET.Element:
        """Convert a dictionary to an XML element."""
        elem = ET.Element(self._make_tag(element_name))
        
        if not isinstance(data, dict):
            elem.text = self._format_value(data)
            return elem
        
        # Separate attributes, text, and child elements
        attrs = {}
        children = {}
        text_content = None
        
        for key, value in data.items():
            if key.startswith(self.attr_prefix):
                # It's an attribute
                attr_name = key[len(self.attr_prefix):]
                attrs[attr_name] = self._format_value(value)
            elif key == self.text_key:
                text_content = value
            else:
                children[key] = value
        
        # Set attributes
        for attr_name, attr_value in attrs.items():
            elem.set(self._make_tag(attr_name), attr_value)
        
        # Set text content
        if text_content is not None:
            elem.text = self._format_value(text_content)
        
        # Add child elements
        for key, value in children.items():
            if value is None:
                if self.null_handling == 'omit':
                    continue
                elif self.null_handling == 'empty':
                    child = ET.SubElement(elem, self._make_tag(key))
                elif self.null_handling == 'nil':
                    child = ET.SubElement(elem, self._make_tag(key))
                    child.set('xsi:nil', 'true')
            elif isinstance(value, dict):
                child = self._dict_to_element(value, key)
                elem.append(child)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        child = self._dict_to_element(item, key)
                    else:
                        child = ET.Element(self._make_tag(key))
                        child.text = self._format_value(item)
                    elem.append(child)
            else:
                child = ET.SubElement(elem, self._make_tag(key))
                child.text = self._format_value(value)
        
        return elem
    
    def _prettify(self, xml_string: str) -> str:
        """Pretty-print XML string."""
        try:
            dom = minidom.parseString(xml_string)
            pretty = dom.toprettyxml(indent=' ' * self.indent, encoding=None)
            # Remove extra blank lines
            lines = [line for line in pretty.split('\n') if line.strip()]
            if not self.xml_declaration and lines and lines[0].startswith('<?xml'):
                lines = lines[1:]
            return '\n'.join(lines) + '\n'
        except Exception:
            return xml_string
    
    def write_string(self, records: Union[List[Dict], Dict]) -> str:
        """
        Write records to XML string.
        
        Args:
            records: Dictionary or list of dictionaries to write
            
        Returns:
            XML content as string
        """
        if isinstance(records, dict):
            records = [records]
        
        if self.single_record_mode and len(records) == 1:
            root = self._dict_to_element(records[0], self.record_element)
        else:
            root = ET.Element(self._make_tag(self.root_element))
            
            if self.namespace:
                if self.namespace_prefix:
                    root.set(f'xmlns:{self.namespace_prefix}', self.namespace)
                else:
                    root.set('xmlns', self.namespace)
            
            for record in records:
                record_elem = self._dict_to_element(record, self.record_element)
                root.append(record_elem)
        
        xml_string = ET.tostring(root, encoding='unicode')
        
        if self.xml_declaration:
            xml_string = f'<?xml version="1.0" encoding="{self.encoding}"?>\n' + xml_string
        
        if self.pretty_print:
            xml_string = self._prettify(xml_string)
        
        return xml_string
    
    def write_file(self, records: Union[List[Dict], Dict], file_path: Union[str, Path]):
        """
        Write records to XML file.
        
        Args:
            records: Dictionary or list of dictionaries to write
            file_path: Output file path
        """
        xml_content = self.write_string(records)
        with open(file_path, 'w', encoding=self.encoding) as f:
            f.write(xml_content)


class XMLWriterPresets:
    """Common XML output format presets."""
    
    @staticmethod
    def standard() -> dict:
        """Standard XML output."""
        return {
            'root_element': 'records',
            'record_element': 'record',
            'xml_declaration': True,
            'pretty_print': True,
            'indent': 2,
            'null_handling': 'omit'
        }
    
    @staticmethod
    def data_feed() -> dict:
        """Data feed/export style XML."""
        return {
            'root_element': 'data',
            'record_element': 'row',
            'xml_declaration': True,
            'pretty_print': True,
            'null_handling': 'empty'
        }
    
    @staticmethod
    def compact() -> dict:
        """Compact XML without pretty-printing."""
        return {
            'root_element': 'records',
            'record_element': 'record',
            'xml_declaration': False,
            'pretty_print': False,
            'null_handling': 'omit'
        }
    
    @staticmethod
    def single_document() -> dict:
        """Single document output (no wrapping root/records)."""
        return {
            'single_record_mode': True,
            'xml_declaration': True,
            'pretty_print': True,
            'null_handling': 'omit'
        }
