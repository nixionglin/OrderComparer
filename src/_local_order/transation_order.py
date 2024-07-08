import openpyxl
import os
import pandas as pd
import warnings

# 流水表类
class TransationOrder:

    def __init__(self, file_path):
        try:
            if not file_path or not os.path.isfile(file_path):
                print("交易文件不存在，请检查！")
            
            warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl.styles.stylesheet')
            self.data = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            print(f"读取交易文件时发生错误: {e}")

    def get_unique_admin_ids(self):
        if self.data.empty:
            return None
        
        return self.data['admin_id'].unique()

    # 获取指定商户数据
    def get_admin_data(self, admin_id):
        if self.data.empty or admin_id is None:
            return None

        return self.data[self.data['admin_id'] == admin_id]


    # 获取指定商户指定订单扣款金额
    def get_total_order_amount(self, admin_id, order_number):
        admin_data = self.get_admin_data(admin_id)
        if admin_data.empty:
            return None
        return round(abs(admin_data[(admin_data['delivery_order_id'] == order_number) & (admin_data['type'] == 1)]['money'].sum() if 'money' in admin_data else 0), 2)


    # 获取指定商户所有订单号
    def get_all_order(self, admin_id):
        admin_data = self.get_admin_data(admin_id)
        if admin_data.empty:
            return None

        return admin_data[admin_data['type'] == 1]['delivery_order_id'].drop_duplicates().dropna()


        # 获取指定商户获取结算期帐账户信息
    def get_admin_info(self, admin_id):
        admin_data = self.get_admin_data(admin_id)
        if admin_data.empty:
            return None

        if not admin_data['money'].isnull().all():
            admin_data = admin_data.sort_values(by='createtime') # 对”createtime“列进行升序排序
            initial_amount = round(admin_data.iloc[0]['before'], 2) # 起始金额=第一行”before“列的值
            balance = round(admin_data.iloc[-1]['after'], 2) #余额=第后一行after值
            total_deduction_amount = round(abs(admin_data[admin_data['type'] == 1]['money'].sum() if 'money' in admin_data else 0), 2)
            unique_order_count = len(admin_data[admin_data['type'] == 1]['delivery_order_id'].drop_duplicates().dropna()) if 'money' in admin_data else 0
            reward_amount = admin_data[(admin_data['type'] == 2) & (admin_data['method'] == 3)]['money'].sum() if 'money' in admin_data else 0
            recharge_amount = admin_data[(admin_data['type'] == 2) & (admin_data['method'].isin([1, 2]))]['money'].sum() if 'money' in admin_data else 0
            recharge_count = len(admin_data[((admin_data['type'] == 2) & ((admin_data['method'] == 1) | (admin_data['method'] == 2)))]) if 'money' in admin_data else 0
            difference = round(abs((initial_amount + reward_amount + recharge_amount - total_deduction_amount) - balance), 2) #订单扣款与水费金额差值，为0时表示正常，反之就是多扣或少扣

            # 发生订单扣款且差值不为0零时视有异常
            if total_deduction_amount > 0 and not difference == 0:
                print(f"商户'{admin_id}' 存在扣款异常！")

            return {
                '订单扣款总额': total_deduction_amount, 
                '订单(去重)数': unique_order_count,
                '新客奖励': reward_amount, 
                '充值金额': recharge_amount,
                '充值笔数': recharge_count,
                '初始金额': initial_amount,
                '账户余额': balance, 
                '差值': difference
            }
        else:
            return None



# 测试代码
if __name__ == "__main__":
    admin_id = 4994
    order_number = '72o92rse2gjha4x7s_gc0uyo42wa4'

    file_path = os.path.join(os.path.dirname(__file__), '../..', 'data', '本地流水6.24--6.30.xlsx')

    try:
        # 创建一个 TransactionOrder 实例
        transaction_order = TransationOrder(file_path=file_path)

        # merchant_data = transaction_order.get_admin_data(admin_id)
        # print("Merchant Data:")
        # print(merchant_data)

        # 调用 get_admin_info 方法(逻辑不太清楚，目前还有问题)
        admin_info = transaction_order.get_admin_info(10786)
        print(f"商户账号信息: {admin_info}")
    
        # total_order_amount = transaction_order.get_total_order_amount(admin_id, order_number)
        # print(f"订单扣款总金额:{total_order_amount}")

        # all_orders = transaction_order.get_all_order(5044)
        # print(f"指定用户所有订单:{all_orders}")
    except Exception as e:
        print(f"An error occurred: {e}")
