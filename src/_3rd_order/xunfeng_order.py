import datetime
import openpyxl
import os
import pandas as pd
import warnings

from openpyxl import load_workbook
from .base_order import Base3rdOrder

class XunFengOrder(Base3rdOrder):

    def __init__(self, file_path):
        try:
            super().__init__(file_path)

            self.check_and_delete_first_row_if_needed(file_path)
            self.order_data = pd.read_excel(file_path, engine='openpyxl')
     
            self.total_deduction_amount = self.get_total_order_amount() + self.get_total_penalty_amount()
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def check_and_delete_first_row_if_needed(self, file_path):
        workbook = load_workbook(file_path)
        sheet = workbook.active

        a1_value = sheet['A1'].value
        if a1_value != "顺丰订单号":
            sheet.delete_rows(1)
 
            merged_cell_ranges = list(sheet.merged_cells.ranges)
            for merged_cell in merged_cell_ranges:
                if merged_cell.min_row == 1:  # 检查是否是现在的第一行（原来的第二行）
                    sheet.merged_cells.remove(merged_cell)

            workbook.save(file_path)

        workbook.close()
    
    def get_total_order_amount(self):
        total_order_amount = self.order_data[self.order_data['订单状态'] == '已完成']['配送费总价(单位元)'].sum()
        return round(total_order_amount, 2)

    def get_total_penalty_amount(self):
        total_penalty_amount = self.order_data[self.order_data['订单状态'] == '已取消']['订单取消费(单位元)'].sum()
        return round(total_penalty_amount, 2)

    def get_order_number_info(self, order_number):
        data = self.order_data[self.order_data['商家订单号'] == order_number]

        if not data.empty:
            order_id = data.iloc[0]['顺丰订单号']
            orider_status = data.iloc[0]['订单状态']
            order_amount = float(str(data.iloc[0]['配送费总价(单位元)']).replace(',', '').strip())
            order_penalty = float(str(data.iloc[0]['订单取消费(单位元)']).replace(',', '').strip())
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
    file_path = os.path.join(os.path.dirname(__file__), '..\..', 'data', '顺丰2024-07-06.xlsx')

    order = XunFengOrder(file_path)

    order_number = '2801137201222294861_9ge1hpxrax1' #501140294136124283_93pjtmg0d0c  701134232008469978_tgxmdkqihau
 
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
