# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: linter
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/2-9:00
# 创建时的IDE名称: PyCharm
from flake8.api import legacy as flake8


def Flake8Linter(file_names, not_show: list = []):
    style_guide = flake8.get_style_guide(ignore=not_show)
    report = style_guide.check_files([file_names])
    return report
