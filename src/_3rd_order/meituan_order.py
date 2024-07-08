import datetime
import openpyxl
import os
import pandas as pd
import warnings

from .base_order import Base3rdOrder

class MeiTuanOrder(Base3rdOrder):
    def __init__(self, file_path):
        super().__init__(file_path)
        try:
            self.order_data = pd.read_excel(file_path, engine='openpyxl')

            self.total_deduction_amount = self.get_total_order_amount() + self.get_total_order_amount()
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
    
    def get_total_order_amount(self):
        total_order_amount = 0

        return round(total_order_amount, 2)

    def get_total_penalty_amount(self):
        total_penalty_amount = 0

        return round(total_penalty_amount, 2)

    def get_order_number_info(self, order_number):
        # 配送单查找在闪送中对应数据（闪送订单'三方订单编号'后面多了一个','）
        data = self.order_data[self.order_data['三方订单编号'] == order_number + ',']

        if not data.empty:
            order_id = data.iloc[0]['订单编号']
            orider_status = data.iloc[0]['订单状态']
            order_amount = float(str(data.iloc[0]['实付金额(元)']).replace(',', '').strip())
            order_penalty = float(str(data.iloc[0]['取消单扣款金额(元)']).replace(',', '').strip())
            return {
                'order_id': order_id, #闪送订单编号
                'orider_status': orider_status, #闪送订单状态
                'order_amount': order_amount, #订单实付金额
                'order_penalty': order_penalty #订单违约金
            }
        else:
            return None


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), '..\..', 'data', '闪送6.24-6.30.xlsx')