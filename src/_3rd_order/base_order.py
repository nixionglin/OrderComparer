# _3rd_order/base_order.py
import os
import warnings

class Base3rdOrder:
    
    def __init__(self, file_path):
        if not file_path or not os.path.isfile(file_path):
            print(f"'{file_path}'文件不存在，请检查！")

        warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl.styles.stylesheet')

    def get_total_penalty_amount():
        """
        获取第三方订单所有违约金之和
        """
        return 0

    def get_total_order_amount(self):
        """
        获取第三方订单扣款金额
        """
        return 0

    def get_order_number_info(self, order_number):
        """
        获取配送单订单号在第三方订单中的订单信息
        : order_number 配送单订单号
        :return: 订单相关数据 {配送平台订单编号、订单状态、订单实付金额、订单违约多}
        """
        return None

