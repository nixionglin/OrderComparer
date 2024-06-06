import tkinter as tk

def initialize_ui():
    root.title('OrderComparer')
    root.geometry('500x300')

    left_frame.pack(side=tk.LEFT, fill=tk.Y)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)

    param_label = tk.Label(left_frame, text='参数')
    param_label.pack(side=tk.TOP, padx=5, pady=5)
    separator = tk.Frame(left_frame, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill='x', padx=5, pady=5)

    for key in config['parameters']:
        param_name = key
        param_value = get_param(key)
        param_name_label = tk.Label(left_frame, text=param_name)
        param_name_label.pack(side=tk.TOP, padx=5, pady=5)
        param_value_label = tk.Label(left_frame, text=param_value)
        param_value_label.pack(side=tk.TOP, padx=5, pady=5)

    check_button = tk.Button(right_frame, text='订单检查', command=check_orders)
    check_button.pack(side=tk.TOP, anchor='ne', padx=5, pady=5)
    result_text = tk.Text(right_frame)
    result_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    status_bar = tk.Label(root, text='状态栏', bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)