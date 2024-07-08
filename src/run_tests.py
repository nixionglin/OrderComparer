import os
import unittest
import unittestreport
import warnings

from unittestreport import TestRunner

class DataChecker(unittest.TestCase):
    def delivery_order_summary(self, delivery_order):
        """Test delivery order summary"""
        self.assertIsNotNone(delivery_order, "Delivery order should not be None")

    def check_shansong_order(self, delivery_order, transation_order, shansong_order):
        """Test shansong order check"""
        self.assertEqual(delivery_order, shansong_order, "Shansong order does not match delivery order")

    def check_dada_order(self, delivery_order, transation_order, dada_order):
        """Test dada order check"""
        self.assertEqual(delivery_order, dada_order, "Dada order does not match delivery order")

    def check_fengniao_order(self, delivery_order, transation_order, fengniao_order):
        """Test fengniao order check"""
        self.assertEqual(delivery_order, fengniao_order, "Fengniao order does not match delivery order")

    def check_xunfeng_order(self, delivery_order, transation_order, xunfeng_order):
        """Test xunfeng order check"""
        self.assertEqual(delivery_order, xunfeng_order, "Xunfeng order does not match delivery order")

    def check_guoxidi_order(self, delivery_order, transation_order, guoxidi_order):
        """Test guoxidi order check"""
        self.assertEqual(delivery_order, guoxidi_order, "Guoxidi order does not match delivery order")

    def check_uu_order(self, delivery_order, transation_order, uu_order):
        """Test uu order check"""
        self.assertEqual(delivery_order, uu_order, "UU order does not match delivery order")

def add_test(suite, test_class, method_name, *args):
    def test_method(self):
        getattr(self, method_name)(*args)

    method = getattr(test_class, method_name)
    docstring = method.__doc__.strip() if method.__doc__ else method_name
    test_name = f'test_{method_name}_{len(suite._tests)}'
    
    # 创建一个带有新名称的测试方法
    new_method = lambda self: test_method(self)
    new_method.__name__ = test_name
    new_method.__doc__ = docstring

    # 动态添加测试方法到测试类
    setattr(test_class, test_name, new_method)
    suite.addTest(test_class(test_name))

def main():
    # 示例变量
    delivery_order = "delivery_order_example"
    transation_order = "transation_order_example"
    shansong_order = "delivery_order_example"
    dada_order = "delivery_order_example"
    fengniao_order = "delivery_order_example"
    xunfeng_order = "delivery_order_example"
    guoxidi_order = "delivery_order_example"
    uu_order = "delivery_order_example"

    # 创建测试套件
    suite = unittest.TestSuite()

    # 动态添加测试用例
    add_test(suite, DataChecker, 'delivery_order_summary', delivery_order)
    add_test(suite, DataChecker, 'check_shansong_order', delivery_order, transation_order, shansong_order)
    add_test(suite, DataChecker, 'check_dada_order', delivery_order, transation_order, dada_order)
    add_test(suite, DataChecker, 'check_fengniao_order', delivery_order, transation_order, fengniao_order)
    add_test(suite, DataChecker, 'check_xunfeng_order', delivery_order, transation_order, xunfeng_order)
    add_test(suite, DataChecker, 'check_guoxidi_order', delivery_order, transation_order, guoxidi_order)
    add_test(suite, DataChecker, 'check_uu_order', delivery_order, transation_order, uu_order)

    # 使用unittestreport运行测试并生成报告
    runner = TestRunner(suite, title='订单对账报告', desc='订单对账', tester='测试者')
    runner.run()

if __name__ == '__main__':
    main()