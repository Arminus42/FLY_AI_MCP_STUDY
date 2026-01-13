import unittest

class TestExample2(unittest.TestCase):
    
    def test_testme(self):
        self.assertIsNone(testme(0, 10, 100))  # Test within range
        self.assertIsNone(testme(0, 10, 300))  # Test c out of upper range
        self.assertIsNone(testme(0, 10, 50))   # Test c out of lower range
        self.assertIsNone(testme(10, 10, 100))  # Test a equals b
        self.assertIsNone(testme(-1, 10, 100))  # Test a starts negative
        
if __name__ == '__main__':
    unittest.main()