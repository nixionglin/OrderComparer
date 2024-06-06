import configparser
import concurrent.futures
import os
import csv
import json
import requests
import time
import tkinter as tk

from configparser import ConfigParser
from config import get_login_credentials
from datetime import datetime
from datetime import timedelta
from tkinter import filedialog

token_expiration = 2 * 3600 * 1000  # Token valid for 2 hours
result_file_name = 'config/shared_prefs_data.json' #store the result data


def load_config():
    """
    加载配置文件
    :return: 配置对象
    """
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

token = None
config = load_config()


def request_token():
    """
    请求登录接口，获取token
    :return: token
    """
    headers = {"Content-Type": "application/json"}
    url = "https://chain-api-test.kuaixiaoxiang.com/login"

    username, password = get_login_credentials()

    data = {
        "username": username,
        "password": password
    }

    print("请求接口 token ......")
    res = requests.post(url=url, headers=headers, json=data)
    token = res.json()["data"]["token"]
    # 将token存储到文件中
    with open(result_file_name, 'w') as file:
        data = {
            'token': token,
            'expiration_time': int(time.time() * 1000)
        }
        json.dump(data, file)

def read_token():
    """
    从JSON文件中读取token
    :param file_path: 文件路径
    :return: token
    """
    with open(result_file_name, 'r') as file:
        data = json.load(file)
        token = data.get('token')
    return token


def read_csv_file(file_path):
    """
    读取CSV文件
    :param file_path: 文件路径
    :return: 文件数据
    """
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data


def get_csv_columns(file_path):
    """
    获取CSV文件列名
    :param file_path: 文件路径
    :return: 列名列表
    """
    with open(file_path, mode='r', encoding='gbk') as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
    return columns

# 根据 待处理 csv 文件中对应日期获取对应数据请求参数
def request_data(token, begin_time, end_time):
    """
    请求数据
    :param token: 访问令牌
    :param begin_time: 开始时间
    :param end_time: 结束时间
    :return: 请求结果
    """
    url = "https://chain-api-test.kuaixiaoxiang.com/op/business/analysis"
    headers = {
        "Content-Type": "application/json",
        "token": token
    }

    now = datetime.now()
    beginTime = now - timedelta(days=7)
    endTime = now - timedelta(days=1)
    compareBeginTime = now - timedelta(days=14)
    compareEndTime = now - timedelta(days=8)
    print(f"beginTime: {beginTime}")
    print(f"endTime: {endTime}")
    print(f"compareBeginTime: {compareBeginTime}")
    print(f"compareEndTime: {compareEndTime}")

    params = {
        "beginTime": begin_time,
        "endTime": end_time,
        "compareBeginTime": compareBeginTime,
        "compareEndTime": compareEndTime
    }


    print(f"根据文件内容请求内部接口数据")

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def compare_data(csv_data, api_data):
    """
    比较数据
    :param csv_data: CSV数据
    :param api_data: API数据
    :return: 比较结果
    """
    print(f"--------------compare_data")


    # 实现比较逻辑
    return "Comparison Result"


def save_processed_csv_file(file_path, process_time, process_status):
    """
    保存处理后的CSV文件
    :param file_path: 文件路径
    :param process_time: 处理时间
    :param process_status: 处理状态
    """
    with open('processed_files.txt', 'a') as processed_files:
        processed_files.write(f"{file_path},{process_time},{process_status}\n")


def read_processed_files():
    """
    从配置本地存储的json处理文件中读取已处理过的文件
    如果json不存在返回空，如果json存在读取json里所有存储的的已处理过的文件并返回
    """
    processed_files = []

    if os.path.exists('config/processed_files.json'):
        with open('config/processed_files.json', 'r') as json_file:
            processed_files = json.load(json_file)
    else:
        return processed_files

def get_unprocessed_csv_files():
    """
    获取未处理的CSV文件
    :return: 未处理的文件列表
    """
    processed_files = read_processed_files()
    csv_files = [file for file in os.listdir('data') if file.endswith('.csv')]
    unprocessed_files = []

    for csv_file in csv_files:
        if any(csv_file in processed_file['file_path'] for processed_file in processed_files):
            continue
        unprocessed_files.append(csv_file)

    return unprocessed_files

def process_file(csv_files):
    print(f"开始处理文件: {csv_files}")
    file_path = os.path.join('data', csv_files)

    csv_data = get_csv_columns(file_path)

    token = read_token()
    api_data = request_data('token123', '2022-01-01', '2022-01-31')
    print("API数据内容:", api_data)

    comparison_result = compare_data(csv_data, api_data)
    return comparison_result


