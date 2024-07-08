import datetime
import openpyxl
import os
import pandas as pd
import warnings

from .base_order import Base3rdOrder

class ShanSongOrder(Base3rdOrder):

    def __init__(self, file_path):
        super().__init__(file_path)
        try:
            self.summary_data = pd.read_excel(file_path, engine='openpyxl', sheet_name='汇总信息')
            self.order_data = pd.read_excel(file_path, engine='openpyxl', sheet_name='订单明细')

            self.total_deduction_amount = self.get_total_order_amount() + self.get_total_penalty_amount()
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def get_total_order_amount(self):
        total_order_amount = 0
        if 'D7' in self.summary_data:
            total_order_amount = round(float(self.summary_data['D7']), 2)
        else:
            total_order_amount = self.order_data[self.order_data['订单状态'] == '闪送完成']['实付金额(元)'].sum()
        return round(total_order_amount, 2)

    def get_total_penalty_amount(self):
        total_penalty_amount = 0
        if 'D5' in self.summary_data:
            total_penalty_amount = float(self.summary_data['D5'])
        else:
            total_penalty_amount = self.order_data[self.order_data['订单状态'] == '已取消']['取消单扣款金额(元)'].sum()
        return round(total_penalty_amount, 2)

    def get_order_number_info(self, order_number):
        # 配送单查找在闪送中对应数据（闪送订单'三方订单编号'后面多了一个','）
        data = self.order_data[self.order_data['三方订单编号'] == order_number + ',']

        if data is not None and not data.empty:
            order_id = data.iloc[0]['订单编号']
            orider_status = data.iloc[0]['订单状态']
            order_amount = float(str(data.iloc[0]['实付金额(元)']).replace(',', '').strip())
            order_penalty = float(str(data.iloc[0]['取消单扣款金额(元)']).replace(',', '').strip())
            actual_deduction = order_amount if orider_status == '闪送完成' else order_penalty
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
    file_path = os.path.join(os.path.dirname(__file__), '..\..', 'data', '闪送6.24-6.30.xlsx')

    order = ShanSongOrder(file_path)

    order_number = '301129501929050300_m35i2p404mn' #f7hef0txw4dsvm764_amp2tvxd6qh

    print(f"平台扣款总金额: {order.total_deduction_amount}")

    total_order_amount = order.get_total_order_amount()
    print(f"订单扣款总金额: {total_order_amount}")

    total_penalty_amount = order.get_total_penalty_amount()
    print(f"违约金总金额: {total_penalty_amount}")

    order_info = order.get_order_number_info(order_number)
    if order_info:
        print(f"Order Info for order number '{order_number}': {order_info}")
    else:
        print(f"配送单订单 '{order_number}' 在闪送订单中不存在!")
    
    order_amount = order_info.get('actual_deduction') if not order_info == None else '订单未找到'
    print(f"订单实际扣款金额: {order_amount}")



