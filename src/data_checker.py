#!/usr/bin/env python3
"""
对账逻辑
"""

import datetime
import os
import openpyxl
import pandas as pd
import unittest
import unittestreport


from src._local_order import DeliveryOrder
from src._local_order import TransationOrder

from src._3rd_order.shansong_order import ShanSongOrder
from src._3rd_order.dada_order import DaDaOrder
from src._3rd_order.fengniao_order import FengNiaoOrder
from src._3rd_order.xunfeng_order import XunFengOrder
from src._3rd_order.guoxiaodi_order import GuoXiaoDiOrder
from src._3rd_order.uu_order import UUOrder


class DataChecker(unittest.TestCase):

    def delivery_order_summary(self, delivery_order_file):
        """
        配送单各平台扣款汇总
        """
        delivery_order = DeliveryOrder(delivery_order_file)
        summary = delivery_order.get_total_platform_info()
        summary.sort(key=lambda x: x['total_amount'], reverse=True) #对扣款金额由高到低进行排序
        print("{:<6}\t{:>5}\t{:>8}".format('平台', '扣款金额', '单数'))
        for item in summary:
            print("{:<6}\t{:>8.2f}\t{:>9}".format(item['platform'], item['total_amount'], item['row_count']))
        
        pass
    
    def check_admin_info(self, delivery_order_file, transation_order_file):
        """
        流水单商户对账
        """
        result = False
        delivery_order = DeliveryOrder(delivery_order_file)
        transation_order = TransationOrder(transation_order_file)
        
        # 获取流水单中admin_id列所有值并去重，得到所有商户信息
        unique_admin_ids = transation_order.get_unique_admin_ids()
        if unique_admin_ids is None:
            self.fail("商户信息为空")
        
        for admin_id in unique_admin_ids:
            print(f"\n--------------------------- 商户'{admin_id}' 对账 ---------------------------")

            # 获取指定商户获取结算期帐账户信息
            admin_info = transation_order.get_admin_info(admin_id)
            total_amount = admin_info.get('订单扣款总额')
            print(f"账户概览：{admin_info}")

            unique_order = delivery_order.get_all_orders(admin_id)
            if unique_order is None:
                continue

            total_order_amount = 0
            for order_number in unique_order:
                order_info = delivery_order.get_admin_order_info(admin_id, order_number)
                order_amount = order_info.get('扣款金额')
                total_order_amount += order_amount
                print(order_info)
               

            if total_order_amount == total_amount:
                result = True

            print(f"商户'admin_id' 对账{'成功' if result == True else '失败'}")

        return result

    def check_shansong_order(self, delivery_order_file, transation_order_file, shansong_order_file):
        """
        闪送订单对账
        """
        order = ShanSongOrder(shansong_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, '闪送')
        self.assertTrue(result)


    def check_dada_order(self, delivery_order_file, transation_order_file, dada_order_file):
        """
        达达订单对账
        """
        order = DaDaOrder(dada_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, '达达')
        self.assertTrue(result)


    def check_fengniao_order(self, delivery_order_file, transation_order_file, fengniao_order_file):
        """
        蜂鸟订单对账
        """
        order = FengNiaoOrder(fengniao_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, '蜂鸟')
        self.assertTrue(result)


    def check_xunfeng_order(self, delivery_order_file, transation_order_file, xunfeng_order_file):
        """
        顺丰同城订单对账
        """
        order = XunFengOrder(xunfeng_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, '顺丰同城')
        self.assertTrue(result)


    def check_guoxidi_order(self, delivery_order_file, transation_order_file, guoxidi_order_file):
        """
        裹小递订单对账
        """
        order = GuoXiaoDiOrder(guoxidi_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, '裹小递')
        self.assertTrue(result)


    def check_uu_order(self, delivery_order_file, transation_order_file, uu_order_file):
        """
        UU跑腿订单对账
        """
        order = UUOrder(uu_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, 'UU跑腿')
        self.assertTrue(result)


    def do_platform_check(self, delivery_order_file, transation_order_file, third_orde, platform):
        result = False
        delivery_order = DeliveryOrder(delivery_order_file)
        transation_order = TransationOrder(transation_order_file)

        platform_data = delivery_order.get_platform_orders(platform)
        # print(summary)
    
        # 获取配送单失败直接失败
        if platform_data.empty:
            return result

        total_count = len(platform_data)
        total_pass_count = 0
        tatol_fail_count = 0

        # 配送单对应第三方平台扣款总金额
        total_amount = round(platform_data['free'].sum(), 2)
        total_third_amount = 0
        total_transation_amount = 0
        

        # 错误汇总信息
        exception_msg = []

        # 获取三方平台对应配送单中操作数据
        data = delivery_order.get_platform_orders(platform)

        # 获取操作数据订单号
        for index, row in data.iterrows():
            # print(f"delivery_order_sn: {row['delivery_order_sn']}, free: {row['free']}, platform_order_id: {row['platform_order_id']}, 发单运力: {row['发单运力']}, 配送状态: {row['配送状态']}")
            
            # 当前配送单对账订单号
            order_number = row['delivery_order_sn']
            platform_id = row['platform_order_id']

            # 当前配送单对应商户
            admin_id = row['admin_id']
        
            # 当前订单配送表中的扣款金额
            delivery_order_amount = round(row['free'], 2)

            # 根据订单号在第三方平台订单表中查找对应的订单，扣款金额以及订单状态相关信息
            if not platform == '裹小递':
                third_order_info = third_orde.get_order_number_info(order_number)
            else:
                third_order_info = third_orde.get_order_number_info(platform_id)


            """
            1. 配送单与第三方平台对账
            """
            if pd.isna(third_order_info):
                print(f"Fail: 配送单订单 '{order_number}' 在{platform}订单中未找到!")
                exception_msg.append(f"配送单订单 '{order_number}' 在{platform}订单中未找到, 该条对账失败！")
                continue

            # 配送表订单在第三方平台订单表扣款金额
            third_order_id = third_order_info.get('order_id')
            third_order_actual_deduction = third_order_info.get('actual_deduction')
            third_orider_status = third_order_info.get('orider_status')
            third_orider_amount = third_order_info.get('order_amount')
            third_orider_penalty = third_order_info.get('order_penalty')
            decution_mode = '完成扣款' if third_orider_amount > 0 else '违约金' if third_orider_penalty > 0 else '未知'

            total_third_amount += third_order_actual_deduction


            """
            2. 配送单与流水单对账
            """

            # 根据配送表订单号去流水单表中查询对应订单扣款金额
            transation_order_amount = transation_order.get_total_order_amount(admin_id, order_number)
            total_transation_amount +=transation_order_amount

            total_third_amount = round(total_third_amount, 2)
            total_transation_amount = round(total_transation_amount, 2)

            check_msg = f"配送单单号:'{order_number}' 扣款: '{delivery_order_amount}', {platform}平台订单 '{third_order_id}' 扣款: '{third_order_actual_deduction}' 扣款形式：'{decution_mode}' 订单状态：'{third_orider_status}' 商户扣款：'{transation_order_amount}'"

            # 根据分别从 delivery_order、third_order、transation_order 三张表中拿到的扣款金额，进行结果判断
            if delivery_order_amount == third_order_actual_deduction == transation_order_amount:
                total_pass_count += 1
                print(f"Pass: {check_msg}")
            else:
                tatol_fail_count += 1
                error_msg = None
                # 检查 delivery_order_amount 与 third_order_actual_deduction 是否一致
                if delivery_order_amount != third_order_actual_deduction:
                    amount_diff = round(delivery_order_amount - third_order_actual_deduction, 2)
                    error_msg = f"快小象平台{'少' if amount_diff > 0 else '多'}扣'{abs(amount_diff)}'元"
                    print(f"Fail: {error_msg} 【{check_msg}】")
                # 如果 delivery_order_amount 与 third_order_actual_deduction 不一致，则检查 delivery_order_amount 与 transation_order_amount
                elif delivery_order_amount != transation_order_amount:
                    amount_diff = round(delivery_order_amount - transation_order_amount, 2)
                    error_msg = f"商户流水{'少' if amount_diff > 0 else '多'}扣'{abs(amount_diff)}'元"
                    print(f"Fail: {error_msg} 【{check_msg}】")
                # 如果delivery_order_amount与third_order_actual_deduction和transation_order_amount都不同，则输出所有平台金额不匹配的信息
                else:
                    error_msg = '*** 在所有平台上的金额不匹配 ***'
                    print(f"Fail:{error_msg} 【{check_msg}】")
                
                exception_msg.append(f"{error_msg} -> {check_msg}")

        if total_amount == total_third_amount == total_transation_amount:
            result = True

        success_rate = round(total_pass_count / total_count * 100, 2) if total_count > 0 else 0

        print(f"---------------------- {platform}平台对账结果【{'成功' if result else '失败'}】  -------------------------")
        print(f"共计完成'{total_count}条对账', 其对账成功的有'{total_pass_count}'条，对账失败的有'{tatol_fail_count}条数据，成功率：'{success_rate}%'")
        print(f"{platform}平台累计扣款：'{total_third_amount}'元  配送表累计扣款: '{total_amount}'元  流水累计扣款：'{total_transation_amount}'元")

        if result == False:
            print("\n对账失败信息如下:")
            for line in exception_msg:
                print(line)
        print("-------------------------------------------------------------------------")
        return result
        


        
