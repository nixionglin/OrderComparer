import datetime
import openpyxl
import os
import pandas as pd
import warnings

from .base_order import Base3rdOrder

class GuoXiaoDiOrder(Base3rdOrder):
    def __init__(self, file_path):
        super().__init__(file_path)
        try:
            self.order_data = pd.read_excel(file_path, engine='openpyxl')
            self.total_deduction_amount = round(self.get_total_order_amount() + self.get_total_penalty_amount(), 2)
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def get_total_order_amount(self):
        total_order_amount = self.order_data[self.order_data['订单状态'] == '已完成']['支付金额'].sum()
        return round(total_order_amount, 2)

    def get_total_penalty_amount(self):
        total_penalty_amount = self.order_data[self.order_data['订单状态'] == '已退款']['取消订单扣款'].sum()
        return round(total_penalty_amount, 2)

    # 与其他平台不同,这里需要传裹小递的订单号
    def get_order_number_info(self, platform_id):
        data = self.order_data[self.order_data['订单号'] == platform_id]

        if not data.empty:
            order_id = data.iloc[0]['订单号']
            orider_status = data.iloc[0]['订单状态']
            order_amount = float(str(data.iloc[0]['支付金额']).replace(',', '').strip())
            order_penalty = float(str(data.iloc[0]['取消订单扣款']).replace(',', '').strip())
            actual_deduction = order_amount if orider_status == '已完成' else order_penalty
            return {
                'actual_deduction': actual_deduction, #实扣款
                'order_id': order_id, #闪送订单编号
                'orider_status': orider_status, #闪送订单状态
                'order_amount': order_amount, #订单实付金额
                'order_penalty': order_penalty #订单违约金
            }
        else:
            return None


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..\..', 'data', '裹小递6.24-6.30.xlsx')
    order = GuoXiaoDiOrder(file_path)

    # 裹小递与其他平台不一样,没有存配送单订单号,需要先通过 order_number 获取 platform_id 传入对应配送单对应的平台号
    order_number = '1901137280343929444_b6fwsusqod6' #f93z97s7zitautkyj_x4g5pjtq2je  
    platform_id = 'ON1806643109254168576'  #ON1806640525328011264
 
    print(f"平台扣款总金额: {order.total_deduction_amount}")

    total_order_amount = order.get_total_order_amount()
    print(f"订单扣款总金额: {total_order_amount}")

    total_penalty_amount = order.get_total_penalty_amount()
    print(f"违约金总金额: {total_penalty_amount}")

    order_info = order.get_order_number_info('ON1805804278829338624')
    if order_info:
        print(f"平台订单信息 '{order_number}': {order_info}")
    else:
        print(f"配送单订单 '{order_number}' 未找到!")
    
    order_amount = order_info.get('actual_deduction') if not order_info == None else '订单未找到'
    print(f"订单实际扣款金额: {order_amount}")