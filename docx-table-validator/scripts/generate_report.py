#!/usr/bin/env python3
"""
generate_report.py - 產生 Markdown 驗證報告

用法：
    python generate_report.py <results_json> --output <output_file>
    
範例：
    python generate_report.py results.json --output report.md
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def generate_summary(results: dict) -> dict:
    """產生摘要統計"""
    validation_results = results.get("validation_results", [])
    
    total_tables = len(validation_results)
    total_errors = sum(len(r.get("errors", [])) for r in validation_results)
    total_warnings = sum(len(r.get("warnings", [])) for r in validation_results)
    passed_tables = sum(1 for r in validation_results 
                       if not r.get("errors") and not r.get("warnings"))
    
    return {
        "total_tables": total_tables,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "passed_tables": passed_tables
    }


def get_overall_status(summary: dict) -> tuple:
    """取得整體狀態"""
    if summary["total_errors"] > 0:
        return "❌ 發現問題", "error"
    elif summary["total_warnings"] > 0:
        return "⚠️ 有警告", "warning"
    else:
        return "✅ 全部通過", "pass"


def generate_table_section(table_result: dict) -> str:
    """產生單個表格的報告區塊"""
    table_index = table_result.get("table_index", "?")
    headers = table_result.get("headers", [])
    errors = table_result.get("errors", [])
    warnings = table_result.get("warnings", [])
    matched_rules = table_result.get("matched_rules", "無")
    
    # 決定狀態圖示
    if errors:
        status_icon = "❌"
    elif warnings:
        status_icon = "⚠️"
    else:
        status_icon = "✅"
    
    # 表格名稱（使用欄位組合）
    table_name = "、".join(headers[:3]) if headers else "未知表格"
    if len(headers) > 3:
        table_name += "..."
    
    lines = [
        f"### 表格 {table_index}：{table_name} {status_icon}",
        "",
        f"**識別欄位**: {', '.join(headers)}",
        f"**套用規則**: {matched_rules}",
        ""
    ]
    
    if errors or warnings:
        lines.extend([
            "| 行號 | 欄位 | 規則 | 問題 | 嚴重程度 |",
            "|------|------|------|------|----------|"
        ])
        
        for error in errors:
            lines.append(
                f"| {error['row']} | {error['column']} | {error['rule_name']} | {error['message']} | ❌ Error |"
            )
        
        for warning in warnings:
            lines.append(
                f"| {warning['row']} | {warning['column']} | {warning['rule_name']} | {warning['message']} | ⚠️ Warning |"
            )
    else:
        lines.append("✅ 所有檢查通過")
    
    lines.append("")
    return "\n".join(lines)


def generate_report(results: dict) -> str:
    """產生完整報告"""
    source_file = results.get("source_file", "unknown.docx")
    chapter = results.get("chapter", "未指定")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = generate_summary(results)
    overall_status, _ = get_overall_status(summary)
    
    # 報告標頭
    report_lines = [
        "# 📋 文件驗證報告",
        "",
        f"**文件**: `{source_file}`",
        f"**章節**: {chapter}",
        f"**驗證時間**: {timestamp}",
        f"**驗證結果**: {overall_status}",
        "",
        "---",
        "",
        "## 📊 摘要",
        "",
        "| 項目 | 數量 |",
        "|------|------|",
        f"| 驗證表格數 | {summary['total_tables']} |",
        f"| ❌ 錯誤 (Error) | {summary['total_errors']} |",
        f"| ⚠️ 警告 (Warning) | {summary['total_warnings']} |",
        f"| ✅ 通過 | {summary['passed_tables']} |",
        "",
        "---",
        "",
        "## 📑 詳細結果",
        ""
    ]
    
    # 各表格結果
    for table_result in results.get("validation_results", []):
        report_lines.append(generate_table_section(table_result))
    
    # 報告結尾
    report_lines.extend([
        "---",
        "",
        f"*報告產生於 {timestamp}*"
    ])
    
    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="產生 Markdown 驗證報告",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("results_json", help="驗證結果 JSON 檔案（由 validate_table.py 產生）")
    parser.add_argument("--template", "-t", help="報告模板檔案（可選）")
    parser.add_argument("--output", "-o", help="輸出 Markdown 檔案路徑")
    
    args = parser.parse_args()
    
    # 讀取驗證結果
    results = json.loads(Path(args.results_json).read_text(encoding="utf-8"))
    
    # 產生報告
    report = generate_report(results)
    
    # 輸出
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"報告已輸出到 {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
