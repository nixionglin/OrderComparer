import datetime
import pandas as pd
import unittest
import os
import openpyxl
import unittestreport

# 全局固定变量
LOCAL_ORDER_COLUMN = 'delivery_order_sn'
THIRD_PARTY_ORDER_COLUMN = '三方订单编号'

class DataComparison(unittest.TestCase):
    def __init__(self, methodName='runTest', third_party_file=None, local_file=None, capacity_platform=None):
        super(DataComparison, self).__init__(methodName)
        self.third_party_file = third_party_file
        self.local_file = local_file
        self.capacity_platform = capacity_platform

    def compare_data(self): 
        # 对传入的两张表进行是否存在case
        if not self.third_party_file or not self.local_file or not os.path.isfile(self.third_party_file) or not os.path.isfile(self.local_file):
            raise ValueError("传入的excel表为空或对应文件不存在，请检查传入数据！")

       # 检查指定的运力平台
        if self.capacity_platform is None:  # Corrected null to None
            raise ValueError(f"未指定运力平台'{self.capacity_platform}'")  # Added f-string for better formatting

        print(f"----------------------- {self.capacity_platform} 平台对账-----------------------") 

        # 读取本地数据表
        local_df = pd.read_excel(self.local_file, engine='openpyxl')
        if local_df.empty:
            raise ValueError("本地Excel表解析失败")

        # 确保本地订单中有必要的列
        if LOCAL_ORDER_COLUMN not in local_df.columns or '发单运力' not in local_df.columns or '配送状态' not in local_df.columns or 'delivery_channel' not in local_df.columns:
            raise ValueError("本地Excel表中缺少必要的关键列")

        # 获取本地订单发单运力单数
        platform_count = len((local_df['发单运力'] == self.capacity_platform))
        if platform_count == 0:
            raise ValueError(f"本地Excel表中没有对应'{self.capacity_platform}'运力") 

        # 读取三方数据表
        third_party_df = pd.read_excel(self.third_party_file, engine='openpyxl', sheet_name='订单明细', dtype={'实付金额(元)': str})
        if third_party_df.empty:
            raise ValueError("第三方Excel表解析失败")

        # 检查第三方订单表是否存在必要列，如三方订单编号、订单状态
        if THIRD_PARTY_ORDER_COLUMN not in third_party_df.columns or '订单状态' not in third_party_df.columns or '实付金额(元)' not in third_party_df.columns:
            raise ValueError(f"第三方Excel表中缺少'{THIRD_PARTY_ORDER_COLUMN}'列") 

        third_party_row_count = len(third_party_df)
        print(f"第三方{self.capacity_platform}订单有效数据有{third_party_row_count}条") 

        flash_delivery_data = local_df[(local_df['发单运力'] == '闪送') & (local_df['配送状态'] == '配送完成') & (local_df['delivery_channel'] == 1)]
        local_row_count = len(flash_delivery_data)
        print(f"配送订单对应{self.capacity_platform}运力有效数据有{third_party_row_count}条") 

        # self.assertEqual(third_party_row_count, local_row_count, f"{self.capacity_platform}({third_party_row_count})与本地配送表订单({order_number}) 数不一致")
        
        for index, row in flash_delivery_data.iterrows():
            order_number = row['delivery_order_sn']
            order_amount = row['free']
            # print(f"本地配送单订单号: {order_number}, 金额: {order_amount}")

            # 查找 '三方订单编号' 列值为 order_number 的数据（闪送订单后面多了一个','）
            third_party_order = third_party_df[third_party_df['三方订单编号'] == order_number + ',']
   
            if not third_party_order.empty:
                third_party_order_number = third_party_order.iloc[0]['三方订单编号']
                third_party_self_number = third_party_order.iloc[0]['订单编号']
                paid_amount_str = third_party_order.iloc[0]['实付金额(元)']
                third_party_order_amount = float(str(paid_amount_str).replace(',', '').strip())
                # print(f"三方订单编号: '{third_party_order_number}'，实付金额(元): '{third_party_order_amount}'")

                if third_party_order_amount == order_amount:
                    print(f"Pass: 本地订单与{self.capacity_platform}订单金额一致：'{order_number}' <-> '{third_party_self_number}' 金额：'{order_amount}'")
                else:
                    print(f"Fail: 本地订单与{self.capacity_platform}不一致: '{order_number}', 金额: '{order_amount}' <->'{third_party_self_number}'，金额: '{third_party_order_amount}'")

                self.assertEqual(third_party_order_amount, order_amount, f"本地配送表订单号 {order_number} 数据不一致")
            else:
                print(f"{self.capacity_platform}订单中未找到配送订单中对应的订单编号: '{order_number}', 金额：'{order_amount}'")

    def local_compare(self):
        print("---------> local_compare")


    def runTest(self):
        self.compare_data()
        self.local_compare()


# 测试代码
if __name__ == "__main__":
    third_party_file = os.path.join(os.path.dirname(__file__), '..', 'data', '闪送6.24-6.30.xlsx')
    local_file = os.path.join(os.path.dirname(__file__), '..', 'data', '配送单6.24-6.30.xlsx')
    # local_flow_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'local_flow0701.xlsx')
    capacity_platform = "闪送"

    suite = unittest.TestSuite()
    data_comparison_test = DataComparison(methodName='runTest', third_party_file=third_party_file, local_file=local_file, capacity_platform=capacity_platform)
    data_comparison_test._testMethodDoc = "闪送订单"
    suite.addTest(data_comparison_test)  # 运力平台

    runner = unittestreport.TestRunner(suite, title='订单对账报告', desc='订单对账', tester='测试者')
    runner.run()

    # 动态生成报告名称
    # report_date = datetime.datetime.now().strftime("%Y%m%d")
    # report_name = f"report_{report_date}.html"
    # report_path = os.path.join(os.path.dirname(__file__), '..', 'reports', report_name)
    # runner.report(report_path)
    # print(f"测试报告已生成: {report_path}")
