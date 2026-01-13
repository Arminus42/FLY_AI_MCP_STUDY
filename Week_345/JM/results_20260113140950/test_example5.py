import unittest

from example5.example5 import numerical_letter_grade

class TestNumericalLetterGrade(unittest.TestCase):

    def test_grades(self):
        self.assertEqual(numerical_letter_grade([4.0, 3.8, 3.5, 3.1, 2.8, 2.5, 2.1, 1.8, 1.4, 1.1, 0.5, 0.0]), 
                         ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E"])

if __name__ == '__main__':
    unittest.main()