# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: __init__.py
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/30-16:35
# 创建时的IDE名称: PyCharm

from . import image_tools
from . import pyd_build_tools

Extensions = [
    {'name': '文字识别', 'command': image_tools.main},
    {'name': '生成Pyd文件', "command": pyd_build_tools.main}
]
