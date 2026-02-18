
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parents[2]))

from validators.table_temperature_descending import validate

class TestTableTemperatureDescending(unittest.TestCase):
    
    def test_positive_case(self):
        # Standard case: Temp decreases, Cels decreases -> Pass
        table = {
            "headers": ["Temperature", "Celsius Value"],
            "rows": [
                ["100", "37.7"],
                ["80", "26.6"],
                ["60", "15.5"]
            ]
        }
        errors = validate(table)
        self.assertEqual(len(errors), 0)

    def test_negative_case(self):
        # Error case: Temp decreases (80->60), but Cels INCREASES (26.6->30.0)
        table = {
            "headers": ["Temperature", "Celsius Value"],
            "rows": [
                ["100", "37.7"],
                ["80", "26.6"],
                ["60", "30.0"] 
            ]
        }
        errors = validate(table)
        self.assertEqual(len(errors), 1)
        self.assertIn("increased", errors[0].message)
        self.assertEqual(errors[0].row, 4) # 1-based index (Header=1, Row1=2, Row2=3, Row3=4)

    def test_missing_columns(self):
        # Columns not found -> No validation performed -> No errors
        table = {
            "headers": ["A", "B"],
            "rows": [["1", "2"]]
        }
        errors = validate(table)
        self.assertEqual(len(errors), 0)

    def test_unsorted_input(self):
        # Validator sorts input by Temperature first.
        # Temp: 60, 100, 80.
        # Sorted: 100, 80, 60.
        # Cels: 15, 37, 26.
        # Sorted Cels (corresponding to Temp): 37, 26, 15.
        # 37->26 (Decr), 26->15 (Decr). -> Pass.
        table = {
            "headers": ["Temperature", "Celsius Value"],
            "rows": [
                ["60", "15.5"],
                ["100", "37.7"],
                ["80", "26.6"]
            ]
        }
        errors = validate(table)
        self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