def handle_result(result):
    file, comparison_result = result
    if comparison_result == "Comparison Result":
        save_processed_csv_file(file, str(datetime.now()), "Processed")

# 初始化脚本主逻辑
def async_process_csv_files():
    print("获取待处理的 csv 文件列表...")

    unprocessed_files = get_unprocessed_csv_files()
    if not unprocessed_files:
        print("无可处理的 csv 文件")
        return True

    # 异步处理 csv 文件
    with concurrent.futures.ThreadPoolExecutor() as executor:
        csv_files = [file for file in os.listdir('data') if file.endswith('.csv')]
        print(f"当前待处理文件: {csv_files}")

        futures = {executor.submit(process_file, file): file for file in csv_files}

        for future in concurrent.futures.as_completed(futures):
            file = futures[future]
            print(f"处理完成的 csv 文件: {file}")

            try:
                result = future.result()
            except Exception as exc:
                print(f"处理 {file} 时异常: {exc}")
            else:
                handle_result(result)

    return True


# 初始化UI
def initialize_ui():
    """
    初始化用户界面
    """
    root = tk.Tk()
    root.title('OrderComparer')
    root.geometry('500x300')

    left_frame = tk.Frame(root)
    right_frame = tk.Frame(root)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)

    param_label = tk.Label(left_frame, text='参数')
    param_label.pack(side=tk.TOP, padx=5, pady=5)
    separator = tk.Frame(left_frame, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill='x', padx=5, pady=5)

    for key, value in config['parameters'].items():

        print(f'{key}: {value}')

        # param_name_label = tk.Label(left_frame, text=param_name)
        # param_name_label.pack(side=tk.TOP, padx=5, pady=5)
        # param_value_label = tk.Label(left_frame, text=param_value)
        # param_value_label.pack(side=tk.TOP, padx=5, pady=5)

    check_button = tk.Button(right_frame, text='订单检查', command=check_orders)
    check_button.pack(side=tk.TOP, anchor='ne', padx=5, pady=5)
    result_text = tk.Text(right_frame)
    result_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    status_bar = tk.Label(root, text='状态栏', bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()


def check_orders(status_bar=None):
    """
    检查订单
    :param status_bar: 状态栏
    """
    status_bar.config(text='检查订单')
    source_data = request_data()
    if source_data:
        status_bar.config(text='调用源出处接口成功')
        target_data = fetch_data_from_target()
        if target_data:
            status_bar.config(text='调用目标出处接口成功')
            preprocessed_source_data = preprocess_data(source_data)
            preprocessed_target_data = preprocess_data(target_data)
            status_bar.config(text='开始数据核对')
            comparison_result = compare_data(preprocessed_source_data, preprocessed_target_data)
            output_result(comparison_result)
            save_result_to_file(comparison_result)
        else:
            status_bar.config(text='调用目标出处接口失败')

def initialize_token():
    token = None
    expand = None
    
    try:
        if os.path.exists(result_file_name):
            with open(result_file_name, 'r') as file:
                data = json.load(file)
            token = data.get('token')
            current_time = int(time.time() * 1000)
            expiration_time = data.get('expiration_time')

            print(f"Token: {token}")
            print(f"Expiration Time: {expiration_time}")
            print(f"Current Time: {current_time}")
            if token and expiration_time and current_time - expiration_time < token_expiration:
                return
    except Exception as e:
        print(f"保存 token 数据的文件不存在: {e}")
    
    request_token()

def fetch_data_from_source():
    # 从源出处获取数据的占位符
    return {}


def fetch_data_from_target():
    # 从目标出处获取数据的占位符
    return {}


def preprocess_data(data):
    # 数据预处理逻辑的占位符
    return data


def compare_data(source_data, target_data):
    # 数据比较逻辑的占位符
    return "Comparison Result"


def output_result(result, result_text=None):
    result_text.insert(tk.END, result)


def save_result_to_file(result):
    os.makedirs('data', exist_ok=True)
    with open('data/result.txt', 'w') as file:
        file.write(result)


if __name__ == "__main__":
    # initialize_ui()
    print("---------- main start -----------")

    initialize_token()

    async_process_csv_files()

    # print("get_csv_columns Columns:")
    # csv_columns = get_csv_columns('data/20240101-20240428-1714284673513.csv')
    # for column in csv_columns:
    #     print(column)
    
    print("---------- main end -----------")

