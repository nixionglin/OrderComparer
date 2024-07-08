import datetime
import openpyxl
import os
import pandas as pd
import warnings

from .base_order import Base3rdOrder

class UUOrder(Base3rdOrder):
    def __init__(self, file_path):
        super().__init__(file_path)
        try:
            self.order_data = pd.read_excel(file_path, engine='openpyxl')
            self.total_deduction_amount = self.get_total_order_amount() + self.get_total_penalty_amount()
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def get_total_order_amount(self):
        total_order_amount = self.order_data[self.order_data['订单状态'] == '完成']['实际支付金额'].sum()
        return round(total_order_amount, 2)

    def get_total_penalty_amount(self):
        total_penalty_amount = self.order_data[self.order_data['订单状态'] == '取消']['上门费'].sum()
        return round(total_penalty_amount, 2)

    def get_order_number_info(self, order_number):
        data = self.order_data[self.order_data['三方订单号'] == order_number]

        if not data.empty:
            order_id = data.iloc[0]['UU订单号']
            orider_status = data.iloc[0]['订单状态']
            order_amount = float(str(data.iloc[0]['实际支付金额']).replace(',', '').strip())
            order_penalty = float(str(data.iloc[0]['上门费']).replace(',', '').strip())
            actual_deduction = order_amount if orider_status == '完成' else order_penalty
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
    file_path = os.path.join(os.path.dirname(__file__), '..\..', 'data', 'UU跑腿6.24-6.30.xlsx')

    order = UUOrder(file_path)

    order_number = '3801126971233402045_d26dwblv7zf' #3901130812901951564_6gn45nx5lcj 3801126971233402045_d26dwblv7zf

    print(f"平台扣款总金额: {order.total_deduction_amount}")

    total_order_amount = order.get_total_order_amount()
    print(f"订单扣款总金额: {total_order_amount}")

    total_penalty_amount = order.get_total_penalty_amount()
    print(f"违约金总金额: {total_penalty_amount}")

    order_info = order.get_order_number_info(order_number)
    if order_info:
        print(f"平台订单信息 '{order_number}': {order_info}")
    else:
        print(f"配送单订单 '{order_number}' 未找到!")
    
    order_amount = order_info.get('actual_deduction') if not order_info == None else '订单未找到'
    print(f"订单实际扣款金额: {order_amount}")
