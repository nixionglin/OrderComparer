# _local_order/delivery_order.py
import openpyxl
import os
import pandas as pd
import numpy as np
import warnings

# 配送单类
class DeliveryOrder:

    def __init__(self, file_path):
        try:
            if not file_path or not os.path.isfile(file_path):
                print("配送单文件不存在，请检查！")
            
            warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl.styles.stylesheet')
            self.data = pd.read_excel(file_path, engine='openpyxl')
            self.platforms = self.data['发单运力'].dropna().unique()
        except Exception as e:
            print(f"读取配送单文件时发生错误: {e}")

    def get_valid_data(self):
        return self.data[(self.data['配送状态'] == '配送完成') & (self.data['delivery_channel'] == 0)]

     # 获取配送单所有第三方平台扣款概览
    def get_total_platform_info(self):
        valid_data = self.get_valid_data()
        total_row_count = len(valid_data)

        platform_info = []
        for platform in self.platforms:
            platform_data = valid_data[valid_data['发单运力'] == platform]
            platform_row_count = len(platform_data)
            platform_total_amount = round(platform_data['free'].sum(), 2)
            platform_info.append(self.getl_platform_info(platform))

        return platform_info


    # 获取配送单指定第三方平台信息概览
    def getl_platform_info(self, platform):
        if not platform in self.platforms:
            print("输入的查询平台不存在!")

        valid_data = self.get_valid_data()
        platform_data = valid_data[valid_data['发单运力'] == platform]
        platform_row_count = len(platform_data)
        platform_total_amount = round(platform_data['free'].sum(), 2)

        return {
            'platform': platform, #对应平台
            'row_count': platform_row_count, #有效订单数
            'total_amount': platform_total_amount #平台总订单扣款
        }


    # 获取配送单中指定平台有效对账数据
    def get_platform_orders(self, platform):
        if not platform in self.platforms:
            print("输入的查询平台'{platform}'不存在!")
        
        valid_data = self.get_valid_data()
        return valid_data[valid_data['发单运力'] == platform]


    # 获取指定订单号扣款金额
    def get_order_number_amount(self, order_number):
        valid_data = self.get_valid_data()
        order_data = valid_data[valid_data['delivery_order_sn'] == order_number]
        return round(order_data['free'].sum(), 2) if not order_data.empty else 0


    # 根据配送单订单号获取对应裹小递订单号
    def get_platform_id_by_order(self, order_number):
        order_data = self.data[self.data['delivery_order_sn'] == order_number]
        return order_data['platform_order_id'].values[0] if not order_data.empty else None


     # 获取商户订单扣款总金额
    def get_total_admin_amount(self, admin_id):
        valid_data = self.get_valid_data()
        order_data = valid_data[valid_data['admin_id'] == admin_id]
        return round(order_data['free'].sum(), 2) if not order_data.empty else 0


    # 获取指定商户指定订单扣款信息
    def get_admin_order_info(self, admin_id, order_number):
        valid_data = self.get_valid_data()
        order_data = valid_data[valid_data['delivery_order_sn'] == order_number]
        dispatch_platform = order_data['发单运力'].str.strip().values[0] if not order_data['发单运力'].empty else '未知'
        order_status = order_data['配送状态'].values[0] if not order_data.empty else "非完成状态"
        order_amount = order_data['free'].values[0] if not order_data.empty else 0
        return {
            '配送单订单': order_number,
            '发单运力：': dispatch_platform,
            '配送状态': order_status,
            '扣款金额': float(format(order_amount, '.2f'))
        }


    # 获取指定商户所有订单号
    def get_all_orders(self, admin_id):
        valid_data = self.data[self.data['delivery_channel'] == 0]
        return valid_data[valid_data['admin_id'] == admin_id]["delivery_order_sn"].dropna().unique()


# 测试代码
if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..\..', 'data', '配送单7.7-7.14.xlsx')

    order = DeliveryOrder(file_path)

    # platform_info = order.get_total_platform_info()
    # print(f"配送单平台信息概览 {platform_info}")

    # platform_id = order.get_platform_id_by_order('4501132601061125993_mi94k0e84oy')
    # print(f"指定的订单号对应的平台号是 '{platform_id}'")

    # print(order.data[order.data['admin_id'] == 2321])


    # admin_amount = order.data[(order.data['admin_id'] == 3787) & (order.data['配送状态'] == '配送完成') & (order.data['delivery_channel'] == 0)]['free'].sum()
    # admin_amount = order.get_total_admin_amount(3787)
    # print(f"指定商户总扣款金额 '{admin_amount}'")

    # all_orders = order.get_all_order_by_admin(3787)
    # print(f"指定商户订单 '{all_orders}'")

    import numpy as np

    value = np.float64(370.0)
    formatted_value = format(value, '.2f')  # 使用format函数
    print(formatted_value)  # 输出: '370.00'

