#!/usr/bin/env python3
"""
validate_table.py - 驗證表格內容

用法：
    python validate_table.py <tables_json> --rules <rules_dir> --output <output_file>
    
範例：
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
    """驗證錯誤"""
    table_index: int
    row: int
    column: str
    rule_id: str
    rule_name: str
    message: str
    severity: str  # "error" or "warning"


@dataclass 
class RuleDefinition:
    """規則定義"""
    id: str
    name: str
    type: str  # not-empty, allowed-values, pattern, conditional, cross-reference, glossary
    severity: str
    config: dict


def parse_markdown_rules(md_content: str) -> dict:
    """
    解析 Markdown 格式的規則檔案
    
    Returns:
        {
            "table_matcher": {"columns": [...]},
            "rules": [RuleDefinition, ...]
        }
    """
    result = {
        "table_matcher": {"columns": []},
        "rules": []
    }
    
    lines = md_content.split('\n')
    current_section = None
    current_rule = None
    rule_id = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        # 識別章節
        if line_stripped.startswith('## 表格識別'):
            current_section = 'matcher'
            continue
        elif line_stripped.startswith('## 驗證規則'):
            current_section = 'rules'
            continue
        
        # 解析表格識別
        if current_section == 'matcher':
            if line_stripped.startswith('- '):
                col = line_stripped[2:].strip()
                result["table_matcher"]["columns"].append(col)
        
        # 解析規則
        elif current_section == 'rules':
            # 規則標題: ### 規則名稱 [ERROR]
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
                # 收集規則內容
                if line_stripped.startswith('- '):
                    item = line_stripped[2:].strip()
                    current_rule["config"]["columns"].append(item)
                    current_rule["config"]["values"].append(item)
                
                # 檢測規則類型
                if '不可為空' in line_stripped or '必填' in line_stripped:
                    current_rule["type"] = "not-empty"
                elif '只能填入' in line_stripped or '允許值' in line_stripped:
                    current_rule["type"] = "allowed-values"
                elif '格式' in line_stripped and '正則' in line_stripped:
                    current_rule["type"] = "pattern"
                elif '當' in line_stripped and '時' in line_stripped:
                    current_rule["type"] = "conditional"
                elif '必須存在於' in line_stripped or '參照' in line_stripped:
                    current_rule["type"] = "cross-reference"
                elif '術語' in line_stripped:
                    current_rule["type"] = "glossary"
                
                # 提取正則表達式
                pattern_match = re.search(r'`([^^].*?)`', line_stripped)
                if pattern_match and current_rule["type"] == "pattern":
                    current_rule["config"]["pattern"] = pattern_match.group(1)
                
                # 記錄描述
                if line_stripped:
                    current_rule["config"]["description"].append(line_stripped)
    
    # 添加最後一條規則
    if current_rule:
        result["rules"].append(current_rule)
    
    return result


def load_rules_from_directory(rules_dir: str) -> list:
    """載入規則目錄中的所有規則檔案"""
    rules_path = Path(rules_dir)
    all_rules = []
    
    for md_file in rules_path.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        parsed = parse_markdown_rules(content)
        parsed["source_file"] = md_file.name
        all_rules.append(parsed)
    
    return all_rules


def match_table_to_rules(table: dict, rules_list: list) -> Optional[dict]:
    """根據表格欄位匹配適用的規則"""
    table_headers = set(h.strip() for h in table.get("headers", []))
    
    for rules in rules_list:
        matcher_columns = set(rules["table_matcher"]["columns"])
        if matcher_columns and matcher_columns.issubset(table_headers):
            return rules
    
    # 如果沒有匹配，返回 common.md 的規則（如果存在）
    for rules in rules_list:
        if rules.get("source_file") == "common.md":
            return rules
    
    return None


def validate_not_empty(table: dict, rule: dict) -> list:
    """驗證必填欄位"""
    errors = []
    columns = rule["config"]["columns"]
    headers = table.get("headers", [])
    
    # 如果沒有指定欄位，檢查所有欄位
    if not columns or columns == ["所有欄位"]:
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
                            message="欄位為空",
                            severity=rule["severity"]
                        ))
    
    return errors


def validate_allowed_values(table: dict, rule: dict) -> list:
    """驗證值域限制"""
    errors = []
    columns = rule["config"]["columns"]
    allowed_values = set(rule["config"]["values"])
    headers = table.get("headers", [])
    
    # 過濾出實際的欄位名稱（不是值域列表中的值）
    actual_columns = [c for c in columns if c in headers]
    
    if not actual_columns:
        # 如果規則描述中沒有明確欄位，嘗試從描述中提取
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
                            message=f"值 \"{value}\" 不在允許值列表中",
                            severity=rule["severity"]
                        ))
    
    return errors


def validate_pattern(table: dict, rule: dict) -> list:
    """驗證格式（正則表達式）"""
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
                            message=f"格式不符合：{pattern}",
                            severity=rule["severity"]
                        ))
    
    return errors


def validate_table(table: dict, rules: dict) -> list:
    """驗證單個表格"""
    all_errors = []
    
    for rule in rules.get("rules", []):
        rule_type = rule.get("type", "unknown")
        
        if rule_type == "not-empty":
            all_errors.extend(validate_not_empty(table, rule))
        elif rule_type == "allowed-values":
            all_errors.extend(validate_allowed_values(table, rule))
        elif rule_type == "pattern":
            all_errors.extend(validate_pattern(table, rule))
        # conditional 和 cross-reference 需要更複雜的邏輯，由 AI 處理
    
    return all_errors


def main():
    parser = argparse.ArgumentParser(
        description="驗證表格內容",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("tables_json", help="表格 JSON 檔案（由 extract_tables.py 產生）")
    parser.add_argument("--rules", "-r", required=True, help="規則目錄路徑")
    parser.add_argument("--glossary", "-g", help="術語表檔案路徑")
    parser.add_argument("--output", "-o", help="輸出 JSON 檔案路徑")
    
    args = parser.parse_args()
    
    # 讀取表格資料
    tables_data = json.loads(Path(args.tables_json).read_text(encoding="utf-8"))
    
    # 載入規則
    rules_list = load_rules_from_directory(args.rules)
    
    # 驗證每個表格
    results = {
        "source_file": tables_data.get("source_file"),
        "chapter": tables_data.get("chapter"),
        "validation_results": []
    }
    
    for table in tables_data.get("tables", []):
        # 匹配規則
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
    
    # 輸出結果
    output_json = json.dumps(results, ensure_ascii=False, indent=2)
    
    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        
        # 統計
        total_errors = sum(len(r["errors"]) for r in results["validation_results"])
        total_warnings = sum(len(r["warnings"]) for r in results["validation_results"])
        print(f"驗證完成：{total_errors} 個錯誤, {total_warnings} 個警告")
        print(f"結果已輸出到 {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
