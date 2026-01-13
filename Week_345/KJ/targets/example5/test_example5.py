import unittest
from example5 import numerical_letter_grade

class TestNumericalLetterGrade(unittest.TestCase):

    def test_perfect_score(self):
        self.assertEqual(numerical_letter_grade([4.0]), ["A+"])

    def test_above_thresholds(self):
        self.assertEqual(numerical_letter_grade([3.8]), ["A"])
        self.assertEqual(numerical_letter_grade([3.4]), ["A-"])
        self.assertEqual(numerical_letter_grade([3.1]), ["B+"])
        self.assertEqual(numerical_letter_grade([2.8]), ["B"])
        self.assertEqual(numerical_letter_grade([2.4]), ["B-"])
        self.assertEqual(numerical_letter_grade([2.1]), ["C+"])
        self.assertEqual(numerical_letter_grade([1.8]), ["C"])
        self.assertEqual(numerical_letter_grade([1.5]), ["C-"])
        self.assertEqual(numerical_letter_grade([1.2]), ["D+"])
        self.assertEqual(numerical_letter_grade([0.9]), ["D"])
        self.assertEqual(numerical_letter_grade([0.2]), ["D-"])

    def test_failure_case(self):
        self.assertEqual(numerical_letter_grade([0.0]), ["E"])

if __name__ == '__main__':
    unittest.main()