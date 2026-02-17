
import unittest
import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parents[2] / "scripts"))

from validate_table import (
    parse_markdown_rules, 
    match_table_to_rules, 
    validate_not_empty, 
    validate_allowed_values, 
    validate_pattern, 
    ValidationError
)

class TestValidateTable(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_parse_markdown_rules(self):
        markdown_content = """
## Table Matcher
- Column A
- Column B

## Validation Rules

### Rule 1 [ERROR]
- Column A
Field must be not empty.

### Rule 2 [WARNING]
- Column B
Allowed values:
- Value 1
- Value 2
        """
        parsed = parse_markdown_rules(markdown_content)
        
        # Test Matcher
        self.assertEqual(parsed["table_matcher"]["columns"], ["Column A", "Column B"])
        
        # Test Rules
        self.assertEqual(len(parsed["rules"]), 2)
        
        rule1 = parsed["rules"][0]
        self.assertEqual(rule1["name"], "Rule 1")
        self.assertEqual(rule1["severity"], "error")
        self.assertEqual(rule1["type"], "not-empty")
        self.assertEqual(rule1["config"]["columns"], ["Column A"])

        rule2 = parsed["rules"][1]
        self.assertEqual(rule2["name"], "Rule 2")
        self.assertEqual(rule2["severity"], "warning")
        self.assertEqual(rule2["type"], "allowed-values")
        self.assertEqual(rule2["config"]["columns"], ["Column B", "Value 1", "Value 2"])
        self.assertEqual(rule2["config"]["values"], ["Column B", "Value 1", "Value 2"])

    def test_match_table_to_rules(self):
        rules_list = [
            {
                "source_file": "rules1.md",
                "table_matcher": {"columns": ["Col A", "Col B"]},
                "rules": []
            },
            {
                "source_file": "rules2.md",
                "table_matcher": {"columns": ["Col C"]},
                "rules": []
            }
        ]

        # Match exact
        table1 = {"headers": ["Col A", "Col B", "Other"]}
        matched1 = match_table_to_rules(table1, rules_list)
        self.assertIsNotNone(matched1)
        self.assertEqual(matched1["source_file"], "rules1.md")

        # Match subset
        table2 = {"headers": ["Col C", "Extra"]}
        matched2 = match_table_to_rules(table2, rules_list)
        self.assertIsNotNone(matched2)
        self.assertEqual(matched2["source_file"], "rules2.md")

        # No match
        table3 = {"headers": ["Col Z"]}
        matched3 = match_table_to_rules(table3, rules_list)
        self.assertIsNone(matched3)

    def test_validate_not_empty(self):
        rule = {
            "id": "rule-1",
            "name": "Test Rule",
            "severity": "error",
            "type": "not-empty",
            "config": {"columns": ["Col A"]}
        }
        
        table = {
            "index": 1,
            "headers": ["Col A", "Col B"],
            "rows": [
                ["Value", "Ok"],   # Row 2 (1-based index from enumerate start=2)
                ["", "Empty"],     # Row 3 - Error
                ["   ", "Space"]   # Row 4 - Error
            ]
        }

        errors = validate_not_empty(table, rule)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].row, 3)
        self.assertEqual(errors[1].row, 4)

    def test_validate_allowed_values(self):
        rule = {
            "id": "rule-2",
            "name": "Test Values",
            "severity": "error",
            "type": "allowed-values",
            "config": {
                "columns": ["Col A"],
                "values": ["Yes", "No"]
            }
        }

        table = {
            "index": 1,
            "headers": ["Col A"],
            "rows": [
                ["Yes"],      # OK
                ["No"],       # OK
                ["Maybe"],    # Error
                [""]          # OK (empty handled by not-empty)
            ]
        }
        
        errors = validate_allowed_values(table, rule)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].row, 4)
        self.assertEqual(errors[0].message, 'Value "Maybe" not in allowed values list')

    def test_validate_pattern(self):
        rule = {
            "id": "rule-3",
            "name": "Test Pattern",
            "severity": "error",
            "type": "pattern",
            "config": {
                "columns": ["Date"],
                "pattern": r"^\d{4}-\d{2}-\d{2}$"
            }
        }

        table = {
            "index": 1,
            "headers": ["Date"],
            "rows": [
                ["2023-01-01"], # OK
                ["2023/01/01"], # Error
                ["invalid"],    # Error
                [""]            # OK (empty handled by not-empty)
            ]
        }

        errors = validate_pattern(table, rule)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].row, 3)
        self.assertEqual(errors[1].row, 4)

if __name__ == "__main__":
    unittest.main()
