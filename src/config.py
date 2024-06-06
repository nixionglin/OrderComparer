import configparser

def get_default_params():
    # 读取默认参数
    return config.get('params', 'default_params', fallback='').split(',')

def get_custom_params():
    # 读取自定义参数
    return config.get('params', 'custom_params', fallback='').split(',')

def get_login_credentials():
    # 获取登录凭据
    username = config.get('login', 'username')
    password = config.get('login', 'password')
    return username, password

# 读取配置文件
config = configparser.ConfigParser()
config.read('config/config.ini', encoding='utf-8')

