
import unittest
import subprocess
import json
import os
import tempfile
import shutil
from pathlib import Path

class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.rules_dir = os.path.join(self.test_dir, "rules")
        os.makedirs(self.rules_dir)
        
        self.script_path = str(Path(__file__).parents[2] / "scripts" / "validate_table.py")
        self.report_script_path = str(Path(__file__).parents[2] / "scripts" / "generate_report.py")
        self.python_exe = sys.executable if 'sys' in globals() else "python"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_full_validation_flow(self):
        # 1. Create a dummy rule
        rule_content = """
## Table Matcher
- Test Column

## Validation Rules

### Rule Test [ERROR]
- Test Column
Field must be not empty.
        """
        params_file = os.path.join(self.rules_dir, "test-rule.md")
        with open(params_file, "w") as f:
            f.write(rule_content)

        # 2. Create dummy table input
        input_data = {
            "source_file": "test.docx",
            "chapter": "Test Chapter",
            "tables": [
                {
                    "index": 1,
                    "headers": ["Test Column", "Other"],
                    "rows": [
                        ["Value", "Ignored"],
                        ["", "Ignored"]  # Error
                    ]
                }
            ]
        }
        input_file = os.path.join(self.test_dir, "tables.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)
            
        output_file = os.path.join(self.test_dir, "results.json")

        # 3. Run the script
        cmd = [
            self.python_exe,
            self.script_path,
            input_file,
            "--rules", self.rules_dir,
            "--output", output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check return code
        self.assertEqual(result.returncode, 0, f"Script failed with stderr: {result.stderr}")
        
        # 4. robustly check output
        self.assertTrue(os.path.exists(output_file), "Output file not created")
        
        with open(output_file, "r") as f:
            output_data = json.load(f)
            
        self.assertEqual(len(output_data["validation_results"]), 1)
        res = output_data["validation_results"][0]
        self.assertEqual(len(res["errors"]), 1)
        self.assertEqual(res["errors"][0]["row"], 3) # implementation uses 1-based index starting at 2 for data rows
        self.assertEqual(res["errors"][0]["message"], "Field is empty")

        # 5. Run report generation
        report_file = os.path.join(self.test_dir, "report.md")
        cmd_report = [
            self.python_exe,
            self.report_script_path,
            output_file,
            "--output", report_file
        ]
        
        result_report = subprocess.run(cmd_report, capture_output=True, text=True)
        self.assertEqual(result_report.returncode, 0, f"Report script failed with stderr: {result_report.stderr}")
        self.assertTrue(os.path.exists(report_file), "Report file not created")
        
        with open(report_file, "r", encoding="utf-8") as f:
            report_content = f.read()
            
        self.assertIn("❌ Issues Found", report_content)
        self.assertIn("Field is empty", report_content)

if __name__ == "__main__":
    import sys
    unittest.main()
