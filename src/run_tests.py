import unittest
import unittestreport

class TestMathFunctions(unittest.TestCase):
    def test_compare_data(self, source_data, target_data):
        result = compare_data(source_data, target_data)
        self.assertEqual(result, "Comparison Result")
    
    def test_addition(self):
        self.assertEqual(2 + 2, 4)

    def test_subtraction(self):
        self.assertEqual(5 - 3, 2)

    def test_multiplication(self):
        self.assertEqual(3 * 4, 12)


class TestDemo(unittest.TestCase):
    def test_compare(self, source_data, target_data):
        result = compare_data(source_data, target_data)
        self.assertEqual(result, "Comparison Result")
    
    def test_add(self):
        self.assertEqual(2 + 2, 4)

    def test_sub(self):
        self.assertEqual(5 - 3, 2)

    def test_multi(self):
        self.assertEqual(3 * 4, 12)

    def test_deom(self):
        pass

if __name__ == '__main__':
    ts = unittest.TestSuite()

    testMathFunctions = unittest.makeSuite(TestMathFunctions)
    testMathFunctions._testMethodDoc = "testMathFunctions"
    ts.addTest(testMathFunctions)

    # TestDemo = TestDemo()
    # TestDemo._testMethodDoc = ""
    # ts.addTest(unittest.makeSuite(TestDemo))

    ts.addTest(TestDemo('test_'))

    runner = unittestreport.TestRunner(ts, title='自动化测试报告', desc='接口测试', tester='测试者')
    runner.run()