import pandas as pd

def parse_csv_to_dataframe(file_path):
    """
    解析CSV文件内容为DataFrame
    :param file_path: CSV文件路径
    :return: DataFrame
    """
    try:
        df = pd.read_csv(file_path, encoding='GBK')
        return df
    except Exception as e:
        print(f"Error parsing CSV file: {e}")
        return None

def generate_summary_data(dataframe):
    """
    通过日期汇总获取本地请求对应日期与比较对应日期等相关参数
    :param dataframe: 数据内容
    :return: 开始时间, 结束时间, 店铺ID, 比较开始时间, 比较结束时间
    """
    # 根据日期进行汇总
    start_date = pd.to_datetime(dataframe['日期'].str.split('-', expand=True)[0]).min().strftime('%Y%m%d') + ' 00:00:00'
    end_date = pd.to_datetime(dataframe['日期'].str.split('-', expand=True)[1]).max().strftime('%Y%m%d') + ' 23:59:59'

    # 根据下单时间返回比较开始时间与结束时间
    dataframe['下单日期'] = pd.to_datetime(dataframe['下单时间']).dt.date
    compare_start_time = dataframe['下单日期'].min().strftime('%Y-%m-%d') + ' 00:00:00'
    compare_end_time = dataframe['下单日期'].max().strftime('%Y-%m-%d') + ' 23:59:59'

    # 根据店铺ID汇总
    poiIds = dataframe['店铺ID'].unique()
    poiId = poiIds[0] if len(poiIds) == 1 else None

    return start_date, end_date, compare_start_time, compare_end_time, poiId

def get_order_amount_list(dataframe):
    """
    通过下单时间获取订单金额清单
    :param dataframe: 数据内容
    :return: day, validOrderAmount, validOrderAmount, validOrderPrice
    """
    dataframe['下单日期'] = pd.to_datetime(dataframe['下单时间']).dt.strftime('%m.%d')
    
    validOrderAmount = dataframe.groupby('下单日期')['订单总金额'].sum() - dataframe.groupby('下单日期')['订单折扣后金额'].sum()
    validOrderAmount = validOrderAmount.reset_index(name='validOrderAmount')
    
    validOrderPrice = dataframe.groupby('下单日期')['订单总金额'].sum() / dataframe.groupby('下单日期').size()
    validOrderPrice = validOrderPrice.reset_index(name='validOrderPrice')

    result_list = []
    for index, row in dataframe.iterrows():
        result = {
            "day": row['下单日期'],
            "validOrderAmount": row['订单总金额'],
            "lossAmount": row['订单总金额'] - row['订单折扣后金额'],
            "validOrderPrice": row['订单总金额'] / dataframe[dataframe['下单日期'] == row['下单日期']].shape[0]
        }
        result_list.append(result)
    return result_list

def calculate_order_count(dataframe):
    """
    汇总csv文件里的订单编号条数定义推单数
    :param dataframe: 数据内容
    :return: 推单数
    """
    order_count = len(dataframe['订单编号'].unique())
    return order_count


def get_valid_order_count(dataframe):
    """
    获取有效订单总数，汇总“订单状态”为“订单完成”的总数，与接口中 orderNum 比对
    :param dataframe: 数据内容
    :return: 有效订单总数
    """
    valid_order_count = len(dataframe[(dataframe['订单状态'] == '订单完成') | (dataframe['订单状态'] == '订单已处理')])
    return valid_order_count

def get_valied_order_rate(dataframe):
    """
    获取有效订单率，有效订单率 = 有效订单总数 / 总订单数。
    :param dataframe: 数据内容
    :return: 有效订单率
    """
    valid_order_count = get_valid_order_count(dataframe)
    total_orders = len(dataframe)
    valid_order_rate = valid_order_count / total_orders if total_orders > 0 else 0
    return valid_order_rate

def summarize_order_amount(dataframe):
    """
    获取所有订单总金额
    :param dataframe: 数据内容
    :return: 所有订单总金额
    """
    total_order_amount = dataframe['订单总金额'].sum()
    return total_order_amount

