import unittest # 테스트를 작성하고 실행하기 위한 도구 모음

class TestExample1(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(foo(42, 0), 1)
        self.assertEqual(foo(42, 1), 0)
        self.assertEqual(foo(0, 0), -1)

    def test_bar(self):
        self.assertEqual(bar(10, 20, 15), 15)
        self.assertEqual(bar(20, 10, 15), 20)
        self.assertEqual(bar(5, 5, 5), 5)

if __name__ == '__main__':
    unittest.main()