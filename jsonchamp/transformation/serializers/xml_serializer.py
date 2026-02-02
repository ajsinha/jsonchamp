"""
XML Output Serializer

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Serializes transformed dictionaries to XML format.
Uses minidom for reliable element name handling.
"""

from xml.dom import minidom
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import re


class XMLSerializer:
    """
    Serializes dictionaries to XML.

    Keys beginning with ``@`` are emitted as XML attributes.
    The special key ``#text`` is emitted as text content.
    List values produce repeated sibling elements.
    """

    def __init__(
        self,
        root_tag: str = 'root',
        record_tag: str = 'record',
        attr_prefix: str = '@',
        text_key: str = '#text',
        indent: int = 2,
        xml_declaration: bool = True,
        encoding: str = 'utf-8',
        pretty: bool = True,
        list_item_tag: str = 'item'
    ):
        self.root_tag = root_tag
        self.record_tag = record_tag
        self.attr_prefix = attr_prefix
        self.text_key = text_key
        self.indent = indent
        self.xml_declaration = xml_declaration
        self.encoding = encoding
        self.pretty = pretty
        self.list_item_tag = list_item_tag

    @staticmethod
    def _sanitize_tag(name: str) -> str:
        """Ensure a string is a valid XML tag name."""
        tag = re.sub(r'[^a-zA-Z0-9_.\-]', '_', str(name))
        if tag and (tag[0].isdigit() or tag[0] == '-'):
            tag = '_' + tag
        return tag or '_'

    def _is_attr(self, key: str) -> bool:
        return key.startswith(self.attr_prefix)

    def _attr_name(self, key: str) -> str:
        return key[len(self.attr_prefix):]

    def _value_to_str(self, value: Any) -> str:
        if value is None:
            return ''
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    def _build_element(self, doc: minidom.Document, tag: str, data: Any):
        """Recursively build a DOM element from a dict / value."""
        safe_tag = self._sanitize_tag(tag)
        elem = doc.createElement(safe_tag)

        if isinstance(data, dict):
            # Attributes
            for key, val in data.items():
                if self._is_attr(key):
                    elem.setAttribute(
                        self._sanitize_tag(self._attr_name(key)),
                        self._value_to_str(val)
                    )
            # Text content
            if self.text_key in data:
                elem.appendChild(doc.createTextNode(self._value_to_str(data[self.text_key])))
            # Child elements
            for key, val in data.items():
                if self._is_attr(key) or key == self.text_key:
                    continue
                if isinstance(val, list):
                    for item in val:
                        child = self._build_element(doc, key, item)
                        elem.appendChild(child)
                else:
                    child = self._build_element(doc, key, val)
                    elem.appendChild(child)

        elif isinstance(data, list):
            for item in data:
                child = self._build_element(doc, self.list_item_tag, item)
                elem.appendChild(child)
        else:
            elem.appendChild(doc.createTextNode(self._value_to_str(data)))

        return elem

    def serialize(self, data: Union[Dict, List[Dict]]) -> str:
        """Serialize dict or list of dicts to an XML string."""
        doc = minidom.Document()

        if isinstance(data, list):
            root = doc.createElement(self._sanitize_tag(self.root_tag))
            doc.appendChild(root)
            for record in data:
                child = self._build_element(doc, self.record_tag, record)
                root.appendChild(child)
        elif isinstance(data, dict):
            root = self._build_element(doc, self.root_tag, data)
            doc.appendChild(root)
        else:
            root = doc.createElement(self._sanitize_tag(self.root_tag))
            root.appendChild(doc.createTextNode(self._value_to_str(data)))
            doc.appendChild(root)

        if self.pretty:
            raw = doc.toprettyxml(indent=' ' * self.indent, encoding=None)
        else:
            raw = doc.toxml(encoding=None)

        # Handle xml_declaration
        if not self.xml_declaration:
            lines = raw.split('\n')
            if lines and lines[0].startswith('<?xml'):
                lines = lines[1:]
            raw = '\n'.join(lines)

        # Clean blank lines
        raw = re.sub(r'\n\s*\n', '\n', raw)
        return raw.strip() + '\n'

    def serialize_to_file(self, data: Union[Dict, List[Dict]], file_path: Union[str, Path]):
        """Serialize and write to a file."""
        content = self.serialize(data)
        with open(file_path, 'w', encoding=self.encoding) as f:
            f.write(content)


def dict_to_xml(
    data: Union[Dict, List[Dict]],
    file_path: Union[str, Path] = None,
    **kwargs
) -> str:
    """
    Convenience function to serialize dicts to XML.

    Args:
        data: Dictionary or list of dictionaries
        file_path: Optional output file path
        **kwargs: Arguments passed to XMLSerializer
    Returns:
        XML string
    """
    serializer = XMLSerializer(**kwargs)
    if file_path:
        serializer.serialize_to_file(data, file_path)
    return serializer.serialize(data)
