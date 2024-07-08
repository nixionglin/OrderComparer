import datetime
import os
import openpyxl
import pandas as pd
import unittest
import unittestreport
import warnings

# 全局固定变量
LOCAL_ORDER_COLUMN = 'delivery_order_sn'
THIRD_PARTY_ORDER_COLUMN = '三方订单编号'
CAPACITY_PLATFORM = '闪送'






class DataComparison(unittest.TestCase):
    def __init__(self, methodName='runTest', third_party_file=None, local_file=None, local_flow_file=None):
        super(DataComparison, self).__init__(methodName)
        self.third_party_file = third_party_file
        self.local_file = local_file
        self.local_flow_file = local_flow_file






    def check_distribution_orders(self):
        print(f"--------------------------- 配送单各平台扣款汇总 ---------------------------") 
        # 检查本地配送单
        if not self.local_file or not os.path.isfile(self.local_file):
            raise ValueError("配送单不存在！")

        # 读取本地数据表
        local_df = pd.read_excel(self.local_file, engine='openpyxl')
        if local_df.empty:
            raise ValueError("配送单文件表解析失败")

        unique_delivery_platforms = local_df['发单运力'].dropna().unique()

        for platform in unique_delivery_platforms:
            platform_data = local_df[(local_df['发单运力'] == platform) & (local_df['配送状态'] == '配送完成') & (local_df['delivery_channel'] == 0)]
            platform_total_free = round(platform_data['free'].sum(), 2)
            print(f"配送平台: '{platform:6}'\t扣款金额总和: '{platform_total_free:.2f}'")


    def compare_data(self): 
        print(f"----------------------- 配送单与{CAPACITY_PLATFORM}平台对账 -----------------------") 
 
        local_df = pd.read_excel(self.local_file, engine='openpyxl')
        if local_df.empty:
            raise ValueError("配送单文件表解析失败")

        # 检查第三方订单是否存在
        if not self.third_party_file or not os.path.isfile(self.third_party_file):
            raise ValueError("{CAPACITY_PLATFORM}订单不存在！")

        # 确保本地订单中有必要的列
        if LOCAL_ORDER_COLUMN not in local_df.columns or '发单运力' not in local_df.columns or '配送状态' not in local_df.columns or 'delivery_channel' not in local_df.columns:
            raise ValueError("配送单文件中缺少必要的关键列")

        # 获取本地订单发单运力单数
        platform_count = len((local_df['发单运力'] == CAPACITY_PLATFORM))
        if platform_count == 0:
            raise ValueError(f"配送单文件中没有对应'{CAPACITY_PLATFORM}'运力") 

        # 读取三方数据表
        third_party_df = pd.read_excel(self.third_party_file, engine='openpyxl', sheet_name='订单明细', dtype={'实付金额(元)': str})
        if third_party_df.empty:
            raise ValueError("第三方Excel表解析失败")

        # 检查第三方订单表是否存在必要列，如三方订单编号、订单状态
        if THIRD_PARTY_ORDER_COLUMN not in third_party_df.columns or '订单状态' not in third_party_df.columns or '实付金额(元)' not in third_party_df.columns:
            raise ValueError(f"第三方Excel表中缺少'{THIRD_PARTY_ORDER_COLUMN}'列") 

        third_party_row_count = len(third_party_df)
        print(f"第三方{CAPACITY_PLATFORM}订单共有 {third_party_row_count} 条数据（含配送完成与取消）") 

        flash_delivery_data = local_df[(local_df['发单运力'] == CAPACITY_PLATFORM) & (local_df['配送状态'] == '配送完成') & (local_df['delivery_channel'] == 0)]
        local_row_count = len(flash_delivery_data)
        print(f"配送订单对应{CAPACITY_PLATFORM}发单运力符合条件(配送状态为已完成, delivery_channel 为 0)的数据有 {local_row_count} 条") 

        total_third_amount = 0.00
        total_local_amount = 0.00
        exception_orders = []

        for index, row in flash_delivery_data.iterrows():
            order_number = row['delivery_order_sn']
            order_amount = row['free']
            # print(f"本地配送单订单号: {order_number}, 金额: {order_amount}")

            # 累计本地配送有效订单扣款金额之和
            total_local_amount += order_amount

            # 查找 '三方订单编号' 列值为 order_number 的数据（闪送订单后面多了一个','）
            third_party_order = third_party_df[third_party_df['三方订单编号'] == order_number + ',']
   
            if not third_party_order.empty:
                third_party_order_number = third_party_order.iloc[0]['三方订单编号']
                third_party_self_number = third_party_order.iloc[0]['订单编号']
                third_orider_status = third_party_order.iloc[0]['订单状态']

                third_order_amount = 0.00
                if third_orider_status == '闪送完成':
                    third_order_amount += float(str(third_party_order.iloc[0]['实付金额(元)']).replace(',', '').strip())
                elif third_orider_status == '已取消':
                        third_order_amount += float(str(third_party_order.iloc[0]['取消单扣款金额(元)']).replace(',', '').strip())

                # 累计本地订单对应第三方订单扣款金额之和
                total_third_amount += third_order_amount

                # paid_amount_str = third_party_order.iloc[0]['实付金额(元)']
                # third_order_amount = float(str(third_party_order.iloc[0]['实付金额(元)']).replace(',', '').strip())

                amount = round(third_order_amount, 2) - round(order_amount, 2)
                if third_order_amount == order_amount:
                    print(f"Pass: 配送单: '{order_number:<31}' 金额: '{order_amount:.2f}';\t{CAPACITY_PLATFORM}订单: '{third_party_self_number:<10}' 状态: '{third_orider_status}'  金额: '{third_order_amount:.2f}';")
                else:
                    order_message = f"Fail: 配送单: '{order_number:<31}' 金额: '{order_amount:.2f}';\t{CAPACITY_PLATFORM}订单: '{third_party_self_number:<10}' 状态: '{third_orider_status}'  金额: '{third_order_amount:.2f}';\t差值: '{amount:.2f}'"
                    print(order_message)
                    exception_orders.append(order_message)

                    # 获取两张表对应订单相关原始数据
                    local_order_data = local_df[local_df['delivery_order_sn'] == order_number]
                    exception_orders.append(f"\t*** 配送单相关原始数据 \n{local_order_data.to_string()}")

                    third_party_order = third_party_df[third_party_df['三方订单编号'] == order_number + ',']
                    exception_orders.append(f"\t*** {CAPACITY_PLATFORM}订单相关原始数据 \n{third_party_order.to_string()}\n")
            else:
                exception_orders.append(f"{CAPACITY_PLATFORM}订单中未找到配送订单中对应的订单编号: '{order_number}', 金额：'{order_amount}'")

        print()

        # 对两个累计和统一2位小数精度
        total_third_amount = round(total_third_amount, 2)
        total_local_amount = round(total_local_amount, 2)
        difference = round(total_third_amount - total_local_amount, 2)

        if difference == 0:
            print(f"对账正常: 配送单 {self.local_file} 与{CAPACITY_PLATFORM}第三方订单 {self.third_party_file} 扣款金额相等({total_third_amount})")
        else:
            exception_type = "多" if difference > 0 else "少"
            print(f"对账异常: 第三方平台{exception_type}扣款 {abs(difference)}元 【 配送单扣款金额:{total_local_amount} {CAPACITY_PLATFORM}平台扣款金额：{total_third_amount}】")
            for order in exception_orders:
                print(order)
        print(f"---------------------------------------------------------------------------\n") 


    def local_compare(self):
        print(f"-----------------------------  本地流水对账 ---------------------------------") 
        if not self.local_flow_file or not os.path.isfile(self.local_flow_file):
            raise ValueError("本地流水订单不存在！")

        # 读取本地数据表
        local_df = pd.read_excel(self.local_file, engine='openpyxl')
        if local_df.empty:
            raise ValueError(f"配送订单表{local_file}解析失败")

        local_flow_df = pd.read_excel(self.local_flow_file, engine='openpyxl')
        if local_flow_df.empty:
            raise ValueError(f"流水表{local_flow_file}解析失败")

        # 获取流水订单中商户号并去重
        unique_admin_ids = local_flow_df['admin_id'].unique()

        for admin_id in unique_admin_ids:
            print(f"\n---------- 商户'{admin_id}'对账 ----------")
            admin_data = local_flow_df[local_flow_df['admin_id'] == admin_id]

            #新客奖励
            new_customer_reward = admin_data[(admin_data['type'] == 2) & (admin_data['method'] == 3)]['money'].sum()
            user_recharge = admin_data[(admin_data['type'] == 2) & (admin_data['method'].isin([1, 2]))]['money'].sum()
            merchant_settlement = round(abs(admin_data[admin_data['type'] == 1]['money'].sum()), 2)

            combined_result = f"流水单: 新客奖励 {new_customer_reward}, 充值 {user_recharge}, 扣款金额 {merchant_settlement}"
            print(combined_result)

            # 获取去重后的订单号
            unique_orders = admin_data[admin_data['type'] == 1]['delivery_order_id'].drop_duplicates().dropna()

            if unique_orders.empty:
                continue

            order_total_free = 0
            valid_orders = [combined_result]

            print(f"配送订单中解析对应订单扣款金额...")
            # 遍历订单
            for order_id in unique_orders:
                delivery_data = local_df[(local_df['delivery_order_sn'] == order_id) & (local_df['配送状态'] == '配送完成')]
                dispatch_platform = delivery_data['发单运力'].str.strip().values[0] if not delivery_data['发单运力'].empty else '未知'
    
                if not delivery_data.empty:
                    free_value = delivery_data['free'].values[0]
                    print(f"发单运力：{dispatch_platform:<8}  订单号: '{order_id:<31}' 扣款金额：'{free_value:.2f}'")
                    order_total_free += free_value
                    order_amounts = local_df.loc[(local_df['delivery_order_sn'] == order_id) & (local_df['配送状态'] == '配送完成'), 'free'].tolist()
                    order_amount_str = ' '.join([f"{order_id}|{amount}" for amount in order_amounts])
                    valid_orders.append(order_amount_str)
                else:
                    print(f"发单运力：{dispatch_platform:<8}  订单号: '{order_id:<31}' 未完成状态, 忽略")
            
            order_total_free = round(order_total_free, 2)
            valid_orders.append(f"该商户配送单中累计扣款: {order_total_free}")

            # 输出商户对账结果
            econciliation_result = '对账成功' if merchant_settlement == order_total_free else '对账失败'
            print(f"\n商户({admin_id}) '{econciliation_result}' 详细对账记录: '{valid_orders}'")
    print(f"---------------------------------------------------------------------------") 

    def runTest(self):
        try:
            self.check_distribution_orders()
        except Exception as e:
            print(f"An error occurred during file check: {e}")

        try:
            self.compare_data()
        except Exception as e:
            print(f"An error occurred during data comparison: {e}")

        try:
            self.local_compare()
        except Exception as e:
            print(f"An error occurred during local comparison: {e}")


# 测试代码
if __name__ == "__main__":
    # 忽略关于默认样式的警告
    warnings.filterwarnings("ignore", "You are trying to set a value on a read-only property")
    warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl.styles.stylesheet')

    third_party_file = os.path.join(os.path.dirname(__file__), '..', 'data', '闪送6.24-6.30.xlsx')
    local_file = os.path.join(os.path.dirname(__file__), '..', 'data', '配送单6.24-6.30.xlsx')
    local_flow_file = os.path.join(os.path.dirname(__file__), '..', 'data', '本地流水6.24--6.30.xlsx')


    suite = unittest.TestSuite()
    data_comparison_test = DataComparison(methodName='runTest', third_party_file=third_party_file, local_file=local_file, local_flow_file=local_flow_file)
    data_comparison_test._testMethodDoc = "闪送订单"
    suite.addTest(data_comparison_test)  # 运力平台

    runner = unittestreport.TestRunner(suite, title='订单对账报告', desc='订单对账', tester='测试者')
    runner.run()
