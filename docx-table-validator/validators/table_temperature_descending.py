#!/usr/bin/env python3
"""
table_temperature_descending.py - Temperature Descending Order Validation

Rule: When Temperature is higher, Celsius Value should be lower (descending order)

Usage:
    python validators/table_temperature_descending.py <table_json>
    
    # Or use as module
    from validators.table_temperature_descending import validate
    errors = validate(table_data)
"""

import json
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationError:
    """Validation error"""
    row: int
    column: str
    message: str
    severity: str = "error"
    rule_id: str = "table-temperature-descending"
    rule_name: str = "Temperature Descending Order Check"


def parse_number(value: str) -> Optional[float]:
    """Parse numeric value, return None if unable to parse"""
    if not value or not value.strip():
        return None
    try:
        # Remove common non-numeric characters
        cleaned = value.strip().replace(',', '').replace(' ', '')
        return float(cleaned)
    except ValueError:
        return None


def validate(table: dict) -> List[ValidationError]:
    """
    Validate table temperature descending order
    
    Args:
        table: Table data in format:
            {
                "headers": ["Temperature", "Celsius Value"],
                "rows": [["100", "80"], ["80", "60"], ...]
            }
    
    Returns:
        List of validation errors
    """
    errors = []
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    
    # Find target column indices
    temp_col_idx = None
    celsius_col_idx = None
    
    for i, header in enumerate(headers):
        header_lower = header.strip().lower()
        if header_lower == "temperature":
            temp_col_idx = i
        elif "celsius" in header_lower or "celsius value" in header_lower:
            celsius_col_idx = i
    
    if temp_col_idx is None or celsius_col_idx is None:
        # Cannot match required columns, rule not applicable
        return []
    
    # Collect valid data points (exclude empty and non-numeric values)
    data_points = []
    for row_idx, row in enumerate(rows, start=2):  # Start from row 2 (row 1 is header)
        if temp_col_idx >= len(row) or celsius_col_idx >= len(row):
            continue
            
        temp_val = parse_number(row[temp_col_idx])
        celsius_val = parse_number(row[celsius_col_idx])
        
        if temp_val is not None and celsius_val is not None:
            data_points.append({
                "row": row_idx,
                "temperature": temp_val,
                "celsius": celsius_val
            })
    
    if len(data_points) < 2:
        # Not enough data points to validate order
        return []
    
    # Sort by Temperature from high to low
    sorted_points = sorted(data_points, key=lambda x: x["temperature"], reverse=True)
    
    # Check if sorted celsius values are descending
    for i in range(1, len(sorted_points)):
        prev = sorted_points[i - 1]
        curr = sorted_points[i]
        
        # If Temperature decreases but celsius increases, rule violated
        if prev["temperature"] > curr["temperature"]:
            if curr["celsius"] > prev["celsius"]:
                errors.append(ValidationError(
                    row=curr["row"],
                    column="Celsius Value",
                    message=f"Temperature decreased from {prev['temperature']} to {curr['temperature']}, "
                           f"but Celsius Value increased from {prev['celsius']} to {curr['celsius']}, "
                           f"should show descending trend",
                    severity="error"
                ))
    
    return errors


def validate_from_json(json_path: str) -> List[dict]:
    """Load table from JSON file and validate"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_errors = []
    
    # Handle single table or multiple tables
    tables = data.get("tables", [data]) if "tables" in data else [data]
    
    for table in tables:
        errors = validate(table)
        for error in errors:
            all_errors.append({
                "table_index": table.get("index", 0),
                "row": error.row,
                "column": error.column,
                "rule_id": error.rule_id,
                "rule_name": error.rule_name,
                "message": error.message,
                "severity": error.severity
            })
    
    return all_errors


def main():
    """Command line entry point"""
    if len(sys.argv) < 2:
        print("Usage: python table_temperature_descending.py <table_json>")
        print("Example: python table_temperature_descending.py tables.json")
        sys.exit(1)
    
    json_path = sys.argv[1]
    errors = validate_from_json(json_path)
    
    if errors:
        print(f"Found {len(errors)} error(s):")
        for error in errors:
            print(f"  Row {error['row']}: {error['message']}")
        sys.exit(1)
    else:
        print("✅ Validation passed: Temperature descending order is correct")
        sys.exit(0)


if __name__ == "__main__":
    main()
