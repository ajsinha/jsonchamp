# SchemaMap DSL - Complete Syntax Reference

**Version:** 1.8.0  
**Copyright:** © 2025-2030, All Rights Reserved - Ashutosh Sinha (ajsinha@gmail.com)  
**Last Updated:** February 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start](#2-quick-start)
3. [File Structure](#3-file-structure)
4. [Complete Syntax Reference](#4-complete-syntax-reference)
   - [4.1 Basic Mapping Syntax](#41-basic-mapping-syntax)
   - [4.2 Path Notation](#42-path-notation)
   - [4.3 Operators](#43-operators)
   - [4.4 Special Directives](#44-special-directives)
5. [Configuration Block](#5-configuration-block)
6. [Aliases](#6-aliases)
7. [Lookup Tables](#7-lookup-tables)
8. [Transform Functions - Complete Reference](#8-transform-functions---complete-reference)
   - [8.1 String Functions](#81-string-functions)
   - [8.2 Numeric Functions](#82-numeric-functions)
   - [8.3 Boolean Functions](#83-boolean-functions)
   - [8.4 Date/Time Functions](#84-datetime-functions)
   - [8.5 Array Functions](#85-array-functions)
   - [8.6 Conditional Functions](#86-conditional-functions)
   - [8.7 Special Functions](#87-special-functions)
9. [Array Transformations](#9-array-transformations)
10. [Computed Fields](#10-computed-fields)
11. [External Functions](#11-external-functions)
12. [Code Compilation](#12-code-compilation)
13. [CSV Transformations](#13-csv-transformations)
14. [XML Transformations](#14-xml-transformations)
15. [Fixed Length Record (FLR) Transformations](#15-fixed-length-record-flr-transformations)
16. [Compiled Transformations](#16-compiled-transformations)
17. [Output Formats](#17-output-formats)
18. [Transform Pipeline](#18-transform-pipeline)
19. [CLI Reference](#19-cli-reference)
20. [Python API Reference](#20-python-api-reference)
21. [Syntax Quick Reference Card](#21-syntax-quick-reference-card)

---

## 1. Overview

SchemaMap is a domain-specific language (DSL) for transforming data between schemas. It provides a declarative, readable syntax for defining field mappings and transformations. SchemaMap supports JSON, CSV, and XML as input formats.

### Key Features

| Feature | Description |
|---------|-------------|
| Declarative Syntax | Clear `source : target` mapping notation |
| Transform Chains | Pipe-based function chaining (`\| trim \| lowercase`) |
| Reusable Aliases | Define common transform patterns once with `@aliases` |
| Multi-Format Input | Support for JSON, CSV, and XML input files |
| Lookup Tables | Map codes to values with `@lookups` |
| Array Support | Transform arrays element-by-element with `[*]` |
| Computed Fields | Generate values using `@compute`, `@now`, `@uuid` |
| String Concatenation | Combine fields with `+` operator |
| Coalescing | First non-null with `??` operator |
| External Functions | Call Python functions with `@compute()` |
| Code Compilation | 5-10x faster standalone Python code |

---

## 2. Quick Start

### Create a Mapping File

```
# my_mapping.smap

@config {
    null_handling : omit
}

@aliases {
    Clean : trim | titlecase
}

@lookups {
    status_codes : { "A": "ACTIVE", "I": "INACTIVE" }
}

# Mappings
user.first_name + " " + user.last_name : fullName | @Clean
user.email                              : email | trim | lowercase
user.status                             : status | lookup(@status_codes)
user.age                                : age | to_int
@now                                    : processedAt
```

### Run the Transformation

```bash
# Interpreted mode
python transform.py my_mapping.smap input.json --output result.json

# Compiled mode (faster)
python transform.py --compile my_mapping.smap -o transformer.py
```

### Python API

```python
from jsonchamp.transformation import transform, load_mapping

# One-liner
result = transform(source_data, "my_mapping.smap")

# Reusable transformer
transformer = load_mapping("my_mapping.smap")
result = transformer.transform(source_data)
```

---

## 3. File Structure

A SchemaMap file (`.smap`) has this structure:

```
# ============================================
# Comments start with #
# ============================================

@config {
    # Configuration options (optional)
}

@aliases {
    # Reusable transform chains (optional)
}

@lookups {
    # Lookup tables (optional)
}

# ============================================
# MAPPINGS (required)
# ============================================
source.path : target.path | transforms
```

### Section Order

1. `@config` - Must come first if present
2. `@aliases` - Must come before lookups and mappings
3. `@lookups` - Must come before mappings
4. Mappings - Main transformation rules

---

## 4. Complete Syntax Reference

### 4.1 Basic Mapping Syntax

```
source_expression : target_path
source_expression : target_path | transform1 | transform2 | ...
```

| Component | Description | Example |
|-----------|-------------|---------|
| `source_expression` | Source field path, constant, or expression | `user.name`, `"constant"`, `a + b` |
| `:` | Separator (reads as "maps to") | `:` |
| `target_path` | Target field path (dot notation) | `customer.fullName` |
| `\|` | Pipe operator (chains transforms) | `\| trim \| lowercase` |
| `transform` | Transform function with optional args | `round(2)`, `lookup(@table)` |

### 4.2 Path Notation

#### Simple Paths

```
field                   # Top-level field
object.field            # Nested field
object.nested.deep      # Deeply nested field
```

#### Array Access

```
array[0]                # First element (index 0)
array[1]                # Second element (index 1)
array[-1]               # Last element
array[-2]               # Second to last element
array[*]                # All elements (wildcard)
array[*].field          # Field from all elements
```

#### Optional Fields

```
field?                  # Optional field (skip if null/missing)
object.field?           # Optional nested field
array[*].field?         # Optional field in array elements
```

#### Path Examples

| Path | Description |
|------|-------------|
| `user.name` | Name field in user object |
| `user.address.city` | City in nested address |
| `orders[0]` | First order |
| `orders[-1].total` | Total from last order |
| `orders[*].items[*].price` | All prices from all items in all orders |
| `user.middle_name?` | Optional middle name |

### 4.3 Operators

#### String Concatenation (`+`)

Combines multiple values into a single string:

```
# Concatenate fields
user.first_name + " " + user.last_name : fullName

# With string literals
"Order: " + order.id : displayId

# Multiple fields
addr.line1 + ", " + addr.city + ", " + addr.state : fullAddress
```

#### Coalescing (`??`)

Returns the first non-null value:

```
# Two options
user.mobile ?? user.home : primaryPhone

# Multiple options
user.mobile ?? user.home ?? user.work ?? "N/A" : phone

# With nested paths
contact.email ?? user.email ?? "unknown@example.com" : email
```

**Evaluation Order:** Left to right, stops at first non-null

| Expression | Values | Result |
|------------|--------|--------|
| `a ?? b ?? c` | `a=null, b="X", c="Y"` | `"X"` |
| `a ?? b ?? c` | `a="A", b="B", c="C"` | `"A"` |
| `a ?? b ?? c` | `a=null, b=null, c="C"` | `"C"` |

### 4.4 Special Directives

#### @now - Current Timestamp

```
@now : createdAt                    # ISO 8601 timestamp
@now : timestamp                    # "2026-01-30T12:00:00.000000Z"
```

#### @uuid - Generate UUID

```
@uuid : transactionId               # UUID v4
@uuid : id                          # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### @compute - Computed Values

```
# Built-in functions
@compute(count(items)) : itemCount
@compute(sum(items[*].price)) : totalPrice

# External functions
@compute(calculate_tax(subtotal, 0.08)) : tax
@compute(format_phone(phone, "US")) : formattedPhone

# Multiple arguments from fields
@compute(format_name(first, middle, last)) : fullName
```

#### Constants

```
"1.0" : version | constant          # String constant
42 : magicNumber | constant         # Numeric constant
true : active | constant            # Boolean constant
```

---

## 5. Configuration Block

```
@config {
    null_handling       : omit
    missing_fields      : skip
    date_format         : iso8601
    decimal_precision   : 2
    strict_mode         : false
}
```

### Configuration Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `null_handling` | `omit`, `keep`, `default` | `keep` | How to handle null values |
| `missing_fields` | `skip`, `error`, `default` | `skip` | Handle missing source fields |
| `date_format` | `iso8601`, custom format | `iso8601` | Default date format |
| `decimal_precision` | Integer | `2` | Default decimal places |
| `strict_mode` | `true`, `false` | `false` | Enable strict validation |

### null_handling Values

| Value | Behavior |
|-------|----------|
| `omit` | Remove null fields from output |
| `keep` | Preserve null values in output |
| `default` | Replace null with type-appropriate default |

### missing_fields Values

| Value | Behavior |
|-------|----------|
| `skip` | Skip mappings where source field is missing |
| `error` | Raise error if source field is missing |
| `default` | Use default value for missing fields |

---

## 6. Aliases

Aliases define reusable transform chains referenced with `@` prefix.

### Definition Syntax

```
@aliases {
    AliasName : transform1 | transform2 | transform3
}
```

### Common Alias Patterns

```
@aliases {
    # String cleaning
    Clean           : trim | collapse_spaces
    CleanUpper      : trim | uppercase
    CleanLower      : trim | lowercase
    CleanTitle      : trim | titlecase
    
    # Type conversions
    ToMoney         : to_float | round(2)
    ToPercent       : to_float | round(3)
    ToInteger       : to_int
    ToBool          : to_bool
    
    # Compound operations
    Email           : trim | lowercase
    Phone           : trim | replace("-", "") | replace(" ", "")
    
    # With validation
    SafeString      : trim | max_length(255) | default("")
}
```

### Using Aliases

```
# Reference with @ prefix
user.name           : fullName | @Clean
user.email          : email | @Email
order.total         : total | @ToMoney
user.status         : active | @ToBool

# Combine with other transforms
field : target | @Clean | uppercase
```

### Alias Expansion

| Alias Usage | Expands To |
|-------------|------------|
| `@Clean` | `trim \| collapse_spaces` |
| `@ToMoney` | `to_float \| round(2)` |
| `@CleanTitle` | `trim \| titlecase` |

---

## 7. Lookup Tables

Lookup tables map input values to output values.

### Definition Syntax

```
@lookups {
    table_name : {
        "input1" : "output1",
        "input2" : "output2",
        "input3" : "output3"
    }
}
```

### Common Lookup Patterns

```
@lookups {
    # Status codes
    status_codes : {
        "A"     : "ACTIVE",
        "I"     : "INACTIVE",
        "P"     : "PENDING",
        "S"     : "SUSPENDED"
    }
    
    # Country names
    countries : {
        "US"    : "United States",
        "CA"    : "Canada",
        "UK"    : "United Kingdom",
        "DE"    : "Germany"
    }
    
    # Boolean-like values
    yes_no : {
        "Y"     : true,
        "N"     : false,
        "1"     : true,
        "0"     : false
    }
    
    # Priority levels
    priorities : {
        "H"     : "HIGH",
        "M"     : "MEDIUM",
        "L"     : "LOW"
    }
}
```

### Using Lookups

```
# Basic lookup
user.status : status | lookup(@status_codes)

# With other transforms
user.country : country | uppercase | lookup(@countries)

# Chained with default
code : displayValue | lookup(@codes) | default("Unknown")
```

### Lookup Behavior

| Input | Table Has Key | Result |
|-------|---------------|--------|
| `"A"` | Yes (`"A": "ACTIVE"`) | `"ACTIVE"` |
| `"X"` | No | `"X"` (pass-through) |
| `null` | N/A | `null` |

---

## 8. Transform Functions - Complete Reference

### 8.1 String Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `trim` | - | Remove leading/trailing whitespace | `"  hello  "` → `"hello"` |
| `ltrim` | - | Remove leading whitespace | `"  hello"` → `"hello"` |
| `rtrim` | - | Remove trailing whitespace | `"hello  "` → `"hello"` |
| `lowercase` | - | Convert to lowercase | `"HELLO"` → `"hello"` |
| `uppercase` | - | Convert to uppercase | `"hello"` → `"HELLO"` |
| `titlecase` | - | Capitalize each word | `"hello world"` → `"Hello World"` |
| `capitalize` | - | Capitalize first letter only | `"hello world"` → `"Hello world"` |
| `collapse_spaces` | - | Replace multiple spaces with single | `"a   b"` → `"a b"` |
| `replace(old, new)` | 2 | Replace substring | `"hello" \| replace("l", "x")` → `"hexxo"` |
| `regex_replace(pattern, repl)` | 2 | Regex replacement | `\| regex_replace("\\d+", "X")` |
| `substring(start, end)` | 1-2 | Extract substring | `"hello" \| substring(0, 2)` → `"he"` |
| `prefix(str)` | 1 | Add prefix | `"123" \| prefix("ID-")` → `"ID-123"` |
| `suffix(str)` | 1 | Add suffix | `"file" \| suffix(".txt")` → `"file.txt"` |
| `max_length(n)` | 1 | Truncate to max length | `"hello" \| max_length(3)` → `"hel"` |
| `min_length(n, pad)` | 1-2 | Pad to min length | `"5" \| min_length(3, "0")` → `"005"` |
| `pad_left(n, char)` | 1-2 | Left pad | `"5" \| pad_left(3, "0")` → `"005"` |
| `pad_right(n, char)` | 1-2 | Right pad | `"5" \| pad_right(3, "0")` → `"500"` |
| `split(delimiter)` | 1 | Split into array | `"a,b,c" \| split(",")` → `["a","b","c"]` |
| `join(delimiter)` | 1 | Join array to string | `["a","b"] \| join(",")` → `"a,b"` |
| `reverse` | - | Reverse string | `"hello"` → `"olleh"` |
| `strip(chars)` | 0-1 | Remove specified characters | `"##hello##" \| strip("#")` → `"hello"` |

### 8.2 Numeric Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `to_int` | - | Convert to integer | `"42"` → `42` |
| `to_float` | - | Convert to float | `"3.14"` → `3.14` |
| `round(decimals)` | 0-1 | Round to decimals | `3.14159 \| round(2)` → `3.14` |
| `floor` | - | Round down | `3.7` → `3` |
| `ceil` | - | Round up | `3.2` → `4` |
| `abs` | - | Absolute value | `-5` → `5` |
| `multiply(n)` | 1 | Multiply by n | `10 \| multiply(2)` → `20` |
| `divide(n)` | 1 | Divide by n | `10 \| divide(2)` → `5` |
| `add(n)` | 1 | Add n | `10 \| add(5)` → `15` |
| `subtract(n)` | 1 | Subtract n | `10 \| subtract(3)` → `7` |
| `modulo(n)` | 1 | Remainder | `10 \| modulo(3)` → `1` |
| `power(n)` | 1 | Raise to power | `2 \| power(3)` → `8` |
| `clamp(min, max)` | 2 | Clamp to range | `15 \| clamp(0, 10)` → `10` |
| `percent` | - | Convert to percentage | `0.15` → `15` |
| `from_percent` | - | Convert from percentage | `15` → `0.15` |

### 8.3 Boolean Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `to_bool` | - | Convert to boolean | `"Y"` → `true`, `"N"` → `false` |
| `negate` | - | Logical NOT | `true` → `false` |
| `is_null` | - | Check if null | `null` → `true` |
| `is_empty` | - | Check if empty | `""` → `true`, `[]` → `true` |
| `is_present` | - | Check if not null/empty | `"hello"` → `true` |

**to_bool Conversion Table:**

| Input | Output |
|-------|--------|
| `"Y"`, `"y"`, `"yes"`, `"Yes"`, `"YES"` | `true` |
| `"N"`, `"n"`, `"no"`, `"No"`, `"NO"` | `false` |
| `"true"`, `"True"`, `"TRUE"` | `true` |
| `"false"`, `"False"`, `"FALSE"` | `false` |
| `"1"`, `1` | `true` |
| `"0"`, `0` | `false` |
| Non-empty string | `true` |
| Empty string `""` | `false` |
| `null` | `false` |

### 8.4 Date/Time Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `parse_date(format)` | 1 | Parse date string | `"01/15/2026" \| parse_date("%m/%d/%Y")` |
| `format_date(format)` | 1 | Format date | `\| format_date("%Y-%m-%d")` |
| `to_iso8601` | - | Convert to ISO format | → `"2026-01-15T00:00:00Z"` |
| `to_timestamp` | - | Convert to Unix timestamp | → `1768521600` |
| `from_timestamp` | - | Convert from Unix timestamp | → ISO date |
| `add_days(n)` | 1 | Add days | `\| add_days(7)` |
| `add_months(n)` | 1 | Add months | `\| add_months(1)` |
| `add_years(n)` | 1 | Add years | `\| add_years(1)` |
| `subtract_days(n)` | 1 | Subtract days | `\| subtract_days(7)` |
| `start_of_day` | - | Set to start of day | → `"2026-01-15T00:00:00Z"` |
| `end_of_day` | - | Set to end of day | → `"2026-01-15T23:59:59Z"` |
| `start_of_month` | - | Set to first of month | → `"2026-01-01T00:00:00Z"` |
| `end_of_month` | - | Set to last of month | → `"2026-01-31T23:59:59Z"` |

**Common Date Format Codes:**

| Code | Meaning | Example |
|------|---------|---------|
| `%Y` | 4-digit year | `2026` |
| `%y` | 2-digit year | `26` |
| `%m` | Month (01-12) | `01` |
| `%d` | Day (01-31) | `15` |
| `%H` | Hour 24h (00-23) | `14` |
| `%I` | Hour 12h (01-12) | `02` |
| `%M` | Minute (00-59) | `30` |
| `%S` | Second (00-59) | `45` |
| `%p` | AM/PM | `PM` |

### 8.5 Array Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `first` | - | Get first element | `[1,2,3]` → `1` |
| `last` | - | Get last element | `[1,2,3]` → `3` |
| `at(index)` | 1 | Get element at index | `[1,2,3] \| at(1)` → `2` |
| `count` | - | Count elements | `[1,2,3]` → `3` |
| `sum` | - | Sum numeric values | `[1,2,3]` → `6` |
| `avg` | - | Average of values | `[1,2,3]` → `2` |
| `min` | - | Minimum value | `[3,1,2]` → `1` |
| `max` | - | Maximum value | `[1,3,2]` → `3` |
| `flatten` | - | Flatten nested arrays | `[[1,2],[3]]` → `[1,2,3]` |
| `distinct` | - | Remove duplicates | `[1,2,1,3]` → `[1,2,3]` |
| `sort` | - | Sort ascending | `[3,1,2]` → `[1,2,3]` |
| `sort_desc` | - | Sort descending | `[1,3,2]` → `[3,2,1]` |
| `reverse` | - | Reverse order | `[1,2,3]` → `[3,2,1]` |
| `take(n)` | 1 | Take first n elements | `[1,2,3] \| take(2)` → `[1,2]` |
| `skip(n)` | 1 | Skip first n elements | `[1,2,3] \| skip(1)` → `[2,3]` |
| `wrap` | - | Wrap single value in array | `"a"` → `["a"]` |
| `unwrap` | - | Extract single element | `["a"]` → `"a"` |
| `filter_null` | - | Remove null values | `[1,null,2]` → `[1,2]` |
| `filter_empty` | - | Remove empty values | `["a","",null]` → `["a"]` |

### 8.6 Conditional Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `default(value)` | 1 | Default if null | `null \| default("N/A")` → `"N/A"` |
| `if_empty(value)` | 1 | Default if empty | `"" \| if_empty("N/A")` → `"N/A"` |
| `if_null(value)` | 1 | Alias for default | Same as `default` |
| `when(match, result)` | 2 | Map specific value | `"A" \| when("A", "Active")` → `"Active"` |
| `else(value)` | 1 | Default for when chain | `\| when("A", "X") \| else("?")` |
| `coalesce(v1, v2, ...)` | 1+ | First non-null | `\| coalesce(a, b, "default")` |
| `if_then_else(cond, t, f)` | 3 | Ternary condition | `\| if_then_else(">10", "big", "small")` |

**When/Else Chain Example:**

```
status : displayStatus
    | when("A", "Active")
    | when("I", "Inactive")
    | when("P", "Pending")
    | else("Unknown")
```

### 8.7 Special Functions

| Function | Arguments | Description | Example |
|----------|-----------|-------------|---------|
| `constant` | - | Mark as constant value | `"1.0" : version \| constant` |
| `lookup(table)` | 1 | Lookup in table | `\| lookup(@status_codes)` |
| `mask(visible)` | 0-1 | Mask sensitive data | `"1234567890" \| mask(4)` → `"******7890"` |
| `hash(algo)` | 0-1 | Hash value | `\| hash("md5")` |
| `base64_encode` | - | Encode to Base64 | `"hello"` → `"aGVsbG8="` |
| `base64_decode` | - | Decode from Base64 | `"aGVsbG8="` → `"hello"` |
| `json_encode` | - | Encode to JSON string | `{a:1}` → `"{\"a\":1}"` |
| `json_decode` | - | Decode JSON string | `"{\"a\":1}"` → `{a:1}` |
| `type` | - | Get value type | `"hello"` → `"string"` |
| `debug` | - | Log value (development) | Logs value, passes through |

---

## 9. Array Transformations

### Element-by-Element Mapping

Use `[*]` wildcard to transform each element:

```
# Transform each element
users[*].name : people[*].fullName | titlecase
users[*].age  : people[*].age | to_int
users[*].email : people[*].contact | lowercase

# Nested arrays
orders[*].items[*].price : orders[*].lineItems[*].amount | to_float
```

### Array Mapping Example

**Source:**
```json
{
  "users": [
    {"name": "JOHN DOE", "age": "30", "status": "A"},
    {"name": "JANE SMITH", "age": "25", "status": "I"}
  ]
}
```

**Mapping:**
```
@lookups {
    status : { "A": "ACTIVE", "I": "INACTIVE" }
}

users[*].name   : people[*].fullName | titlecase
users[*].age    : people[*].yearsOld | to_int
users[*].status : people[*].status | lookup(@status)
```

**Result:**
```json
{
  "people": [
    {"fullName": "John Doe", "yearsOld": 30, "status": "ACTIVE"},
    {"fullName": "Jane Smith", "yearsOld": 25, "status": "INACTIVE"}
  ]
}
```

### Array Aggregation

```
# Count elements
@compute(count(items)) : itemCount

# Sum values
@compute(sum(items[*].price)) : totalPrice

# Average
@compute(avg(items[*].rating)) : averageRating

# Get specific elements
items[0] : firstItem
items[-1] : lastItem
```

---

## 10. Computed Fields

### Using @compute

```
# Built-in aggregate functions
@compute(count(items)) : totals.itemCount
@compute(sum(items[*].price)) : totals.subtotal
@compute(avg(items[*].rating)) : metrics.avgRating
@compute(min(items[*].price)) : metrics.lowestPrice
@compute(max(items[*].price)) : metrics.highestPrice

# Arithmetic expressions
@compute(subtotal * 0.08) : tax
@compute(subtotal + tax + shipping) : grandTotal

# External function calls
@compute(calculate_tax(subtotal, rate)) : tax
@compute(format_phone(phone, "US")) : formattedPhone
@compute(generate_order_id(order_num, channel)) : orderId
```

### Using @now and @uuid

```
# Current timestamp
@now : createdAt
@now : metadata.processedAt
@now : audit.timestamp

# Generate UUID
@uuid : transactionId
@uuid : correlationId
@uuid : requestId
```

### Computed Field Examples

| Expression | Description | Example Output |
|------------|-------------|----------------|
| `@now` | ISO 8601 timestamp | `"2026-01-30T12:00:00.000000Z"` |
| `@uuid` | UUID v4 | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` |
| `@compute(count(items))` | Array length | `5` |
| `@compute(sum(prices))` | Sum of array | `150.50` |

---

## 11. External Functions

### Registering Functions

**Via CLI:**
```bash
python transform.py mapping.smap input.json --functions my_functions.py
```

**Via Python API:**
```python
from jsonchamp.transformation import load_mapping

transformer = load_mapping("mapping.smap")
transformer.register_function("calculate_tax", calculate_tax)
transformer.register_file("my_functions.py")
```

### Using External Functions

```
# Single argument
@compute(mask_ssn(customer.ssn)) : customer.maskedSSN

# Multiple arguments
@compute(format_phone(phone, "US")) : formattedPhone
@compute(calculate_age(birth_date)) : age
@compute(format_name(first, middle, last, suffix)) : fullName

# Multiple arguments from different paths
@compute(calculate_total(order.subtotal, order.tax_rate, order.shipping)) : order.total
```

### Function Best Practices

```python
# custom_functions.py

def format_phone(phone: str, country: str = "US") -> str:
    """Format phone number for display."""
    if not phone:
        return None
    
    import re
    digits = re.sub(r'\D', '', str(phone))
    
    if country == "US" and len(digits) == 10:
        return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def mask_ssn(ssn: str) -> str:
    """Mask SSN showing only last 4 digits."""
    if not ssn:
        return None
    
    digits = ssn.replace("-", "")
    if len(digits) >= 4:
        return f"XXX-XX-{digits[-4:]}"
    return "XXX-XX-XXXX"

def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date."""
    if not birth_date:
        return None
    
    from datetime import datetime, date
    try:
        bd = datetime.strptime(birth_date, "%m/%d/%Y").date()
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except ValueError:
        return None
```

---

## 12. Code Compilation

### Compiling to Python

```bash
# Basic compilation
python transform.py --compile mapping.smap

# Custom output and class name
python transform.py --compile mapping.smap \
    -o my_transformer.py \
    --class-name MyTransformer
```

### Using Compiled Code

```python
from my_transformer import MyTransformer

# Create instance
transformer = MyTransformer()

# Register external functions if needed
transformer.register_function("calculate_tax", calculate_tax)

# Transform data
result = transformer.transform(source_data)

# Batch transformation
results = transformer.transform_batch(items)
```

### Performance Comparison

| Metric | Interpreted | Compiled | Improvement |
|--------|-------------|----------|-------------|
| Simple transforms | ~8,000 ops/sec | ~40,000 ops/sec | 5x |
| Complex transforms | ~250 ops/sec | ~1,600 ops/sec | 6.4x |

### Benchmarking

```bash
python transform.py --benchmark mapping.smap input.json --iterations 10000
```

---

## 13. CSV Transformations

SchemaMap can transform CSV files by converting each row to JSON, then applying the mapping rules.

### CSV to JSON Conversion

CSV columns become top-level JSON fields:

**Input CSV:**
```csv
id,name,email,status
1,John Doe,john@example.com,A
2,Jane Smith,jane@test.org,I
```

**Converted JSON (per row):**
```json
{"id": 1, "name": "John Doe", "email": "john@example.com", "status": "A"}
{"id": 2, "name": "Jane Smith", "email": "jane@test.org", "status": "I"}
```

### CSV Transformation CLI

```bash
# Basic CSV transformation
python transform_csv.py mapping.smap customers.csv

# With output file
python transform_csv.py mapping.smap data.csv --output result.json

# Custom delimiter (semicolon)
python transform_csv.py mapping.smap data.csv --delimiter ";"

# Tab-separated values
python transform_csv.py mapping.smap data.tsv --delimiter "\t"

# CSV without header
python transform_csv.py mapping.smap data.csv --no-header --columns "id,name,email"

# Use preset format
python transform_csv.py mapping.smap data.csv --preset excel
python transform_csv.py mapping.smap data.tsv --preset tsv
```

### CSV CLI Options

| Option | Description |
|--------|-------------|
| `--delimiter, -d` | Field delimiter (default: `,`) |
| `--quotechar, -q` | Quote character (default: `"`) |
| `--no-header` | CSV has no header row |
| `--columns` | Column names (comma-separated, for --no-header) |
| `--skip-rows` | Skip N rows at start |
| `--encoding` | File encoding (default: utf-8) |
| `--no-infer-types` | Keep all values as strings |
| `--preset` | Use preset format (excel, tsv, pipe, semicolon) |

### CSV Python API

```python
from jsonchamp.transformation import transform_csv, load_mapping
from jsonchamp.transformation.converters import CSVConverter, csv_to_json

# One-step transformation
results = transform_csv("customers.csv", "mapping.smap")

# Manual conversion and transformation
records = csv_to_json("customers.csv", delimiter=';')
transformer = load_mapping("mapping.smap")
results = [transformer.transform(r) for r in records]

# With options
converter = CSVConverter(
    delimiter=';',
    encoding='utf-8',
    infer_types=True,
    strip_whitespace=True
)
records = converter.convert_file("data.csv")
```

### CSV Mapping Example

```
# customer_mapping.smap - transform CSV customer records

@config {
    null_handling : omit
}

@aliases {
    CleanTitle : trim | titlecase
}

@lookups {
    status_codes : { "A": "ACTIVE", "I": "INACTIVE" }
}

# CSV columns map as top-level fields
id              : customerId | to_int
name            : fullName | @CleanTitle
email           : contact.email | trim | lowercase
status          : accountStatus | lookup(@status_codes)

@now            : processedAt
```

---

## 14. XML Transformations

SchemaMap can transform XML files by converting XML elements to JSON, then applying the mapping rules.

### XML to JSON Conversion

XML elements become JSON objects. Attributes use `@` prefix, text content uses `#text` key.

**Input XML:**
```xml
<order id="ORD-001" status="SHIPPED">
    <customer type="B">
        <name>ACME Corp</name>
        <email>orders@acme.com</email>
    </customer>
    <items>
        <item sku="W-001">
            <name>Widget</name>
            <quantity>10</quantity>
        </item>
    </items>
</order>
```

**Converted JSON:**
```json
{
  "order": {
    "@id": "ORD-001",
    "@status": "SHIPPED",
    "customer": {
      "@type": "B",
      "name": "ACME Corp",
      "email": "orders@acme.com"
    },
    "items": {
      "item": {
        "@sku": "W-001",
        "name": "Widget",
        "quantity": 10
      }
    }
  }
}
```

### XML Transformation CLI

```bash
# Basic XML transformation
python transform_xml.py mapping.smap order.xml

# With output file
python transform_xml.py mapping.smap order.xml --output result.json

# Process multiple records from XML
python transform_xml.py mapping.smap orders.xml --records "order"

# Strip XML namespaces
python transform_xml.py mapping.smap soap_response.xml --strip-namespaces

# Don't preserve root element
python transform_xml.py mapping.smap data.xml --no-root

# Custom attribute prefix
python transform_xml.py mapping.smap data.xml --attr-prefix "_"

# Force elements to always be arrays
python transform_xml.py mapping.smap data.xml --always-array "item,option"
```

### XML CLI Options

| Option | Description |
|--------|-------------|
| `--records, -r` | XPath to record elements for batch processing |
| `--attr-prefix` | Prefix for attributes (default: `@`) |
| `--text-key` | Key for text content (default: `#text`) |
| `--strip-namespaces` | Remove namespace prefixes |
| `--no-root` | Don't preserve root element |
| `--no-infer-types` | Keep all values as strings |
| `--always-array` | Elements that should always be arrays |
| `--preset` | Use preset format (standard, soap, no_attrs) |

### XML Python API

```python
from jsonchamp.transformation import transform_xml, load_mapping
from jsonchamp.transformation.converters import XMLConverter, xml_to_json, xml_to_json_records

# One-step transformation
result = transform_xml("order.xml", "mapping.smap")

# Multiple records
results = transform_xml("orders.xml", "mapping.smap", element_path="orders/order")

# Manual conversion
data = xml_to_json("order.xml", strip_namespaces=True)
transformer = load_mapping("mapping.smap")
result = transformer.transform(data)

# Extract records from XML
records = xml_to_json_records("orders.xml", "order")
results = [transformer.transform(r) for r in records]
```

### XML Mapping Example

```
# order_mapping.smap - transform XML order

@config {
    null_handling : omit
}

@aliases {
    CleanTitle : trim | titlecase
    ToMoney    : to_float | round(2)
}

# XML attributes use @ prefix
order.@id                   : orderId
order.@status               : status

# Nested elements
order.customer.@type        : customer.type
order.customer.name         : customer.companyName | @CleanTitle
order.customer.email        : customer.contact.email | lowercase

# Array elements
order.items.item[*].@sku    : lineItems[*].sku
order.items.item[*].name    : lineItems[*].description
order.items.item[*].quantity : lineItems[*].qty | to_int

@now                        : processedAt
```

---

## 15. Fixed Length Record (FLR) Transformations

SchemaMap can transform fixed-length record files (common in mainframe/COBOL systems) by converting each record to JSON based on a layout definition.

### FLR to JSON Conversion

Fixed-length records have fields at specific positions with fixed widths:

**Input FLR (customers.dat):**
```
0000000001JOHN DOE                      JOHN.DOE@EXAMPLE.COM            A0000123456
0000000002JANE SMITH                    JANE.SMITH@TEST.ORG             I0000056789
```

**Layout Definition:**
```json
{
  "fields": [
    {"name": "id", "start": 1, "length": 10, "data_type": "integer"},
    {"name": "name", "start": 11, "length": 30, "data_type": "string"},
    {"name": "email", "start": 41, "length": 30, "data_type": "string"},
    {"name": "status", "start": 71, "length": 1, "data_type": "string"},
    {"name": "balance", "start": 72, "length": 10, "data_type": "decimal", "decimal_places": 2}
  ]
}
```

**Converted JSON:**
```json
{"id": 1, "name": "JOHN DOE", "email": "JOHN.DOE@EXAMPLE.COM", "status": "A", "balance": 1234.56}
```

### FLR Transformation CLI

```bash
# Basic FLR transformation with JSON layout
python transform_flr.py mapping.smap data.dat --layout layout.json

# With output file
python transform_flr.py mapping.smap data.dat --layout layout.json --output result.json

# Using simple text layout format
python transform_flr.py mapping.smap data.dat --layout layout.txt

# Skip header and footer lines
python transform_flr.py mapping.smap data.dat --layout layout.json --skip-header 1 --skip-footer 1

# EBCDIC encoded mainframe file
python transform_flr.py mapping.smap mainframe.dat --layout layout.json --encoding cp037

# Validate layout before processing
python transform_flr.py mapping.smap data.dat --layout layout.json --validate-layout

# Show intermediate JSON conversion
python transform_flr.py mapping.smap data.dat --layout layout.json --show-json
```

### FLR CLI Options

| Option | Description |
|--------|-------------|
| `--layout, -l` | Path to layout file (required) |
| `--encoding` | File encoding (default: utf-8, use cp037 for EBCDIC) |
| `--skip-header` | Number of header lines to skip |
| `--skip-footer` | Number of footer lines to skip |
| `--no-skip-blank` | Don't skip blank lines |
| `--strip-record` | Strip trailing whitespace from records |
| `--preset` | Use preset format (mainframe, cobol, ascii) |
| `--validate-layout` | Validate layout and show issues |
| `--show-json` | Show intermediate FLR-to-JSON conversion |
| `--show-layout` | Show parsed layout definition |

### Layout File Formats

#### JSON Layout Format

```json
{
  "record_length": 100,
  "fields": [
    {
      "name": "id",
      "start": 1,
      "length": 10,
      "data_type": "integer",
      "trim": true
    },
    {
      "name": "name",
      "start": 11,
      "length": 30,
      "data_type": "string",
      "trim": true
    },
    {
      "name": "amount",
      "start": 41,
      "length": 12,
      "data_type": "decimal",
      "decimal_places": 2
    },
    {
      "name": "birth_date",
      "start": 53,
      "length": 8,
      "data_type": "date",
      "date_format": "YYYYMMDD"
    },
    {
      "name": "active",
      "start": 61,
      "length": 1,
      "data_type": "boolean"
    }
  ]
}
```

#### Simple Text Layout Format

```
# field_name,start,length,type[,decimal_places_or_date_format]
id,1,10,integer
name,11,30,string
amount,41,12,decimal,2
birth_date,53,8,date,YYYYMMDD
active,61,1,boolean
```

### Field Data Types

| Type | Description | Example Input | Example Output |
|------|-------------|---------------|----------------|
| `string` | Text (default) | `"JOHN DOE    "` | `"JOHN DOE"` |
| `integer` | Whole number | `"0000001234"` | `1234` |
| `decimal` | Decimal number | `"0000123456"` (2 places) | `1234.56` |
| `date` | Date value | `"20260130"` (YYYYMMDD) | `"2026-01-30"` |
| `boolean` | True/False | `"Y"`, `"1"`, `"T"` | `true` |

### FLR Python API

```python
from jsonchamp.transformation import transform_flr, load_mapping
from jsonchamp.transformation.converters import FLRConverter, RecordLayout, flr_to_json

# One-step transformation with JSON layout file
results = transform_flr("customers.dat", "mapping.smap", "layout.json")

# With layout dict
layout = {
    "fields": [
        {"name": "id", "start": 1, "length": 10, "data_type": "integer"},
        {"name": "name", "start": 11, "length": 30}
    ]
}
results = transform_flr("data.dat", "mapping.smap", layout)

# Build layout programmatically
layout = RecordLayout()
layout.add_field("id", 1, 10, data_type="integer")
layout.add_field("name", 11, 30)
layout.add_field("amount", 41, 12, data_type="decimal", decimal_places=2)
results = transform_flr("data.dat", "mapping.smap", layout)

# Manual conversion and transformation
records = flr_to_json("data.dat", "layout.json")
transformer = load_mapping("mapping.smap")
results = [transformer.transform(r) for r in records]

# With FLRConverter options
converter = FLRConverter(
    layout=layout,
    encoding='cp037',      # EBCDIC for mainframe
    header_lines=1,        # Skip header
    footer_lines=1,        # Skip footer
    skip_blank_lines=True
)
records = converter.convert_file("mainframe.dat")
```

### FLR Mapping Example

```
# customer_mapping.smap - transform FLR customer records

@config {
    null_handling : omit
}

@aliases {
    CleanTitle : trim | titlecase
    ToMoney    : to_float | round(2)
}

@lookups {
    status_codes : { "A": "ACTIVE", "I": "INACTIVE", "P": "PENDING" }
}

# FLR fields map as top-level (like CSV)
id              : customerId
name            : fullName | @CleanTitle
email           : contact.email | trim | lowercase
status          : accountStatus | lookup(@status_codes)
balance         : account.balance | @ToMoney

@now            : processedAt
"FLR"           : sourceFormat | constant
```

---

## 16. Compiled Transformations

Compiled transformers are 5-10x faster than interpreted mode. They work with all input formats.

### Creating Compiled Transformers

```python
from jsonchamp.transformation import create_compiled_transformer, compile_and_transform

# Create reusable compiled transformer
transformer = create_compiled_transformer("mapping.smap")

# Transform single dict
result = transformer.transform({"name": "John", "age": 30})

# Transform batch
results = transformer.transform_batch([data1, data2, data3])

# One-step compile and transform
result = compile_and_transform(source_data, "mapping.smap")
```

### Using Compiled Transformers with All Formats

```python
from jsonchamp.transformation import (
    create_compiled_transformer, 
    csv_to_json, xml_to_json, flr_to_json
)

# Create compiled transformer once
transformer = create_compiled_transformer("mapping.smap")

# Use with JSON/dict data
result = transformer.transform({"name": "John"})

# Use with CSV data
records = csv_to_json("data.csv")
results = [transformer.transform(r) for r in records]

# Use with XML data
data = xml_to_json("data.xml")
result = transformer.transform(data)

# Use with FLR data
records = flr_to_json("data.dat", "layout.json")
results = [transformer.transform(r) for r in records]
```

### CLI Compiled Mode

```bash
# Dict transformation with compiled mode
python transform_dict.py mapping.smap input.json --compiled

# Benchmark interpreted vs compiled
python transform_dict.py mapping.smap input.json --benchmark
```

---

## 17. Output Formats

SchemaMap can serialize transformation results to JSON, CSV, or XML.

### Output Format Selection

All transform functions and CLI scripts accept `--output-format` (`-of`):

```bash
# CSV input → JSON output (default)
python transform_csv.py mapping.smap data.csv

# CSV input → CSV output
python transform_csv.py mapping.smap data.csv -of csv -o result.csv

# CSV input → XML output
python transform_csv.py mapping.smap data.csv -of xml -o result.xml
```

### JSON Output

JSON is the default output format, returning native Python dicts/lists.

| Option | CLI Flag | Default | Description |
|--------|----------|---------|-------------|
| `indent` | `--compact` | 2 | Indentation (None if compact) |
| `sort_keys` | — | False | Sort keys alphabetically |
| `wrap_key` | `--wrap-key` | None | Wrap list in `{key: [...]}` |

### CSV Output

The CSV serializer flattens nested dicts into dot-notation column headers.

**Nested JSON:**
```json
{"contact": {"email": "a@b.com"}, "age": 30}
```

**Becomes CSV:**
```
contact.email,age
a@b.com,30
```

| Option | CLI Flag | Default | Description |
|--------|----------|---------|-------------|
| `delimiter` | `--out-delimiter` | `,` | Field separator |
| `include_header` | `--no-out-header` | True | Include header row |
| `columns` | `--out-columns` | Auto | Explicit column list |
| `flatten_separator` | `--flatten-sep` | `.` | Nested key separator |
| `null_value` | — | `""` | String for None values |

### XML Output

The XML serializer converts dicts to well-formed XML elements.
Keys prefixed with `@` become attributes. The `#text` key becomes text content.

| Option | CLI Flag | Default | Description |
|--------|----------|---------|-------------|
| `root_tag` | `--root-tag` | `root` | Root element tag |
| `record_tag` | `--record-tag` | `record` | Per-record element tag |
| `attr_prefix` | — | `@` | Prefix for attribute keys |
| `text_key` | — | `#text` | Key for text content |
| `xml_declaration` | `--no-xml-declaration` | True | Include `<?xml?>` |

### Python API — Output Serializers

```python
from jsonchamp.transformation import (
    CSVSerializer, XMLSerializer, JSONSerializer,
    dict_to_csv, dict_to_xml, dict_to_json
)

data = [{"id": 1, "contact": {"email": "a@b.com"}},
        {"id": 2, "contact": {"email": "c@d.com"}}]

# Convenience functions
csv_text = dict_to_csv(data)
xml_text = dict_to_xml(data, root_tag="people", record_tag="person")
json_text = dict_to_json(data, indent=4)

# Write to file
dict_to_csv(data, file_path="output.csv", delimiter=";")
dict_to_xml(data, file_path="output.xml", root_tag="people")

# Full control with serializer classes
csv_ser = CSVSerializer(delimiter="\t", columns=["id", "contact.email"])
csv_text = csv_ser.serialize(data)
csv_ser.serialize_to_file(data, "output.tsv")
```

### Transform Functions with Output Format

All transform functions (`transform_csv`, `transform_xml`, `transform_flr`)
accept `output_format` and `output_options`:

```python
from jsonchamp.transformation import transform_csv

# CSV → JSON (default)
results = transform_csv("data.csv", "mapping.smap")

# CSV → CSV
csv_text = transform_csv("data.csv", "mapping.smap",
                         output_format="csv",
                         output_options={"delimiter": ";"})

# CSV → XML
xml_text = transform_csv("data.csv", "mapping.smap",
                         output_format="xml",
                         output_options={"root_tag": "customers",
                                         "record_tag": "customer"})
```

---

## 18. Transform Pipeline

The `TransformPipeline` class provides an end-to-end interface for reading
any supported format, transforming it, and writing to any output format.

### Supported Format Matrix

| Input ↓ / Output → | JSON | CSV | XML |
|---------------------|------|-----|-----|
| **JSON / Dict**     | ✓    | ✓   | ✓   |
| **CSV**             | ✓    | ✓   | ✓   |
| **XML**             | ✓    | ✓   | ✓   |
| **FLR**             | ✓    | ✓   | ✓   |

### Pipeline Python API

```python
from jsonchamp.transformation import TransformPipeline

# CSV → XML pipeline
pipeline = TransformPipeline(
    mapping_file="mapping.smap",
    input_format="csv",
    output_format="xml",
    output_options={"root_tag": "employees", "record_tag": "employee"}
)

# Run against a file
xml_string = pipeline.run("employees.csv")

# Run against in-memory data
xml_string = pipeline.run_data([{"first": "John"}, {"first": "Jane"}])

# Run and write to file
pipeline.run_to_file("employees.csv", "employees.xml")

# FLR → CSV pipeline with compiled transformer
pipeline = TransformPipeline(
    mapping_file="mapping.smap",
    input_format="flr",
    output_format="csv",
    layout="layout.json",
    compiled=True   # 5-10x faster
)
csv_string = pipeline.run("mainframe.dat")
```

### Pipeline CLI

```bash
# CSV → JSON
python transform_pipeline.py mapping.smap data.csv -if csv

# CSV → CSV (re-map, rename, compute fields)
python transform_pipeline.py mapping.smap data.csv -if csv -of csv -o output.csv

# CSV → XML
python transform_pipeline.py mapping.smap data.csv -if csv -of xml -o output.xml

# FLR → CSV
python transform_pipeline.py mapping.smap data.dat -if flr --layout layout.json -of csv

# XML → CSV
python transform_pipeline.py mapping.smap orders.xml -if xml --records "order" -of csv

# With compiled transformer
python transform_pipeline.py mapping.smap data.csv -if csv -of xml --compiled
```

### Pipeline CLI Options

| Option | Description |
|--------|-------------|
| `-if`, `--input-format` | Input format: json, csv, xml, flr |
| `-of`, `--output-format` | Output format: json, csv, xml |
| `-o`, `--output` | Output file path |
| `--delimiter` | CSV input delimiter |
| `--layout` | FLR layout file |
| `--records` | XML XPath for batch records |
| `--root-tag` | XML output root tag |
| `--record-tag` | XML output record tag |
| `--out-delimiter` | CSV output delimiter |
| `--compiled` | Use compiled transformer |

---

## 19. CLI Reference

### Basic Usage

```bash
python transform.py <mapping_file> <input_file> [options]
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Output file (default: stdout) |
| `--functions FILE` | Load external functions from Python file |
| `--schema FILE` | Validate output against JSON Schema |
| `--verbose` | Verbose output |
| `--quiet` | Suppress non-error output |
| `--pretty` | Pretty-print JSON output |

### Compilation Options

| Option | Description |
|--------|-------------|
| `--compile` | Compile to Python code |
| `--class-name NAME` | Class name for compiled code |

### Benchmark Options

| Option | Description |
|--------|-------------|
| `--benchmark` | Run performance benchmark |
| `--iterations N` | Number of benchmark iterations |

### Examples

```bash
# Basic transformation
python transform.py mapping.smap input.json

# With output file
python transform.py mapping.smap input.json -o result.json

# With external functions
python transform.py mapping.smap input.json --functions funcs.py

# Compile to Python
python transform.py --compile mapping.smap -o transformer.py

# Benchmark
python transform.py --benchmark mapping.smap input.json --iterations 10000
```

---

## 20. Python API Reference

### Quick Transform

```python
from jsonchamp.transformation import transform

result = transform(source_data, "mapping.smap")
```

### Load Mapping

```python
from jsonchamp.transformation import load_mapping

transformer = load_mapping("mapping.smap")
result = transformer.transform(source_data)
```

### Register Functions

```python
# Single function
transformer.register_function("my_func", my_func)

# Multiple functions
transformer.register_functions({
    "func1": func1,
    "func2": func2
})

# From file
transformer.register_file("functions.py")

# From module
transformer.register_module("my_module")
```

### Batch Processing

```python
results = transformer.transform_batch(items)
```

### Error Handling

```python
from jsonchamp.transformation import TransformError

try:
    result = transformer.transform(data)
except TransformError as e:
    print(f"Transformation failed: {e}")
```

---

## 21. Syntax Quick Reference Card

### Mapping Syntax

```
source : target                     # Simple mapping
source : target | transform         # With transform
source : target | t1 | t2 | t3      # Transform chain
source : target | @Alias            # Using alias
```

### Operators

```
a + " " + b                         # String concatenation
a ?? b ?? c                         # Coalescing (first non-null)
field?                              # Optional field
```

### Path Notation

```
field                               # Simple field
object.field                        # Nested field
array[0]                            # Array index
array[-1]                           # Last element
array[*]                            # All elements (wildcard)
array[*].field                      # Field from all elements
```

### Special Directives

```
@now                                # Current timestamp
@uuid                               # Generate UUID
@compute(expr)                      # Computed value
@compute(func(arg1, arg2))          # External function call
"constant"                          # String constant
```

### Blocks

```
@config { option : value }          # Configuration
@aliases { Name : transforms }      # Alias definitions
@lookups { table : { k : v } }      # Lookup tables
```

### Common Transforms

| Transform | Description |
|-----------|-------------|
| `trim` | Remove whitespace |
| `lowercase` | Convert to lowercase |
| `uppercase` | Convert to uppercase |
| `titlecase` | Capitalize words |
| `to_int` | Convert to integer |
| `to_float` | Convert to float |
| `to_bool` | Convert to boolean |
| `round(n)` | Round to n decimals |
| `default(v)` | Default if null |
| `lookup(@t)` | Lookup in table |
| `split(d)` | Split by delimiter |
| `join(d)` | Join with delimiter |
| `max_length(n)` | Truncate |
| `replace(o, n)` | Replace substring |

---

## Related Documentation

- [SHOWCASE_EXAMPLES.md](SHOWCASE_EXAMPLES.md) - Detailed walkthrough of showcase examples
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [EXAMPLES.md](EXAMPLES.md) - Additional examples
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

---

**Document Version:** 1.4.2  
**Author:** Ashutosh Sinha (ajsinha@gmail.com)
