#!/usr/bin/env python3
"""
extract_tables.py - 從 DOCX 文件中提取指定章節的表格

用法：
    python extract_tables.py <docx_file> --chapter <chapter_number> --output <output_file>
    
範例：
    python extract_tables.py document.docx --chapter 10 --output tables.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    print("錯誤：需要安裝 python-docx 套件")
    print("請執行：pip install python-docx")
    sys.exit(1)


def find_chapter_start(doc: Document, chapter_number: int) -> int:
    """
    找到指定章節的起始段落索引
    
    Args:
        doc: Word 文件物件
        chapter_number: 章節編號
        
    Returns:
        段落索引，找不到時返回 -1
    """
    patterns = [
        rf'^{chapter_number}[\.\s]',          # "10." 或 "10 "
        rf'^第\s*{chapter_number}\s*章',      # "第10章"
        rf'^Chapter\s*{chapter_number}\b',    # "Chapter 10"
    ]
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return i
    return -1


def find_chapter_end(doc: Document, start_index: int, chapter_number: int) -> int:
    """
    找到章節的結束位置（下一章節的開始或文件結尾）
    
    Args:
        doc: Word 文件物件
        start_index: 當前章節起始索引
        chapter_number: 當前章節編號
        
    Returns:
        結束段落索引
    """
    next_chapter = chapter_number + 1
    patterns = [
        rf'^{next_chapter}[\.\s]',
        rf'^第\s*{next_chapter}\s*章',
        rf'^Chapter\s*{next_chapter}\b',
    ]
    
    for i in range(start_index + 1, len(doc.paragraphs)):
        text = doc.paragraphs[i].text.strip()
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return i
    
    return len(doc.paragraphs)


def extract_table_data(table: Table) -> dict:
    """
    提取表格資料
    
    Args:
        table: Word 表格物件
        
    Returns:
        包含 headers 和 rows 的字典
    """
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(cells)
    
    if not rows:
        return {"headers": [], "rows": []}
    
    return {
        "headers": rows[0],
        "rows": rows[1:] if len(rows) > 1 else []
    }


def get_chapter_title(doc: Document, para_index: int) -> str:
    """取得章節標題"""
    if 0 <= para_index < len(doc.paragraphs):
        return doc.paragraphs[para_index].text.strip()
    return ""


def extract_tables_from_chapter(docx_path: str, chapter_number: int) -> dict:
    """
    從指定章節提取所有表格
    
    Args:
        docx_path: DOCX 檔案路徑
        chapter_number: 章節編號
        
    Returns:
        包含所有表格資料的字典
    """
    doc = Document(docx_path)
    
    # 找到章節範圍
    start_idx = find_chapter_start(doc, chapter_number)
    if start_idx == -1:
        return {
            "source_file": Path(docx_path).name,
            "chapter": f"第 {chapter_number} 章（未找到）",
            "error": f"找不到第 {chapter_number} 章",
            "tables": []
        }
    
    end_idx = find_chapter_end(doc, start_idx, chapter_number)
    chapter_title = get_chapter_title(doc, start_idx)
    
    # 取得文件的 XML 結構來定位表格位置
    # python-docx 的 tables 是全文件的，需要判斷位置
    tables_data = []
    table_index = 0
    
    # 遍歷文件的 body 元素
    body = doc.element.body
    current_para_idx = 0
    
    for element in body:
        if element.tag.endswith('p'):  # 段落
            current_para_idx += 1
        elif element.tag.endswith('tbl'):  # 表格
            if start_idx <= current_para_idx < end_idx:
                # 這個表格在目標章節內
                if table_index < len(doc.tables):
                    table = doc.tables[table_index]
                    table_data = extract_table_data(table)
                    table_data["index"] = len(tables_data) + 1
                    tables_data.append(table_data)
            table_index += 1
    
    return {
        "source_file": Path(docx_path).name,
        "chapter": chapter_title,
        "chapter_number": chapter_number,
        "tables": tables_data
    }


def extract_all_tables(docx_path: str) -> dict:
    """
    提取文件中的所有表格
    
    Args:
        docx_path: DOCX 檔案路徑
        
    Returns:
        包含所有表格資料的字典
    """
    doc = Document(docx_path)
    
    tables_data = []
    for i, table in enumerate(doc.tables):
        table_data = extract_table_data(table)
        table_data["index"] = i + 1
        tables_data.append(table_data)
    
    return {
        "source_file": Path(docx_path).name,
        "chapter": "全文件",
        "tables": tables_data
    }


def main():
    parser = argparse.ArgumentParser(
        description="從 DOCX 文件中提取表格",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
    # 提取第 10 章的表格
    python extract_tables.py document.docx --chapter 10 --output tables.json
    
    # 提取所有表格
    python extract_tables.py document.docx --output tables.json
        """
    )
    
    parser.add_argument("docx_file", help="DOCX 檔案路徑")
    parser.add_argument("--chapter", "-c", type=int, help="章節編號（不指定則提取全文件）")
    parser.add_argument("--output", "-o", help="輸出 JSON 檔案路徑（不指定則輸出到標準輸出）")
    
    args = parser.parse_args()
    
    # 檢查檔案是否存在
    if not Path(args.docx_file).exists():
        print(f"錯誤：找不到檔案 {args.docx_file}", file=sys.stderr)
        sys.exit(1)
    
    # 提取表格
    if args.chapter:
        result = extract_tables_from_chapter(args.docx_file, args.chapter)
    else:
        result = extract_all_tables(args.docx_file)
    
    # 輸出結果
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"已輸出到 {args.output}")
        print(f"找到 {len(result['tables'])} 個表格")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
