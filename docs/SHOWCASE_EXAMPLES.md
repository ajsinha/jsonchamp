# SchemaMap Showcase Examples - Complete Reference Guide

**Version:** 1.8.0  
**Copyright:** © 2025-2030, All Rights Reserved - Ashutosh Sinha (ajsinha@gmail.com)  
**Last Updated:** January 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Simple Showcase Example](#2-simple-showcase-example)
   - [2.1 Overview](#21-overview)
   - [2.2 Source Data Structure](#22-source-data-structure)
   - [2.3 Configuration Block](#23-configuration-block)
   - [2.4 Aliases Definition](#24-aliases-definition)
   - [2.5 Lookup Tables](#25-lookup-tables)
   - [2.6 Mapping Rules Explained](#26-mapping-rules-explained)
   - [2.7 Complete Output](#27-complete-output)
   - [2.8 Running the Transformation](#28-running-the-transformation)
3. [E-Commerce Order Transformation](#3-e-commerce-order-transformation)
   - [3.1 Overview](#31-overview)
   - [3.2 Source Data Structure](#32-source-data-structure)
   - [3.3 Configuration](#33-configuration)
   - [3.4 Aliases](#34-aliases)
   - [3.5 Lookup Tables](#35-lookup-tables)
   - [3.6 Custom Python Functions](#36-custom-python-functions)
   - [3.7 Array Transformations](#37-array-transformations)
   - [3.8 Computed Aggregate Fields](#38-computed-aggregate-fields)
   - [3.9 Running the Transformation](#39-running-the-transformation)
4. [Code Compilation and Performance](#4-code-compilation-and-performance)
5. [Best Practices](#5-best-practices)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Introduction

This document provides exhaustive documentation for the two showcase examples included with JsonChamp SchemaMap v1.4.x. These examples demonstrate every capability of the transformation DSL.

### Document Scope

This reference covers:
- Complete source data structure analysis with field-by-field breakdown
- Every mapping rule with step-by-step transformation explanations
- All transformation functions, aliases, and lookup tables
- Custom Python function documentation with signatures and examples
- Code compilation process and performance benchmarks
- Best practices, troubleshooting, and common patterns

### Examples Overview

| Example | Complexity | Key Features | Primary Use Case |
|---------|------------|--------------|------------------|
| Simple Showcase | Basic | Core DSL features | Learning & quick transforms |
| E-Commerce Order | Advanced | 40+ custom functions | Enterprise integration |

### Feature Comparison Matrix

| Feature | Simple Example | E-Commerce Example |
|---------|----------------|-------------------|
| Basic field mapping | ✓ | ✓ |
| Nested path mapping | ✓ | ✓ |
| String transforms (trim, case) | ✓ | ✓ |
| Numeric transforms (round, convert) | ✓ | ✓ |
| Aliases (reusable chains) | ✓ | ✓ |
| Lookup tables | ✓ | ✓ |
| Array transformations [*] | ✓ | ✓ |
| String concatenation (+) | ✓ | ✓ |
| Coalescing (??) | ✓ | ✓ |
| Computed fields (@now, @uuid) | ✓ | ✓ |
| External Python functions | - | ✓ |
| Multi-argument functions | - | ✓ |
| Array aggregate functions | - | ✓ |
| Code compilation | ✓ | ✓ |

---

## 2. Simple Showcase Example

### 2.1 Overview

The Simple Showcase demonstrates core SchemaMap features in a concise format. It transforms a user/order record with common data cleaning and formatting operations.

**File Location:** `examples/transformation/showcase/`

| File | Size | Description |
|------|------|-------------|
| `simple_showcase.smap` | 1.8 KB | SchemaMap transformation file (45 lines) |
| `simple_input.json` | 518 bytes | Sample source data |
| `simple_output.json` | 480 bytes | Expected transformation output |
| `compiled/simple_transformer.py` | 8.4 KB | Compiled Python transformer (223 lines) |

---

### 2.2 Source Data Structure

The source JSON represents a typical user record with an associated order:

```json
{
    "user": {
        "id": "USR-12345",
        "status": "A",
        "first_name": "JOHN",
        "last_name": "DOE",
        "email": "  JOHN.DOE@EXAMPLE.COM  ",
        "age": "35",
        "mobile": null,
        "phone": "555-1234",
        "work": "555-5678",
        "address": {
            "street": "  123 Main Street  ",
            "city": "new york",
            "country": "US"
        },
        "tags": ["TECHNOLOGY", "FINANCE", "TRAVEL"]
    },
    "order": {
        "total": "1234.567"
    }
}
```

#### Field-by-Field Analysis

| Path | Type | Example Value | Data Quality Issues |
|------|------|---------------|---------------------|
| `user.id` | string | `USR-12345` | None - clean identifier |
| `user.status` | string | `A` | Single-char code needs expansion |
| `user.first_name` | string | `JOHN` | UPPERCASE from legacy system |
| `user.last_name` | string | `DOE` | UPPERCASE from legacy system |
| `user.email` | string | `  JOHN...  ` | Leading/trailing whitespace, UPPERCASE |
| `user.age` | string | `35` | String type, needs integer conversion |
| `user.mobile` | null | `null` | Null value - need fallback |
| `user.phone` | string | `555-1234` | Available for fallback |
| `user.work` | string | `555-5678` | Secondary fallback |
| `user.address.street` | string | `  123 Main...  ` | Extra whitespace |
| `user.address.city` | string | `new york` | lowercase, needs titlecase |
| `user.address.country` | string | `US` | Country code needs full name |
| `user.tags` | array | `[TECHNOLOGY...]` | UPPERCASE strings |
| `order.total` | string | `1234.567` | String with excess decimals |

---

### 2.3 Configuration Block

The `@config` block sets global transformation options:

```
@config {
    null_handling : omit
}
```

| Option | Value | Description | Alternative Values |
|--------|-------|-------------|-------------------|
| `null_handling` | `omit` | Remove null values from output JSON | `keep`, `default` |

**Explanation:** With `null_handling` set to `omit`, any field that would have a null value is excluded from the output. This creates cleaner JSON without explicit null entries.

---

### 2.4 Aliases Definition

Aliases define reusable transformation chains. They are referenced with the `@` prefix:

```
@aliases {
    Clean       : trim | collapse_spaces
    CleanTitle  : trim | titlecase
    ToMoney     : to_float | round(2)
}
```

#### Alias: @Clean

**Purpose:** Basic string cleaning - remove whitespace and normalize internal spaces  
**Transform Chain:** `trim` → `collapse_spaces`

| Step | Transform | Input | Output |
|------|-----------|-------|--------|
| 1 | `trim` | `"  hello   world  "` | `"hello   world"` |
| 2 | `collapse_spaces` | `"hello   world"` | `"hello world"` |

The `trim` function removes leading and trailing whitespace. The `collapse_spaces` function replaces multiple consecutive spaces with a single space.

#### Alias: @CleanTitle

**Purpose:** Clean string and convert to Title Case  
**Transform Chain:** `trim` → `titlecase`

| Step | Transform | Input | Output |
|------|-----------|-------|--------|
| 1 | `trim` | `"  JOHN DOE  "` | `"JOHN DOE"` |
| 2 | `titlecase` | `"JOHN DOE"` | `"John Doe"` |

Titlecase capitalizes the first letter of each word while lowercasing the rest.

#### Alias: @ToMoney

**Purpose:** Convert to monetary value with exactly 2 decimal places  
**Transform Chain:** `to_float` → `round(2)`

| Step | Transform | Input | Output |
|------|-----------|-------|--------|
| 1 | `to_float` | `"1234.567"` | `1234.567` |
| 2 | `round(2)` | `1234.567` | `1234.57` |

The `to_float` function converts a string to a floating-point number. The `round(2)` function rounds to 2 decimal places, suitable for currency values.

---

### 2.5 Lookup Tables

Lookup tables map codes to human-readable values:

```
@lookups {
    status_map : {
        "A" : "ACTIVE",
        "I" : "INACTIVE", 
        "P" : "PENDING"
    }
    
    country_names : {
        "US" : "United States",
        "CA" : "Canada",
        "UK" : "United Kingdom"
    }
}
```

#### status_map Lookup

**Purpose:** Map single-character status codes to full status names

| Input Code | Output Value | Description |
|------------|--------------|-------------|
| `"A"` | `"ACTIVE"` | Active/enabled account |
| `"I"` | `"INACTIVE"` | Inactive/disabled account |
| `"P"` | `"PENDING"` | Pending approval |
| Unknown | Unchanged | Pass-through if not found |

**Usage:** `user.status : status | lookup(@status_map)`

#### country_names Lookup

**Purpose:** Map ISO country codes to full country names

| Input Code | Output Value |
|------------|--------------|
| `"US"` | `"United States"` |
| `"CA"` | `"Canada"` |
| `"UK"` | `"United Kingdom"` |

**Usage:** `user.address.country : address.country | lookup(@country_names)`

---

### 2.6 Mapping Rules Explained

Each mapping rule follows the syntax:

```
source_expression : target_path | transform1 | transform2 | ...
```

#### Rule 1: Simple Field Mapping

```
user.id : userId
```

- **Source Path:** `user.id`
- **Source Value:** `"USR-12345"`
- **Target Path:** `userId`
- **Transforms:** None (direct copy)
- **Result:** `"userId": "USR-12345"`

This is the simplest form of mapping - a direct copy from source to target with no transformation.

#### Rule 2: Lookup Transformation

```
user.status : status | lookup(@status_map)
```

- **Source Path:** `user.status`
- **Source Value:** `"A"`
- **Target Path:** `status`
- **Transform:** `lookup(@status_map)` - finds 'A' in status_map table
- **Result:** `"status": "ACTIVE"`

The lookup function searches the specified lookup table for the input value and returns the corresponding mapped value.

#### Rule 3: String Concatenation with Transforms

```
user.first_name + " " + user.last_name : fullName | @CleanTitle
```

**Source Expression:** Concatenation of three parts

| Step | Operation | Accumulated Value |
|------|-----------|-------------------|
| 1 | Get `user.first_name` | `"JOHN"` |
| 2 | Add literal `" "` | `"JOHN "` |
| 3 | Get `user.last_name` | `"JOHN DOE"` |
| 4 | Apply `@CleanTitle` alias | `"John Doe"` |

**Result:** `"fullName": "John Doe"`

The `+` operator concatenates multiple source values and string literals. Transforms are applied after concatenation.

#### Rule 4: Email Normalization

```
user.email : email | trim | lowercase
```

**Source Value:** `"  JOHN.DOE@EXAMPLE.COM  "`

| Step | Transform | Value After Transform |
|------|-----------|----------------------|
| 1 | `trim` | `"JOHN.DOE@EXAMPLE.COM"` |
| 2 | `lowercase` | `"john.doe@example.com"` |

**Result:** `"email": "john.doe@example.com"`

Email addresses should always be stored in lowercase for consistent comparison and lookup.

#### Rule 5: Type Conversion (String to Integer)

```
user.age : age | to_int
```

- **Source Value:** `"35"` (string type)
- **Transform:** `to_int` - converts string to integer
- **Result:** `"age": 35` (integer type)

Many legacy systems store numeric values as strings. The `to_int` transform converts to proper integer type.

#### Rule 6: Money Formatting with Alias

```
order.total : orderTotal | @ToMoney
```

- **Source Value:** `"1234.567"`
- **Transform:** `@ToMoney` alias (expands to: `to_float | round(2)`)

| Step | Transform | Value |
|------|-----------|-------|
| 1 | `to_float` | `1234.567` |
| 2 | `round(2)` | `1234.57` |

**Result:** `"orderTotal": 1234.57`

Monetary values should have exactly 2 decimal places for proper currency representation.

#### Rules 7-9: Nested Path Mapping

```
user.address.street  : address.line1   | @Clean
user.address.city    : address.city    | @CleanTitle
user.address.country : address.country | lookup(@country_names)
```

These rules demonstrate mapping from nested source paths to nested target paths:

| Source Path | Target Path | Transform | Input | Output |
|-------------|-------------|-----------|-------|--------|
| `user.address.street` | `address.line1` | `@Clean` | `"  123 Main Street  "` | `"123 Main Street"` |
| `user.address.city` | `address.city` | `@CleanTitle` | `"new york"` | `"New York"` |
| `user.address.country` | `address.country` | `lookup` | `"US"` | `"United States"` |

The target nested structure is automatically created if it doesn't exist.

#### Rule 10: Array Transformation

```
user.tags[*] : interests[*] | lowercase
```

- **Source Array:** `["TECHNOLOGY", "FINANCE", "TRAVEL"]`
- **Wildcard `[*]`:** Operates on ALL elements in the array
- **Transform:** `lowercase` applied to EACH element individually
- **Result Array:** `["technology", "finance", "travel"]`

| Index | Input Element | After lowercase |
|-------|---------------|-----------------|
| 0 | `"TECHNOLOGY"` | `"technology"` |
| 1 | `"FINANCE"` | `"finance"` |
| 2 | `"TRAVEL"` | `"travel"` |

The `[*]` wildcard is essential for array processing. Without it, the entire array would be treated as a single value.

#### Rule 11: Coalescing (First Non-Null)

```
user.mobile ?? user.phone ?? user.work : primaryPhone
```

**Operator:** `??` (coalesce) - returns first non-null value

| Check Order | Path | Value | Action |
|-------------|------|-------|--------|
| 1 | `user.mobile` | `null` | Skip (is null) |
| 2 | `user.phone` | `"555-1234"` | **Use this value!** |
| 3 | `user.work` | `"555-5678"` | Not evaluated |

**Result:** `"primaryPhone": "555-1234"`

Coalescing is evaluated left-to-right and short-circuits when a non-null value is found.

#### Rules 12-13: Computed Fields

```
@now  : processedAt
@uuid : transactionId
```

| Directive | Description | Example Output |
|-----------|-------------|----------------|
| `@now` | Current ISO 8601 timestamp | `"2026-01-30T02:39:31.355398Z"` |
| `@uuid` | Generate unique UUID v4 | `"de118307-2e31-45d8-85a8-c63a65297c7d"` |

Computed fields generate dynamic values at transformation time.

#### Rule 14: Constant Value

```
"1.0" : version | constant
```

- **Source:** `"1.0"` (literal string constant)
- **Transform:** `constant` (no-op, marks as constant)
- **Result:** `"version": "1.0"`

String literals as source values create constant output values. The `constant` transform is optional but documents intent.

---

### 2.7 Complete Output

The fully transformed output JSON:

```json
{
  "userId": "USR-12345",
  "status": "ACTIVE",
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "age": 35,
  "orderTotal": 1234.57,
  "address": {
    "line1": "123 Main Street",
    "city": "New York",
    "country": "United States"
  },
  "interests": ["technology", "finance", "travel"],
  "primaryPhone": "555-1234",
  "processedAt": "2026-01-30T02:39:31.355398Z",
  "transactionId": "de118307-2e31-45d8-85a8-c63a65297c7d",
  "version": "1.0"
}
```

### Transformation Summary Table

| # | Source | Target | Key Transformation |
|---|--------|--------|-------------------|
| 1 | `user.id` | `userId` | Direct copy |
| 2 | `user.status` | `status` | Lookup: A→ACTIVE |
| 3 | `first_name + last_name` | `fullName` | Concat + titlecase |
| 4 | `user.email` | `email` | trim + lowercase |
| 5 | `user.age` | `age` | String to integer |
| 6 | `order.total` | `orderTotal` | Float + round(2) |
| 7 | `address.street` | `address.line1` | Clean whitespace |
| 8 | `address.city` | `address.city` | Titlecase |
| 9 | `address.country` | `address.country` | Lookup: US→United States |
| 10 | `tags[*]` | `interests[*]` | Array lowercase |
| 11 | `mobile ?? phone` | `primaryPhone` | First non-null |
| 12 | `@now` | `processedAt` | Current timestamp |
| 13 | `@uuid` | `transactionId` | Generate UUID |
| 14 | `"1.0"` | `version` | Constant value |

---

### 2.8 Running the Transformation

**Interpreted Mode:**

```bash
python transform.py examples/transformation/showcase/simple_showcase.smap \
    examples/transformation/showcase/simple_input.json \
    --output result.json
```

**Compiled Mode (6x faster):**

```bash
# Compile to Python
python transform.py --compile examples/transformation/showcase/simple_showcase.smap \
    -o simple_transformer.py --class-name SimpleTransformer

# Use compiled transformer
python simple_transformer.py input.json
```

---

## 3. E-Commerce Order Transformation

### 3.1 Overview

This comprehensive example demonstrates a production-grade transformation of a legacy e-commerce order management system (OMS) format to a modern REST API format. It showcases all SchemaMap capabilities including external Python functions with multiple arguments.

**File Location:** `examples/transformation/showcase/ecommerce/`

| File | Size | Description |
|------|------|-------------|
| `legacy_order.json` | 7.5 KB | Complex legacy OMS order format |
| `modern_order_schema.json` | 10 KB | Target JSON Schema definition |
| `order_transformation.smap` | 23 KB | Transformation rules (449 lines) |
| `ecommerce_functions.py` | 20 KB | Custom Python functions (727 lines, 40+ functions) |
| `transformed_order.json` | 7.8 KB | Example transformation output |
| `compiled/ecommerce_transformer.py` | 41 KB | Compiled Python transformer (774 lines) |

### Transformation Scale

| Metric | Value |
|--------|-------|
| Source fields | 150+ |
| Target fields | 200+ |
| Mapping rules | 150+ |
| Lookup tables | 12 |
| Aliases defined | 10 |
| Custom Python functions | 40+ |
| Lines of mapping code | 449 |

---

### 3.2 Source Data Structure

The legacy order JSON contains these major sections:

| Section | Description | Key Challenges |
|---------|-------------|----------------|
| `order_header` | Order metadata, dates, status | MM/DD/YYYY dates, status codes |
| `customer_info` | Customer profile, contact, loyalty | UPPERCASE names, SSN to mask |
| `billing_address` | Billing address details | All uppercase, needs formatting |
| `shipping_address` | Shipping with instructions | All uppercase, needs formatting |
| `line_items[]` | Array of order items | Multiple items with pricing |
| `payment_info[]` | Array of payments | Multiple payment methods |
| `order_totals` | Financial totals | Calculations needed |
| `shipping_info` | Shipping method, tracking | Multiple tracking numbers |
| `promotions_applied[]` | Applied promos | Multiple promotions |
| `audit_info` | System metadata | Timestamps, source system |

#### Order Header Fields

| Field | Type | Example | Transformation Needed |
|-------|------|---------|----------------------|
| `order_num` | string | `"ORD-2024-78523"` | Generate unique ID |
| `order_date` | string | `"12/15/2024"` | Convert to ISO 8601 |
| `order_time` | string | `"14:35:22"` | Combine with date |
| `channel` | string | `"WEB"` | Map to standard enum |
| `order_status` | string | `"SHIP"` | Map code to full status |
| `priority_flag` | string | `"Y"` | Convert to boolean |
| `gift_flag` | string | `"N"` | Convert to boolean |
| `notes` | string | `"  Please..."` | Trim whitespace |

#### Customer Information Fields

| Field | Type | Example | Transformation Needed |
|-------|------|---------|----------------------|
| `cust_id` | string | `"CUST-98765"` | Clean |
| `cust_type` | string | `"P"` | Map: P→INDIVIDUAL |
| `first_nm` | string | `"JENNIFER"` | Titlecase |
| `middle_nm` | string | `"MARIE"` | Titlecase |
| `last_nm` | string | `"SMITH-JOHNSON"` | Titlecase |
| `suffix` | string | `"III"` | Uppercase |
| `email_addr` | string | `"  JENNIFER..."` | Trim + lowercase |
| `phone_primary` | string | `"2125551234"` | Format: +1 (212) 555-1234 |
| `birth_dt` | string | `"06/15/1985"` | ISO date + calculate age |
| `gender_cd` | string | `"F"` | Map: F→FEMALE |
| `ssn` | string | `"123-45-6789"` | Mask: XXX-XX-6789 |
| `loyalty_tier` | string | `"G"` | Map: G→GOLD |
| `loyalty_points` | integer | `15750` | Calculate tier expiration |

---

### 3.3 Configuration

```
@config {
    null_handling       : omit
    missing_fields      : skip
    date_format         : iso8601
    decimal_precision   : 2
}
```

| Option | Value | Description |
|--------|-------|-------------|
| `null_handling` | `omit` | Remove null values from output |
| `missing_fields` | `skip` | Don't fail on missing source fields |
| `date_format` | `iso8601` | Use ISO 8601 date format |
| `decimal_precision` | `2` | Default decimal places for rounding |

---

### 3.4 Aliases

```
@aliases {
    # String cleaning
    Clean       : trim | collapse_spaces
    CleanUpper  : trim | uppercase
    CleanLower  : trim | lowercase
    CleanTitle  : trim | titlecase
    
    # Data type conversions
    ToMoney     : to_float | round(2)
    ToPercent   : to_float | round(3)
    ToInteger   : to_int
    ToBool      : to_bool
}
```

| Alias | Transforms | Input Example | Output Example |
|-------|------------|---------------|----------------|
| `@Clean` | `trim \| collapse_spaces` | `"  hi   there  "` | `"hi there"` |
| `@CleanUpper` | `trim \| uppercase` | `"  hello  "` | `"HELLO"` |
| `@CleanLower` | `trim \| lowercase` | `"  HELLO  "` | `"hello"` |
| `@CleanTitle` | `trim \| titlecase` | `"  JOHN DOE  "` | `"John Doe"` |
| `@ToMoney` | `to_float \| round(2)` | `"123.456"` | `123.46` |
| `@ToPercent` | `to_float \| round(3)` | `"8.8754"` | `8.875` |
| `@ToInteger` | `to_int` | `"42"` | `42` |
| `@ToBool` | `to_bool` | `"Y"` | `true` |

---

### 3.5 Lookup Tables

The transformation defines 12 lookup tables:

#### status_codes

```
status_codes : {
    "NEW"    : "PENDING",     "PND"    : "PENDING",
    "CNF"    : "CONFIRMED",   "PROC"   : "PROCESSING",
    "PICK"   : "PROCESSING",  "PACK"   : "PROCESSING",
    "SHIP"   : "SHIPPED",     "INTRANS": "SHIPPED",
    "DLVR"   : "DELIVERED",   "CXL"    : "CANCELLED",
    "VOID"   : "CANCELLED",   "RFD"    : "REFUNDED"
}
```

#### customer_types

| Code | Value | Description |
|------|-------|-------------|
| `P` | `INDIVIDUAL` | Personal/individual customer |
| `B` | `BUSINESS` | Business customer |
| `G` | `GOVERNMENT` | Government entity |
| `I` | `INDIVIDUAL` | Alternative individual code |

#### loyalty_tiers

| Code | Value | Base Months |
|------|-------|-------------|
| `B` | `BRONZE` | 6 |
| `S` | `SILVER` | 9 |
| `G` | `GOLD` | 12 |
| `P` | `PLATINUM` | 18 |
| `D` | `DIAMOND` | 24 |

#### payment_methods

| Code | Value |
|------|-------|
| `CC` | `CREDIT_CARD` |
| `DEBIT` | `DEBIT_CARD` |
| `PAYPAL` | `PAYPAL` |
| `LOYALTY` | `LOYALTY_POINTS` |
| `GC` | `GIFT_CARD` |

---

### 3.6 Custom Python Functions

The `ecommerce_functions.py` file contains 40+ custom functions organized by category.

#### Date/Time Functions

##### parse_legacy_date(date_str, time_str)

Converts legacy MM/DD/YYYY date and HH:MM:SS time to ISO 8601 format.

```python
def parse_legacy_date(date_str: str, time_str: str = None) -> str
```

**SchemaMap usage:**
```
@compute(parse_legacy_date(order_header.order_date, order_header.order_time)) : orderDate
```

**Example:**
- Input: `date_str="12/15/2024"`, `time_str="14:35:22"`
- Output: `"2024-12-15T14:35:22Z"`

##### calculate_age(birth_date)

Calculates age in years from a birth date.

```python
def calculate_age(birth_date: str) -> int
```

**SchemaMap usage:**
```
@compute(calculate_age(customer_info.birth_dt)) : customer.profile.age
```

**Example:**
- Input: `"06/15/1985"` (when current date is 2026-01-30)
- Output: `40`

#### Name Formatting Functions

##### format_full_name(first, middle, last, suffix)

Builds a properly formatted full name from components.

```python
def format_full_name(first: str, middle: str, last: str, suffix: str = None) -> str
```

**SchemaMap usage:**
```
@compute(format_full_name(customer_info.first_nm, customer_info.middle_nm,
                          customer_info.last_nm, customer_info.suffix)) : customer.profile.fullName
```

**Example:**
- Input: `first="JENNIFER"`, `middle="MARIE"`, `last="SMITH-JOHNSON"`, `suffix="III"`
- Output: `"Jennifer Marie Smith-Johnson III"`

#### Phone Formatting Functions

##### format_phone(phone, country)

Formats a raw phone number for display.

```python
def format_phone(phone: str, country: str = "US") -> str
```

**SchemaMap usage:**
```
@compute(format_phone(customer_info.phone_primary, "US")) : customer.contact.primaryPhone
```

**Example:**
- Input: `phone="2125551234"`, `country="US"`
- Output: `"+1 (212) 555-1234"`

#### Address Formatting Functions

##### format_address_single_line(...)

Creates a formatted single-line address from components.

```python
def format_address_single_line(line1: str, line2: str, line3: str,
                               city: str, state: str, postal: str, country: str) -> str
```

**SchemaMap usage:**
```
@compute(format_address_single_line(billing_address.addr_line1,
         billing_address.addr_line2, billing_address.addr_line3,
         billing_address.city, billing_address.state_prov,
         billing_address.postal_cd, billing_address.country_cd)) : addresses.billing.formatted
```

**Example:**
- Input: `line1="123 MAIN STREET"`, `line2="APT 4B"`, `line3=null`, `city="NEW YORK"`, `state="NY"`, `postal="10001"`, `country="US"`
- Output: `"123 Main Street, Apt 4B, New York, NY 10001"`

#### Financial Calculation Functions

##### calculate_profit_margin(unit_price, unit_cost)

Calculates profit margin as a percentage.

```python
def calculate_profit_margin(unit_price: float, unit_cost: float) -> float
```

**Formula:** `((price - cost) / price) * 100`

**Example:**
- Input: `unit_price=799.99`, `unit_cost=450.00`
- Output: `43.75` (43.75% profit margin)

##### calculate_effective_tax_rate(tax_total, subtotal)

Calculates the effective tax rate.

**SchemaMap usage:**
```
@compute(calculate_effective_tax_rate(order_totals.tax_total,
                                      order_totals.subtotal)) : totals.effectiveTaxRate
```

**Example:**
- Input: `tax_total=90.97`, `subtotal=1024.96`
- Output: `8.875`

##### sum_item_weights(items)

Sums weights from all items considering quantities.

**SchemaMap usage:**
```
@compute(sum_item_weights(line_items)) : totals.totalWeight
```

**Calculation:** `sum(qty_ordered * weight_lbs)` for all items

#### Loyalty Functions

##### calculate_loyalty_tier_expiration(current_tier, loyalty_points)

Calculates loyalty tier expiration based on tier and points.

**Logic:**
- Base months by tier: B=6, S=9, G=12, P=18, D=24
- Bonus: +1 month per 10,000 points (max 6 bonus months)

**Example:**
- Input: `current_tier="G"`, `loyalty_points=15750`
- Calculation: 12 base + 1 bonus (15750/10000 = 1) = 13 months
- Output: `"2027-02-28"`

#### Data Masking Functions

##### mask_ssn(ssn)

Masks SSN showing only last 4 digits for PII protection.

**SchemaMap usage:**
```
@compute(mask_ssn(customer_info.ssn)) : customer.profile.taxId
```

**Example:**
- Input: `"123-45-6789"`
- Output: `"XXX-XX-6789"`

> **IMPORTANT:** This function is essential for PII compliance. Never store unmasked SSNs in target systems.

#### ID Generation Functions

##### generate_order_id(order_num, channel, timestamp)

Generates a unique order ID using MD5 hash of components.

**SchemaMap usage:**
```
@compute(generate_order_id(order_header.order_num, order_header.channel,
                           order_header.order_date)) : orderId
```

**Example:**
- Input: `order_num="ORD-2024-78523"`, `channel="WEB"`, `timestamp="12/15/2024"`
- Output: `"ORD-2B767D9E"`

---

### 3.7 Array Transformations

Arrays are transformed using the `[*]` wildcard syntax:

#### Line Items Array

```
# Map each field from source array to target array
line_items[*].line_num       : items[*].lineNumber | @ToInteger
line_items[*].item_sku       : items[*].sku | @CleanUpper
line_items[*].item_desc      : items[*].name | @CleanTitle
line_items[*].qty_ordered    : items[*].quantity.ordered | @ToInteger
line_items[*].unit_price     : items[*].pricing.unitPrice | @ToMoney
line_items[*].extended_price : items[*].pricing.extendedPrice | @ToMoney
line_items[*].gift_wrap      : items[*].gift.isGiftWrapped | @ToBool
```

**How Array Transformation Works:**
1. Extract the specified field from EACH element in the source array
2. Apply the specified transforms to EACH extracted value
3. Place the results in corresponding positions in the target array
4. Nested target paths create nested objects within each array element

#### Payment Array

```
payment_info[*].payment_seq    : payments[*].sequence | @ToInteger
payment_info[*].payment_method : payments[*].method | lookup(@payment_methods)
payment_info[*].payment_amt    : payments[*].amount | @ToMoney
payment_info[*].card_type      : payments[*].card.type | @CleanUpper
payment_info[*].card_last4     : payments[*].card.lastFour
```

---

### 3.8 Computed Aggregate Fields

External functions can operate on entire arrays to compute aggregates:

```
# Count items in array (built-in function)
@compute(count(line_items)) : totals.itemCount

# Sum quantities across all items (custom function)
@compute(count_total_quantity(line_items)) : totals.totalQuantity

# Sum weights across all items (custom function)
@compute(sum_item_weights(line_items)) : totals.totalWeight

# Calculate effective tax rate (custom function)
@compute(calculate_effective_tax_rate(order_totals.tax_total,
                                      order_totals.subtotal)) : totals.effectiveTaxRate
```

---

### 3.9 Running the Transformation

**Interpreted Mode (with custom functions):**

```bash
python transform.py \
    examples/transformation/showcase/ecommerce/order_transformation.smap \
    examples/transformation/showcase/ecommerce/legacy_order.json \
    --functions examples/transformation/showcase/ecommerce/ecommerce_functions.py \
    --output transformed_order.json
```

**Compile to Python:**

```bash
python transform.py --compile \
    examples/transformation/showcase/ecommerce/order_transformation.smap \
    -o ecommerce_transformer.py \
    --class-name ECommerceTransformer
```

**Run Benchmark:**

```bash
python transform.py --benchmark \
    examples/transformation/showcase/ecommerce/order_transformation.smap \
    examples/transformation/showcase/ecommerce/legacy_order.json \
    --iterations 2000
```

---

## 4. Code Compilation and Performance

### Compilation Benefits

| Aspect | Interpreted Mode | Compiled Mode |
|--------|------------------|---------------|
| Startup time | Parsing overhead each run | Instant (pre-parsed) |
| Transform execution | Runtime dispatch | Inlined Python code |
| Lookup tables | Runtime loading | Embedded in generated code |
| Dependencies | Requires SchemaMap runtime | Standalone Python class |
| Debugging | Easier to trace | Harder to debug |
| Performance | Baseline | 5-10x faster |

### Benchmark Results

**E-Commerce Order Transformation:**

| Metric | Interpreted | Compiled | Improvement |
|--------|-------------|----------|-------------|
| Operations/second | 259 | 1,610 | 6.2x |
| Microseconds/operation | 3,862 | 621 | 6.2x |
| Total time (2000 iterations) | 7.72 sec | 1.24 sec | 6.2x faster |

### When to Use Each Mode

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| Development | Interpreted | Quick iteration, easy debugging |
| Testing | Interpreted | Better error messages |
| Production (low volume) | Either | Both perform adequately |
| Production (high volume) | Compiled | 5-10x faster |
| Batch processing | Compiled | Significant time savings |
| Real-time API | Compiled | Lower latency |

---

## 5. Best Practices

### 5.1 Mapping File Organization

Structure your mapping files for maintainability:

```
# 1. Configuration first
@config { ... }

# 2. Aliases next (reusable patterns)
@aliases { ... }

# 3. Lookup tables
@lookups { ... }

# 4. Mappings grouped by section with clear headers
#===============================================================================
# ORDER HEADER
#===============================================================================
order.id : orderId
...
```

### 5.2 Use Aliases for Repeated Patterns

**Avoid repetition:**

```
# BAD - repeating same transforms
field1 : output1 | trim | lowercase
field2 : output2 | trim | lowercase
field3 : output3 | trim | lowercase

# GOOD - use alias
@aliases { CleanLower : trim | lowercase }

field1 : output1 | @CleanLower
field2 : output2 | @CleanLower
field3 : output3 | @CleanLower
```

### 5.3 Custom Function Guidelines

- **Pure functions:** No side effects, same input always produces same output
- **Null-safe:** Always check for None/null inputs before processing
- **Type-flexible:** Handle both string and numeric inputs gracefully
- **Well-documented:** Include docstrings with parameter descriptions and examples
- **Return None for errors:** Don't raise exceptions that crash the transformation

### 5.4 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Aliases | PascalCase | `@CleanTitle`, `@ToMoney` |
| Lookup tables | snake_case | `status_codes`, `country_names` |
| Custom functions | snake_case | `format_phone`, `calculate_age` |
| Target paths | camelCase | `orderId`, `fullName` |

---

## 6. Troubleshooting

### 6.1 Common Errors

**"Expected ':' in mapping"**
- **Cause:** Parser couldn't find the colon separator
- **Solution:** Check for missing colons or special characters in paths

**"Function not found: xxx"**
- **Cause:** External function not registered
- **Solution:** Use `--functions` flag to register the Python file

**"list indices must be integers"**
- **Cause:** Applying string operation to an array
- **Solution:** Use `[*]` notation for array fields

**"unhashable type: 'dict'"**
- **Cause:** Trying to look up a dictionary in a lookup table
- **Solution:** Ensure lookup source is a scalar value, not an object

### 6.2 Debug Tips

1. Use verbose mode: `python transform.py mapping.smap input.json --verbose`
2. Test custom functions independently in Python before using in mappings
3. Validate incrementally - start with simple mappings, add complexity gradually
4. Review compiled code to understand transformation logic
5. Check that all required external functions are registered

### 6.3 Performance Tips

- Use compiled transformers in production for 5-10x speedup
- Pre-register external functions outside of hot loops
- Use batch transformation for processing multiple records
- Avoid complex regex patterns in frequently-called custom functions
- Cache lookup table results for repeated transformations

---

**Document Version:** 1.6.0  
**Author:** Ashutosh Sinha (ajsinha@gmail.com)
