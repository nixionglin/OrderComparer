#!/usr/bin/env python3
"""
对账逻辑
"""

import datetime
import math
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
from src._3rd_order.xunfeng_c_order import XunFengCOrder
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
        print(f"------------------------------------------")
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
        
        transation_order_info = transation_order.get_order_info()
        print(f"\n*************************** 流水单信息汇总 ***************************")
        print(transation_order_info)
        print()

        for admin_id in unique_admin_ids:

            # 获取指定商户获取结算期帐账户信息
            admin_details = []
            admin_info = transation_order.get_admin_info(admin_id)
            total_amount = admin_info.get('订单扣款金额')
            admin_details.append(f"账户概览：{admin_info}")

            unique_order = delivery_order.get_all_orders(admin_id)
            if unique_order is None:
                continue

            total_order_amount = 0
            for order_number in unique_order:
                order_info = delivery_order.get_admin_order_info(admin_id, order_number)
                order_amount = order_info.get('扣款金额')
                total_order_amount += order_amount
                admin_details.append(order_info)

            
            total_order_amount = round(total_order_amount, 2)
            if math.isclose(total_order_amount, total_amount):
                result = True

            print(f"\n--------------------------- 商户'{admin_id}' 对账【{'成功' if result else '失败'}】 ---------------------------")

            if result:
                print(f"配送单累计扣款：{total_order_amount}")

            for line in admin_details:
                print(line)

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


    def check_xunfengc_order(self, delivery_order_file, transation_order_file, xunfengc_order_file):
        """
        顺丰企业订单对账
        """
        order = XunFengCOrder(xunfengc_order_file)
        result = self.do_platform_check(delivery_order_file, transation_order_file, order, '顺丰企业C')
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
        total_fail_count = 0

        # 配送单、第三方平台以及流水单扣款总金额
        total_amount = round(platform_data['free'].sum(), 2)
        total_third_amount = 0
        total_transation_amount = 0

        # 配送单扣款金额汇总
        total_normal_amount = 0
        total_penalty_amount = 0
        total_penalty_count = 0
        

        # 汇总信息
        details = []
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
            if not platform in ('裹小递', '顺丰企业C'):
                third_order_info = third_orde.get_order_number_info(order_number)
            else:
                third_order_info = third_orde.get_order_number_info(platform_id)


            """
            1. 配送单与第三方平台对账
            """
            if pd.isna(third_order_info):
                total_fail_count += 1
                details.append(f"Fail: 配送单订单 '{order_number}' 在{platform}订单中未找到!")
                exception_msg.append(f"配送单订单 '{order_number}' 在{platform}订单中未找到, 该条数据对账失败！")
                continue

            # 配送表订单在第三方平台订单表扣款金额
            third_order_id = third_order_info.get('order_id')
            third_order_actual_deduction = third_order_info.get('actual_deduction')
            third_orider_status = third_order_info.get('orider_status')
            third_orider_amount = third_order_info.get('order_amount')
            third_orider_penalty = third_order_info.get('order_penalty')

            if third_orider_penalty > 0:
                total_penalty_amount += third_orider_penalty
                total_penalty_count += 1

            decution_mode = '订单违约' if third_orider_penalty > 0 else '订单完成' if third_orider_amount > 0 else '未知'

            total_third_amount += third_order_actual_deduction


            """
            2. 配送单与流水单对账
            """

            # 根据配送表订单号去流水单表中查询对应订单扣款金额
            transation_order_amount = transation_order.get_total_order_amount(admin_id, order_number)
            total_transation_amount += transation_order_amount

            total_third_amount = round(total_third_amount, 2)
            total_transation_amount = round(total_transation_amount, 2)

            check_msg = f"配送单单号:'{order_number}' 扣款: '{delivery_order_amount}'元,  {platform}平台订单 '{third_order_id}' 扣款: '{third_order_actual_deduction}'元 扣款形式:'{decution_mode}' 订单状态: '{third_orider_status}',  商户扣款: '{transation_order_amount}'元"

            # 根据分别从 delivery_order、third_order、transation_order 三张表中拿到的扣款金额，进行结果判断
            if delivery_order_amount == third_order_actual_deduction == transation_order_amount:
                total_pass_count += 1
                details.append(f"Pass: {check_msg}")
            else:
                total_fail_count += 1
                error_msg = None
                # 检查 delivery_order_amount 与 third_order_actual_deduction 是否一致
                if delivery_order_amount != third_order_actual_deduction:
                    amount_diff = round(delivery_order_amount - third_order_actual_deduction, 2)
                    error_msg = f"快小象平台{'少' if amount_diff > 0 else '多'}扣'{abs(amount_diff)}'元"
                    details.append(f"Fail: {error_msg} 【{check_msg}】")
                # 如果 delivery_order_amount 与 third_order_actual_deduction 不一致，则检查 delivery_order_amount 与 transation_order_amount
                elif delivery_order_amount != transation_order_amount:
                    amount_diff = round(delivery_order_amount - transation_order_amount, 2)
                    error_msg = f"商户流水{'少' if amount_diff > 0 else '多'}扣'{abs(amount_diff)}'元"
                    details.append(f"Fail: {error_msg} 【{check_msg}】")
                # 如果delivery_order_amount与third_order_actual_deduction和transation_order_amount都不同，则输出所有平台金额不匹配的信息
                else:
                    error_msg = '*** 在所有平台上的金额不匹配 ***'
                    details.append(f"Fail:{error_msg} 【{check_msg}】")
                
                exception_msg.append(f"{error_msg} -> {check_msg}")

        if total_amount == total_third_amount == total_transation_amount:
            result = True

        success_rate = round(total_pass_count / total_count * 100, 2) if total_count > 0 else 0

        print(f"\n*********************** {platform}平台对账结果【{'成功' if result else '失败'}】 ***********************")
        print(f"累计有效订单'{total_count}'条, 其中对账成功的有'{total_pass_count}'条，对账失败的有'{total_fail_count}'条数据，成功率：'{success_rate}%'")
        if total_penalty_count > 0:
            print(f"配送单中违约订单{total_penalty_count}笔，违约金扣款{total_penalty_amount}(元)")

        print(f"\n对账平台\t\t{total_third_amount}")
        print(f"---------------------------")
        print(f"{platform}平台\t\t{total_third_amount}")
        print(f"配送单\t\t{total_amount}")
        print(f"流水单\t\t{total_transation_amount}")

        print("\n对账明细:")
        for line in details:
            print(line)

        if result == False:
            print("\n对账失败明细:")
            for line in exception_msg:
                print(line)

        print("-------------------------------------------------------------------------")
        return result
        

