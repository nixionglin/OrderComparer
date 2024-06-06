import unittest
import unittestreport

class TestMathFunctions(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(2 + 2, 4)

    def test_subtraction(self):
        self.assertEqual(5 - 3, 2)

    def test_multiplication(self):
        self.assertEqual(3 * 4, 12)

if __name__ == '__main__':
    ts = unittest.TestSuite()
    ts.addTest(unittest.makeSuite(TestMathFunctions))

    runner = unittestreport.TestRunner(ts, title='自动化测试报告', desc='接口测试', tester='测试者')
    runner.run()