def summarize_completed_orders_amount(dataframe):
    """
    获取所有有效订单交易额（订单状态为'订单完成'和'订单已处理' 的订单总金额 ）
    :param dataframe: 数据内容
    :return: 所有有 '订单总金额' for completed or processed orders
    """
    completed_orders = dataframe[(dataframe['订单状态'] == '订单完成') | (dataframe['订单状态'] == '订单已处理')]
    total_completed_orders_amount = completed_orders['订单总金额'].sum()
    return total_completed_orders_amount

def summarize_completed_orders_amount(dataframe):
    """
    获取有效订单单均价
    :param dataframe: 数据内容
    :return: 有效订单单均价
    """
    return summarize_completed_orders_amount(dataframe) / get_valid_order_count(dataframe)

def get_date_count(dataframe):
    """
    计算日期范围列中的天数
    :param dataframe: 数据内容
    :return: 日期天数
    """
    if '日期' in dataframe.columns:
        date_series = pd.to_datetime(dataframe['日期'])
        days_count = (date_series.max() - date_series.min()).days + 1
    else:
        days_count = 1  # Fallback if '日期' column is missing or empty
    return days_count

def get_daily_average_push_orders(dataframe):
    """
    获取日均推单数，日均推单数 = 所有推单数 / 日期天数
    :param dataframe: 数据内容
    :return: 日均推单数
    """
    total_orders = calculate_order_count(dataframe)
    days_count = get_days_count(dataframe)
    daily_average_push_orders = total_orders / days_count if days_count > 0 else 0
    return daily_average_push_orders

def get_valid_push_orders_order_count(dataframe):
    """
    获取日推有效单数，日均推单数 = 所有有效订单数 / 日期天数
    :param dataframe: 数据内容
    :return: 日推有效单数
    """
    return get_valid_order_count(dataframe) / get_date_count(dataframe)

def get_daily_average_valid_orders_amount(dataframe):
    """
    获取日均有效订单交易额，其值 = 有效订单交易额除以统计时间范围内的天数
    :param dataframe: 数据内容
    :return: 日均有效订单交易额
    """
    total_valid_orders_amount = summarize_completed_orders_amount(dataframe)
    days_count = get_date_count(dataframe)
    daily_average_valid_orders_amount = total_valid_orders_amount / days_count if days_count > 0 else 0
    return daily_average_valid_orders_amount

def get_cancelled_order_count(dataframe):
    """
    获取订单状态为“订单取消”的订单总数
    :param dataframe: 数据内容
    :return: 订单取消总数
    """
    cancelled_order_count = len(dataframe[dataframe['订单状态'] == '订单取消'])
    return cancelled_order_count



# 测试代码
def test_summarize_data(csv_file_path):
    # Read test data from CSV file
    test_df = parse_csv_to_dataframe(csv_file_path)

    # Execute the function to be tested
    start_date, end_date, compare_start_time, compare_end_time, poiId = generate_summary_data(test_df)

    # Print the results for tracking
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Compare Start Time: {compare_start_time}")
    print(f"Compare End Time: {compare_end_time}")
    print(f"poi ID: {poiId}")

    order_list = get_order_amount_list(test_df)

    # Print the results for tracking
    # for order in order_list:
    #     print("{")
    #     print(f"    day: {order['day']}")
    #     print(f"    validOrderAmount: {order['validOrderAmount']}")
    #     print(f"    lossAmount: {order['lossAmount']}")
    #     print(f"    validOrderPrice: {order['validOrderPrice']}")
    #     print("}")

    order_count = calculate_order_count(test_df)
    valid_order_count = get_valid_order_count(test_df)
    cancelled_order_count = get_cancelled_order_count(test_df)

    print(f"日均推单数: {order_count}")
    print(f"日推有效单数: {valid_order_count}")
    print(f"取消订单数: {cancelled_order_count}")

if __name__ == "__main__":
    csv_file_path = 'data/20240101-20240428-1714284673513.csv'
    test_summarize_data(csv_file_path)