def add_test(suite, test_class, method_name, *args):
    """
    添加 testcase 核心代码
    """
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


def preprocess_file():
    """
    对账相关账单文预处理
    """
    # 定义文件名映射规则（注：顺丰企业账单需要放在顺丰前）
    rename_rules = {
        '配送单': '配送单',
        '流水': '流水账单',
        '闪送': '闪送账单',
        '达达': '达达账单',
        '蜂鸟': '蜂鸟账单',
        '企业C': '顺丰企业C账单',
        '顺丰': '顺丰账单',
        '裹小递': '裹小递账单',
        'UU跑腿': 'UU跑腿账单'
    }

    # 获取data目录下的所有文件
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    files = [f for f in os.listdir(data_dir)]

    # 遍历文件，根据规则重命名
    for file in files:
        if file.endswith('.xlsx'):
            original_file_path = os.path.join(data_dir, file)
            new_file_name = None
            # 检查文件名中的关键字并应用映射规则
            for keyword, new_name in rename_rules.items():
                if keyword in file:
                    new_file_name = new_name + '.xlsx'
                    break

            if new_file_name:
                new_file_path = os.path.join(data_dir, new_file_name) # 新文件的完整路径
                os.rename(original_file_path, new_file_path) # 新文件的完整路径

def _test():
    """
    手动测试
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', '配送单7.7-7.14.xlsx')
    data_checker = DataChecker()
    summary_data = data_checker.get_delivery_order_summary(file_path)
    print(summary_data)


def main():
    preprocess_file()

    # 本地两张数据表
    delivery_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '配送单.xlsx')
    transation_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '流水账单.xlsx')

    # 第三方平台数据表
    shansong_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '闪送账单.xlsx')
    dada_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '达达账单.xlsx')
    fengniao_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '蜂鸟账单.xlsx')
    xunfeng_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '顺丰账单.xlsx')
    xunfengc_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '顺丰企业C账单.xlsx')
    guoxidi_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', '裹小递账单.xlsx')
    uu_order_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'UU跑腿账单.xlsx')


    suite = unittest.TestSuite()

    add_test(suite, DataChecker, 'delivery_order_summary', delivery_order_file)
    add_test(suite, DataChecker, 'check_admin_info', delivery_order_file, transation_order_file)
    add_test(suite, DataChecker, 'check_shansong_order', delivery_order_file, transation_order_file, shansong_order_file)
    add_test(suite, DataChecker, 'check_dada_order', delivery_order_file, transation_order_file, dada_order_file)
    add_test(suite, DataChecker, 'check_fengniao_order', delivery_order_file, transation_order_file, fengniao_order_file)
    add_test(suite, DataChecker, 'check_guoxidi_order', delivery_order_file, transation_order_file, guoxidi_order_file)
    add_test(suite, DataChecker, 'check_xunfeng_order', delivery_order_file, transation_order_file, xunfeng_order_file)
    add_test(suite, DataChecker, 'check_xunfengc_order', delivery_order_file, transation_order_file, xunfengc_order_file)
    add_test(suite, DataChecker, 'check_uu_order', delivery_order_file, transation_order_file, uu_order_file)


    suite = unittestreport.TestRunner(suite, title='订单对账报告', desc='订单对账', tester='杨晓惠', templates=1)
    suite.run(thread_count=5)
    # suite.send_email(
    #     host="smtp.163.com",
    #     port=465,
    #     user='nixionglin@163.com',
    #     password='NBSWDHHGQNIIYCAQ',
    #     to_addrs=["nixionglin@gamil.com", "yangxiaohui@kuaixiaoxiang.com", "nixionglin@126.com"],
    # )


if __name__ == "__main__":
    main()