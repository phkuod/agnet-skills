#!/usr/bin/env python3
"""
validate_table.py - Validate table content
"""

import argparse
import json
import re
import sys
import os
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List


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


def parse_markdown_rules(md_content: str) -> dict:
    """
    Parse Markdown format rule file with YAML frontmatter
    """
    result = {
        "id": None,
        "title": None,
        "script": None,
        "table_matcher": {"columns": [], "match_mode": "contains", "column_pattern": None, "section_pattern": None},
        "rules": []
    }
    
    # Parse YAML frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', md_content, re.DOTALL)
    if frontmatter_match:
        import yaml
        try:
            fm = yaml.safe_load(frontmatter_match.group(1))
            result["id"] = fm.get("id")
            result["title"] = fm.get("title")
            result["script"] = fm.get("script")
        except:
            pass
            
    # Remove frontmatter for content parsing
    content = re.sub(r'^---\n.*?\n---\n', '', md_content, flags=re.DOTALL)
    lines = content.split('\n')
    
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
            if line_stripped.startswith('```'):
                if in_code_block:
                    in_code_block = False
                    in_matcher_yaml = False
                    in_columns_list = False
                else:
                    in_code_block = True
                    if 'yaml' in line_stripped:
                        in_matcher_yaml = True
                continue
            
            if in_code_block and in_matcher_yaml:
                if re.match(r'^\s*columns:', line_stripped):
                    inline_match = re.match(r'^\s*columns:\s*\[(.+)\]', line_stripped)
                    if inline_match:
                        cols = [c.strip().strip("'\"") for c in inline_match.group(1).split(',')]
                        result["table_matcher"]["columns"].extend(cols)
                    else:
                        in_columns_list = True
                    continue
                
                if in_columns_list:
                    yaml_item = re.match(r'^\s*-\s+(.+)$', line_stripped)
                    if yaml_item:
                        col = yaml_item.group(1).strip().strip("'\"")
                        result["table_matcher"]["columns"].append(col)
                    elif line_stripped and not line_stripped.startswith('#'):
                        in_columns_list = False
                
                mode_match = re.match(r'^\s*match-mode:\s*(\S+)', line_stripped)
                if mode_match:
                    result["table_matcher"]["match_mode"] = mode_match.group(1).strip()
                    in_columns_list = False
                
                pattern_match = re.match(r"^\s*column-pattern:\s*[\"'](.+?)[\"']", line_stripped)
                if pattern_match:
                    result["table_matcher"]["column_pattern"] = pattern_match.group(1)
                    in_columns_list = False
                
                section_match = re.search(r'section-pattern:\s*["\'](.+?)["\']', line_stripped)
                if section_match:
                    result["table_matcher"]["section_pattern"] = section_match.group(1)
                    in_columns_list = False
                
                continue
            
            if not in_code_block and line_stripped.startswith('- '):
                col = line_stripped[2:].strip()
                result["table_matcher"]["columns"].append(col)
        
        # Parse rules
        elif current_section == 'rules':
            if 'exception' in line_stripped.lower():
                current_section = 'exceptions'
                continue
                
            # Default rule if none found yet
            if not current_rule and ('empty' in line_stripped.lower() or 'required' in line_stripped.lower()):
                current_rule = {
                    "id": result["id"] or "rule-1",
                    "name": result["title"] or "Rule",
                    "type": "not-empty",
                    "severity": "error",
                    "config": {"columns": [], "values": [], "description": [line_stripped]}
                }
                continue

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
                    "config": {"columns": [], "values": [], "pattern": None, "description": []}
                }
                continue
            
            if current_rule:
                if line_stripped.startswith('- '):
                    item = line_stripped[2:].strip()
                    current_rule["config"]["columns"].append(item)
                    current_rule["config"]["values"].append(item)
                
                if 'empty' in line_stripped.lower() or 'required' in line_stripped.lower():
                    current_rule["type"] = "not-empty"
                elif 'allowed' in line_stripped.lower() or 'values' in line_stripped.lower():
                    current_rule["type"] = "allowed-values"
                
                if line_stripped:
                    current_rule["config"]["description"].append(line_stripped)
    
    if current_rule:
        result["rules"].append(current_rule)
    
    return result


def load_rules_from_directory(rules_dir: str) -> list:
    rules_path = Path(rules_dir)
    all_rules = []
    for md_file in rules_path.glob("*.md"):
        if md_file.name.startswith('_'): continue
        content = md_file.read_text(encoding="utf-8")
        parsed = parse_markdown_rules(content)
        parsed["source_file"] = md_file.name
        all_rules.append(parsed)
    return all_rules


