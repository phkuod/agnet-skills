#!/usr/bin/env python3
"""
table_required_fields.py - Required Fields Validation
"""

from dataclasses import dataclass
from typing import List

@dataclass
class ValidationError:
    row: int
    column: str
    message: str
    severity: str = "error"
    rule_id: str = "table-required-fields"
    rule_name: str = "Required Fields Check"

def validate(table: dict) -> List[ValidationError]:
    """
    Validate that all cells in a table under 'Reliability Rules' are non-empty.
    """
    errors = []
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    chapter = table.get("chapter", "")
    section = table.get("section", "")
    
    # Check if table is under Reliability Rules
    if "Reliability Rules" not in chapter and "Reliability Rules" not in section:
        return []
        
    for row_idx, row in enumerate(rows, start=2):
        for col_idx, cell_value in enumerate(row):
            if not cell_value.strip():
                col_name = headers[col_idx] if col_idx < len(headers) else f"Col {col_idx+1}"
                errors.append(ValidationError(
                    row=row_idx,
                    column=col_name,
                    message="Field is empty",
                    severity="error"
                ))
                
    return errors

if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        sys.exit(0)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    tables = data.get("tables", [data]) if "tables" in data else [data]
    all_errors = []
    for table in tables:
        for err in validate(table):
            all_errors.append(err)
    if all_errors:
        for err in all_errors:
            print(f"Row {err.row}, Column {err.column}: {err.message}")
        sys.exit(1)
    else:
        print("PASS")
        sys.exit(0)
