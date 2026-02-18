
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

    def test_parse_yaml_code_block_matcher(self):
        """Test that parser extracts columns from YAML code blocks"""
        markdown_content = """
### Phase 1: Find Targets

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Metal Layer
  column-pattern: '\\d+°C'
  match-mode: contains
```

### Phase 2: Apply Validation

### Required Fields [ERROR]
- Metal Layer
Field must be not empty.
        """
        parsed = parse_markdown_rules(markdown_content)

        # Should extract columns from YAML code block
        self.assertIn("Metal Layer", parsed["table_matcher"]["columns"])
        # Should extract column-pattern
        self.assertEqual(parsed["table_matcher"]["column_pattern"], "\\d+°C")
        # Should extract match-mode
        self.assertEqual(parsed["table_matcher"]["match_mode"], "contains")

    def test_parse_yaml_inline_columns(self):
        """Test that parser handles inline YAML column lists"""
        markdown_content = """
## Table Matcher

```yaml
matcher:
  type: column-headers
  columns: [Risk ID, Description, Impact Level]
```

## Validation Rules

### Rule 1 [ERROR]
- Risk ID
Field must be not empty.
        """
        parsed = parse_markdown_rules(markdown_content)
        self.assertEqual(parsed["table_matcher"]["columns"], ["Risk ID", "Description", "Impact Level"])

    def test_match_table_with_column_pattern(self):
        """Test pattern-based matching for dynamic temperature headers"""
        rules_list = [
            {
                "source_file": "temp-rule.md",
                "table_matcher": {
                    "columns": ["Metal Layer"],
                    "column_pattern": "\\d+°C",
                    "match_mode": "contains"
                },
                "rules": []
            }
        ]

        # Should match: has Metal Layer + temperature columns
        table1 = {"headers": ["Metal Layer", "100°C", "120°C", "150°C", "200°C"]}
        matched1 = match_table_to_rules(table1, rules_list)
        self.assertIsNotNone(matched1)
        self.assertEqual(matched1["source_file"], "temp-rule.md")

        # Should match: different temperature set
        table2 = {"headers": ["Metal Layer", "100°C", "115°C", "175°C", "250°C"]}
        matched2 = match_table_to_rules(table2, rules_list)
        self.assertIsNotNone(matched2)

    def test_match_table_pattern_no_match(self):
        """Test that pattern doesn't match tables without temperature columns"""
        rules_list = [
            {
                "source_file": "temp-rule.md",
                "table_matcher": {
                    "columns": ["Metal Layer"],
                    "column_pattern": "\\d+°C",
                    "match_mode": "contains"
                },
                "rules": []
            }
        ]

        # No match: has Metal Layer but no temperature columns
        table1 = {"headers": ["Metal Layer", "Ea (eV)", "R² Fit"]}
        matched1 = match_table_to_rules(table1, rules_list)
        self.assertIsNone(matched1)

        # No match: has temperature columns but no Metal Layer
        table2 = {"headers": ["Parameter", "100°C", "200°C"]}
        matched2 = match_table_to_rules(table2, rules_list)
        self.assertIsNone(matched2)

        # No match: completely different table
        table3 = {"headers": ["Risk Item", "Severity"]}
        matched3 = match_table_to_rules(table3, rules_list)
        self.assertIsNone(matched3)

if __name__ == "__main__":
    unittest.main()