def match_table_to_rules(table: dict, rules_list: list) -> List[dict]:
    """Match applicable rules (can be multiple)"""
    table_headers = set(h.strip() for h in table.get("headers", []))
    chapter = table.get("chapter", "All")
    section = table.get("section", "All")
    
    matched = []
    for rules in rules_list:
        matcher = rules["table_matcher"]
        matcher_columns = set(matcher.get("columns", []))
        column_pattern = matcher.get("column_pattern")
        section_pattern = matcher.get("section_pattern")
        
        # Match by columns
        col_match = matcher_columns.issubset(table_headers) if matcher_columns else True
        
        # Match by column pattern
        pat_match = True
        if column_pattern:
            try:
                regex = re.compile(column_pattern)
                pat_match = any(regex.search(h) for h in table_headers)
            except: pat_match = False
        
        # Match by section
        sec_match = True
        if section_pattern:
            try:
                regex = re.compile(section_pattern, re.IGNORECASE)
                sec_match = regex.search(chapter) or regex.search(section)
            except: sec_match = False
            
        if col_match and pat_match and sec_match:
            if matcher_columns or column_pattern or section_pattern:
                matched.append(rules)
                
    return matched


def run_external_validator(script_path: str, table: dict) -> list:
    """Run an external Python validator script"""
    errors = []
    try:
        # Prepare temp file for single table
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(table, tmp)
            tmp_path = tmp.name
        
        # Run script
        script_abs_path = os.path.join(os.getcwd(), '.agent', 'skills', 'docx-validator', script_path)
        if not os.path.exists(script_abs_path):
            # Fallback to absolute if already absolute
            script_abs_path = script_path
            
        proc = subprocess.run([sys.executable, script_abs_path, tmp_path], 
                             capture_output=True, text=True, encoding='utf-8')
        
        # Cleanup
        os.unlink(tmp_path)
        
        if proc.returncode != 0:
            # Parse output lines
            for line in proc.stdout.strip().split('\n'):
                if 'Row' in line and ':' in line:
                    msg = line.split(':', 1)[1].strip()
                    # Optional: extract more details
                    errors.append(ValidationError(
                        table_index=table.get("index", 0),
                        row=0, column="Unknown", rule_id="script", rule_name="External Script",
                        message=msg, severity="error"
                    ))
    except Exception as e:
        print(f"Error running script {script_path}: {e}")
    return errors


def validate_not_empty(table: dict, rule: dict) -> list:
    errors = []
    columns = rule["config"].get("columns", [])
    headers = table.get("headers", [])
    if not columns or columns == ["All columns"]: columns = headers
    
    for row_idx, row in enumerate(table.get("rows", []), start=2):
        for col_name in columns:
            if col_name in headers:
                col_idx = headers.index(col_name)
                if col_idx < len(row):
                    val = row[col_idx].strip()
                    if not val:
                        print(f"      Found empty cell in {col_name} at row {row_idx}")
                        errors.append(ValidationError(
                            table_index=table.get("index", 0),
                            row=row_idx, column=col_name,
                            rule_id=rule.get("id", "not-empty"),
                            rule_name=rule.get("name", "Required Fields"),
                            message="Field is empty", severity="error"
                        ))
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tables_json")
    parser.add_argument("--rules", "-r", required=True)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    
    tables_data = json.loads(Path(args.tables_json).read_text(encoding="utf-8"))
    rules_list = load_rules_from_directory(args.rules)
    
    results = {"source_file": tables_data.get("source_file"), "validation_results": []}
    
    for table in tables_data.get("tables", []):
        matched_rules = match_table_to_rules(table, rules_list)
        table_result = {
            "table_index": table.get("index"),
            "section": table.get("section"),
            "errors": [],
            "warnings": []
        }
        
        for rule_file in matched_rules:
            print(f"  Table {table.get('index')} matched {rule_file['source_file']}")
            # Run external script if defined
            if rule_file.get("script"):
                ext_errors = run_external_validator(rule_file["script"], table)
                for err in ext_errors:
                    err.rule_id = rule_file.get("id") or "script"
                    err.rule_name = rule_file.get("title") or "Script"
                    table_result["errors"].append(asdict(err))
            
            # Run internal validators
            for rule in rule_file.get("rules", []):
                print(f"    Running internal rule: {rule['name']} ({rule['type']})")
                if rule["type"] == "not-empty":
                    errs = validate_not_empty(table, rule)
                    for e in errs: table_result["errors"].append(asdict(e))
        
        results["validation_results"].append(table_result)
    
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
        total = sum(len(r["errors"]) for r in results["validation_results"])
        print(f"Validation complete: {total} error(s)")
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