def add_test(suite, test_class, method_name, *args):
    def test_method(self):
        getattr(self, method_name)(*args)

    method = getattr(test_class, method_name)
    docstring = method.__doc__.strip() if method.__doc__ else method_name
    test_name = f'test_{method_name}'
    
    # 创建一个带有新名称的测试方法
    new_method = lambda self: test_method(self)
    new_method.__name__ = test_name
    new_method.__doc__ = docstring

    # 动态添加测试方法到测试类
    setattr(test_class, test_name, new_method)
    suite.addTest(test_class(test_name))

def _test():
    """
    手动测试
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', '配送单6.24-6.30.xlsx')
    data_checker = DataChecker()
    summary_data = data_checker.get_delivery_order_summary(file_path)
    print(summary_data)


def main():
    # 本地两张数据表
    delivery_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '配送单6.24-6.30.xlsx')
    transation_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '本地流水6.24--6.30.xlsx')

    # 第三方平台数据表
    shansong_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '闪送6.24-6.30.xlsx')
    dada_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '达达.xlsx')
    fengniao_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '蜂鸟订单6.24-6.30.xlsx')
    xunfeng_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '顺丰2024-07-06.xlsx')
    guoxidi_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '裹小递6.24-6.30.xlsx')
    uu_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'UU跑腿6.24-6.30.xlsx')


    suite = unittest.TestSuite()

    add_test(suite, DataChecker, 'delivery_order_summary', delivery_order_file)
    add_test(suite, DataChecker, 'check_admin_info', delivery_order_file, transation_order_file)
    add_test(suite, DataChecker, 'check_shansong_order', delivery_order_file, transation_order_file, shansong_order_file)
    add_test(suite, DataChecker, 'check_dada_order', delivery_order_file, transation_order_file, dada_order_file)
    add_test(suite, DataChecker, 'check_fengniao_order', delivery_order_file, transation_order_file, fengniao_order_file)
    add_test(suite, DataChecker, 'check_guoxidi_order', delivery_order_file, transation_order_file, guoxidi_order_file)
    add_test(suite, DataChecker, 'check_xunfeng_order', delivery_order_file, transation_order_file, xunfeng_order_file)
    add_test(suite, DataChecker, 'check_uu_order', delivery_order_file, transation_order_file, uu_order_file)

    suite = unittestreport.TestRunner(suite, title='订单对账报告', desc='订单对账', tester='杨晓惠')
    suite.run()


# 测试代码
if __name__ == "__main__":
    main()