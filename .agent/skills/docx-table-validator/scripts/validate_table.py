#!/usr/bin/env python3
"""
validate_table.py - Validate table content

Usage:
    python validate_table.py <tables_json> --rules <rules_dir> --output <output_file>
    
Example:
    python validate_table.py tables.json --rules rules/ --output results.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ValidationError:
    """Validation error"""
    table_index: int
    row: int
    column: str
    rule_id: str
    rule_name: str
    message: str
    severity: str  # "error" or "warning"


@dataclass 
class RuleDefinition:
    """Rule definition"""
    id: str
    name: str
    type: str  # not-empty, allowed-values, pattern, conditional, cross-reference, glossary
    severity: str
    config: dict


def parse_markdown_rules(md_content: str) -> dict:
    """
    Parse Markdown format rule file
    
    Returns:
        {
            "table_matcher": {"columns": [...]},
            "rules": [RuleDefinition, ...]
        }
    """
    result = {
        "table_matcher": {"columns": [], "match_mode": "contains", "column_pattern": None},
        "rules": []
    }
    
    lines = md_content.split('\n')
    current_section = None
    current_rule = None
    rule_id = 0
    in_code_block = False
    in_matcher_yaml = False
    in_columns_list = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Identify sections
        if not in_code_block and (line_stripped.startswith('## Table') or line_stripped.startswith('### Target') or line_stripped.startswith('### Phase 1')):
            current_section = 'matcher'
            continue
        elif not in_code_block and (line_stripped.startswith('## Validation') or line_stripped.startswith('### Validation') or line_stripped.startswith('### Phase 2')):
            current_section = 'rules'
            in_matcher_yaml = False
            in_code_block = False
            in_columns_list = False
            continue
        
        # Parse table matcher
        if current_section == 'matcher':
            # Track code block boundaries
            if line_stripped.startswith('```'):
                if in_code_block:
                    # Closing code block
                    in_code_block = False
                    in_matcher_yaml = False
                    in_columns_list = False
                else:
                    # Opening code block
                    in_code_block = True
                    if 'yaml' in line_stripped:
                        in_matcher_yaml = True
                continue
            
            # Parse YAML code block content
            if in_code_block and in_matcher_yaml:
                # Detect "columns:" key
                if re.match(r'^\s*columns:', line_stripped):
                    # Inline list: columns: [A, B, C]
                    inline_match = re.match(r'^\s*columns:\s*\[(.+)\]', line_stripped)
                    if inline_match:
                        cols = [c.strip().strip("'\"") for c in inline_match.group(1).split(',')]
                        result["table_matcher"]["columns"].extend(cols)
                    else:
                        in_columns_list = True
                    continue
                
                # List items under "columns:"
                if in_columns_list:
                    yaml_item = re.match(r'^\s*-\s+(.+)$', line_stripped)
                    if yaml_item:
                        col = yaml_item.group(1).strip().strip("'\"")
                        result["table_matcher"]["columns"].append(col)
                    elif line_stripped and not line_stripped.startswith('#'):
                        in_columns_list = False
                
                # Extract match-mode
                mode_match = re.match(r'^\s*match-mode:\s*(\S+)', line_stripped)
                if mode_match:
                    result["table_matcher"]["match_mode"] = mode_match.group(1).strip()
                    in_columns_list = False
                
                # Extract column-pattern
                pattern_match = re.match(r"^\s*column-pattern:\s*[\"'](.+?)[\"']", line_stripped)
                if pattern_match:
                    result["table_matcher"]["column_pattern"] = pattern_match.group(1)
                    in_columns_list = False
                
                continue
            
            # Fallback: bullet list matchers (outside code blocks)
            if not in_code_block and line_stripped.startswith('- '):
                col = line_stripped[2:].strip()
                result["table_matcher"]["columns"].append(col)
        
        # Parse rules
        elif current_section == 'rules':
            # Rule title: ### Rule Name [ERROR]
            match = re.match(r'^###\s+(.+?)\s*\[(ERROR|WARNING)\]', line_stripped, re.IGNORECASE)
            if match:
                if current_rule:
                    result["rules"].append(current_rule)
                
                rule_id += 1
                rule_name = match.group(1).strip()
                severity = match.group(2).lower()
                
                current_rule = {
                    "id": f"rule-{rule_id}",
                    "name": rule_name,
                    "type": "unknown",
                    "severity": severity,
                    "config": {
                        "columns": [],
                        "values": [],
                        "pattern": None,
                        "condition": None,
                        "then": None,
                        "description": []
                    }
                }
                continue
            
            if current_rule:
                # Collect rule content
                if line_stripped.startswith('- '):
                    item = line_stripped[2:].strip()
                    current_rule["config"]["columns"].append(item)
                    current_rule["config"]["values"].append(item)
                
                # Detect rule type
                if 'empty' in line_stripped.lower() or 'required' in line_stripped.lower():
                    current_rule["type"] = "not-empty"
                elif 'allowed' in line_stripped.lower() or 'values' in line_stripped.lower():
                    current_rule["type"] = "allowed-values"
                elif 'format' in line_stripped.lower() and 'regex' in line_stripped.lower():
                    current_rule["type"] = "pattern"
                elif 'when' in line_stripped.lower() and 'then' in line_stripped.lower():
                    current_rule["type"] = "conditional"
                elif 'reference' in line_stripped.lower():
                    current_rule["type"] = "cross-reference"
                elif 'terminology' in line_stripped.lower():
                    current_rule["type"] = "glossary"
                
                # Extract regex pattern
                pattern_match = re.search(r'`([^^].*?)`', line_stripped)
                if pattern_match and current_rule["type"] == "pattern":
                    current_rule["config"]["pattern"] = pattern_match.group(1)
                
                # Record description
                if line_stripped:
                    current_rule["config"]["description"].append(line_stripped)
    
    # Add last rule
    if current_rule:
        result["rules"].append(current_rule)
    
    return result


def load_rules_from_directory(rules_dir: str) -> list:
    """Load all rule files from rules directory"""
    rules_path = Path(rules_dir)
    all_rules = []
    
    for md_file in rules_path.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        parsed = parse_markdown_rules(content)
        parsed["source_file"] = md_file.name
        all_rules.append(parsed)
    
    return all_rules


def match_table_to_rules(table: dict, rules_list: list) -> Optional[dict]:
    """Match applicable rules based on table columns and/or column patterns"""
    table_headers = set(h.strip() for h in table.get("headers", []))
    
    for rules in rules_list:
        matcher = rules["table_matcher"]
        matcher_columns = set(matcher.get("columns", []))
        column_pattern = matcher.get("column_pattern")
        
        # Check exact columns (subset match)
        exact_match = matcher_columns.issubset(table_headers) if matcher_columns else False
        
        # Check column pattern (regex against any header)
        pattern_match = False
        if column_pattern:
            try:
                regex = re.compile(column_pattern)
                pattern_match = any(regex.search(h) for h in table_headers)
            except re.error:
                pass
        
        # Match logic:
        # - If both exact columns and pattern: both must match
        # - If only exact columns: exact must match
        # - If only pattern: pattern must match
        if matcher_columns and column_pattern:
            if exact_match and pattern_match:
                return rules
        elif matcher_columns:
            if exact_match:
                return rules
        elif column_pattern:
            if pattern_match:
                return rules
    
    # If no match, return common.md rules (if exists)
    for rules in rules_list:
        if rules.get("source_file") == "common.md":
            return rules
    
    return None


def validate_not_empty(table: dict, rule: dict) -> list:
    """Validate required fields"""
    errors = []
    columns = rule["config"]["columns"]
    headers = table.get("headers", [])
    
    # If no columns specified, check all columns
    if not columns or columns == ["All columns"]:
        columns = headers
    
    for row_idx, row in enumerate(table.get("rows", []), start=2):
        for col_name in columns:
            if col_name in headers:
                col_idx = headers.index(col_name)
                if col_idx < len(row):
                    value = row[col_idx].strip()
                    if not value:
                        errors.append(ValidationError(
                            table_index=table.get("index", 0),
                            row=row_idx,
                            column=col_name,
                            rule_id=rule["id"],
                            rule_name=rule["name"],
                            message="Field is empty",
                            severity=rule["severity"]
                        ))
    
    return errors


def validate_allowed_values(table: dict, rule: dict) -> list:
    """Validate allowed values"""
    errors = []
    columns = rule["config"]["columns"]
    allowed_values = set(rule["config"]["values"])
    headers = table.get("headers", [])
    
    # Filter actual column names (not values in the list)
    actual_columns = [c for c in columns if c in headers]
    
    if not actual_columns:
        # If no explicit columns in rule description, try to extract from description
        for desc in rule["config"].get("description", []):
            for header in headers:
                if header in desc and header not in actual_columns:
                    actual_columns.append(header)
    
    for row_idx, row in enumerate(table.get("rows", []), start=2):
        for col_name in actual_columns:
            if col_name in headers:
                col_idx = headers.index(col_name)
                if col_idx < len(row):
                    value = row[col_idx].strip()
                    if value and value not in allowed_values:
                        errors.append(ValidationError(
                            table_index=table.get("index", 0),
                            row=row_idx,
                            column=col_name,
                            rule_id=rule["id"],
                            rule_name=rule["name"],
                            message=f"Value \"{value}\" not in allowed values list",
                            severity=rule["severity"]
                        ))
    
    return errors


def validate_pattern(table: dict, rule: dict) -> list:
    """Validate format (regex)"""
    errors = []
    pattern = rule["config"].get("pattern")
    columns = rule["config"]["columns"]
    headers = table.get("headers", [])
    
    if not pattern:
        return errors
    
    actual_columns = [c for c in columns if c in headers]
    
    try:
        regex = re.compile(pattern)
    except re.error:
        return errors
    
    for row_idx, row in enumerate(table.get("rows", []), start=2):
        for col_name in actual_columns:
            if col_name in headers:
                col_idx = headers.index(col_name)
                if col_idx < len(row):
                    value = row[col_idx].strip()
                    if value and not regex.match(value):
                        errors.append(ValidationError(
                            table_index=table.get("index", 0),
                            row=row_idx,
                            column=col_name,
                            rule_id=rule["id"],
                            rule_name=rule["name"],
                            message=f"Format does not match: {pattern}",
                            severity=rule["severity"]
                        ))
    
    return errors


def validate_table(table: dict, rules: dict) -> list:
    """Validate single table"""
    all_errors = []
    
    for rule in rules.get("rules", []):
        rule_type = rule.get("type", "unknown")
        
        if rule_type == "not-empty":
            all_errors.extend(validate_not_empty(table, rule))
        elif rule_type == "allowed-values":
            all_errors.extend(validate_allowed_values(table, rule))
        elif rule_type == "pattern":
            all_errors.extend(validate_pattern(table, rule))
        # conditional and cross-reference require more complex logic, handled by AI
    
    return all_errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate table content",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("tables_json", help="Table JSON file (generated by extract_tables.py)")
    parser.add_argument("--rules", "-r", required=True, help="Rules directory path")
    parser.add_argument("--glossary", "-g", help="Glossary file path")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Read table data
    tables_data = json.loads(Path(args.tables_json).read_text(encoding="utf-8"))
    
    # Load rules
    rules_list = load_rules_from_directory(args.rules)
    
    # Validate each table
    results = {
        "source_file": tables_data.get("source_file"),
        "chapter": tables_data.get("chapter"),
        "validation_results": []
    }
    
    for table in tables_data.get("tables", []):
        # Match rules
        matched_rules = match_table_to_rules(table, rules_list)
        
        table_result = {
            "table_index": table.get("index"),
            "headers": table.get("headers"),
            "matched_rules": matched_rules.get("source_file") if matched_rules else None,
            "errors": [],
            "warnings": []
        }
        
        if matched_rules:
            errors = validate_table(table, matched_rules)
            for error in errors:
                error_dict = asdict(error)
                if error.severity == "error":
                    table_result["errors"].append(error_dict)
                else:
                    table_result["warnings"].append(error_dict)
        
        results["validation_results"].append(table_result)
    
    # Output result
    output_json = json.dumps(results, ensure_ascii=False, indent=2)
    
    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        
        # Statistics
        total_errors = sum(len(r["errors"]) for r in results["validation_results"])
        total_warnings = sum(len(r["warnings"]) for r in results["validation_results"])
        print(f"Validation complete: {total_errors} error(s), {total_warnings} warning(s)")
        print(f"Results saved to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
