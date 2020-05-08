# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: user-config
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/24-14:54
# 创建时的IDE名称: PyCharm

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from default_config import *
from ui_config import *
# Write your config hear.
default_html_css_name = 'vs'
if __name__ == "__main__":
    for Key, Value in config_locals.items():  # 所有默认的设置选项(运行以查看)
        print({Key: Value})
