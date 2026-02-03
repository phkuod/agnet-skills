#!/usr/bin/env python3
"""
table_temperature_descending.py - 溫度遞減順序驗證

規則：當 Temperature 越高，攝氏溫度值應越低（遞減排序）

用法：
    python validators/table_temperature_descending.py <table_json>
    
    # 或作為模組使用
    from validators.table_temperature_descending import validate
    errors = validate(table_data)
"""

import json
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationError:
    """驗證錯誤"""
    row: int
    column: str
    message: str
    severity: str = "error"
    rule_id: str = "table-temperature-descending"
    rule_name: str = "溫度遞減順序檢查"


def parse_number(value: str) -> Optional[float]:
    """解析數值，無法解析時返回 None"""
    if not value or not value.strip():
        return None
    try:
        # 移除常見的非數字字符
        cleaned = value.strip().replace(',', '').replace(' ', '')
        return float(cleaned)
    except ValueError:
        return None


def validate(table: dict) -> List[ValidationError]:
    """
    驗證表格的溫度遞減順序
    
    Args:
        table: 表格資料，格式：
            {
                "headers": ["Temperature", "攝氏溫度值"],
                "rows": [["100", "80"], ["80", "60"], ...]
            }
    
    Returns:
        驗證錯誤列表
    """
    errors = []
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    
    # 找到目標欄位索引
    temp_col_idx = None
    celsius_col_idx = None
    
    for i, header in enumerate(headers):
        header_lower = header.strip().lower()
        if header_lower == "temperature":
            temp_col_idx = i
        elif "攝氏溫度值" in header or "攝氏" in header:
            celsius_col_idx = i
    
    if temp_col_idx is None or celsius_col_idx is None:
        # 無法匹配到必要欄位，規則不適用
        return []
    
    # 收集有效的資料點 (排除空值和非數值)
    data_points = []
    for row_idx, row in enumerate(rows, start=2):  # 從第2行開始（第1行是表頭）
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
        # 資料點不足，無法驗證順序
        return []
    
    # 依 Temperature 由高到低排序
    sorted_points = sorted(data_points, key=lambda x: x["temperature"], reverse=True)
    
    # 檢查排序後的 celsius 是否遞減
    for i in range(1, len(sorted_points)):
        prev = sorted_points[i - 1]
        curr = sorted_points[i]
        
        # 如果 Temperature 降低，但 celsius 升高，則違反規則
        if prev["temperature"] > curr["temperature"]:
            if curr["celsius"] > prev["celsius"]:
                errors.append(ValidationError(
                    row=curr["row"],
                    column="攝氏溫度值",
                    message=f"溫度從 {prev['temperature']} 降到 {curr['temperature']}，"
                           f"但攝氏溫度值從 {prev['celsius']} 升到 {curr['celsius']}，"
                           f"應呈現遞減趨勢",
                    severity="error"
                ))
    
    return errors


def validate_from_json(json_path: str) -> List[dict]:
    """從 JSON 檔案載入表格並驗證"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_errors = []
    
    # 處理單個表格或多個表格
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
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python table_temperature_descending.py <table_json>")
        print("範例: python table_temperature_descending.py tables.json")
        sys.exit(1)
    
    json_path = sys.argv[1]
    errors = validate_from_json(json_path)
    
    if errors:
        print(f"發現 {len(errors)} 個錯誤:")
        for error in errors:
            print(f"  行 {error['row']}: {error['message']}")
        sys.exit(1)
    else:
        print("✅ 驗證通過：溫度遞減順序正確")
        sys.exit(0)


if __name__ == "__main__":
    main()
