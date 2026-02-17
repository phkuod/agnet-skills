
import unittest
import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parents[2] / "scripts"))

from generate_report import (
    generate_summary,
    get_overall_status,
    generate_table_section
)

class TestGenerateReport(unittest.TestCase):

    def test_generate_summary(self):
        results = {
            "validation_results": [
                {"errors": [1], "warnings": []},
                {"errors": [], "warnings": [1]},
                {"errors": [], "warnings": []}
            ]
        }
        summary = generate_summary(results)
        self.assertEqual(summary["total_tables"], 3)
        self.assertEqual(summary["total_errors"], 1)
        self.assertEqual(summary["total_warnings"], 1)
        self.assertEqual(summary["passed_tables"], 1)

    def test_get_overall_status(self):
        # Error case
        status_text, status_type = get_overall_status({"total_errors": 1, "total_warnings": 0})
        self.assertEqual(status_type, "error")
        self.assertIn("Found", status_text)

        # Warning case
        status_text, status_type = get_overall_status({"total_errors": 0, "total_warnings": 1})
        self.assertEqual(status_type, "warning")
        self.assertIn("Warnings", status_text)

        # Pass case
        status_text, status_type = get_overall_status({"total_errors": 0, "total_warnings": 0})
        self.assertEqual(status_type, "pass")
        self.assertIn("Passed", status_text)

    def test_generate_table_section(self):
        # Case with errors
        table_result = {
            "table_index": 1,
            "headers": ["Col1", "Col2"],
            "matched_rules": "rules.md",
            "errors": [{
                "row": 2, 
                "column": "Col1", 
                "rule_name": "Test Rule", 
                "message": "Empty field"
            }],
            "warnings": []
        }
        section = generate_table_section(table_result)
        self.assertIn("### Table 1", section)
        self.assertIn("❌", section)
        self.assertIn("| 2 | Col1 | Test Rule | Empty field | ❌ Error |", section)

        # Case with pass
        table_result_pass = {
            "table_index": 2,
            "headers": ["ColA"],
            "matched_rules": "rules.md",
            "errors": [],
            "warnings": []
        }
        section_pass = generate_table_section(table_result_pass)
        self.assertIn("✅ All checks passed", section_pass)

if __name__ == "__main__":
    unittest.main()
