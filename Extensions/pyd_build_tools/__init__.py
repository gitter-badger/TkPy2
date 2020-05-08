# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: __init__.py
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/3-9:00
# 创建时的IDE名称: PyCharm

import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
from .build import build_file
from .file_types import all_filetypes


def main():
    file_name = tkFileDialog.askopenfilenames(title='选择文件', filetypes=all_filetypes)
    if not file_name:
        return
    if not tkMessageBox.askyesno('问题', '是否生成PYD文件?'):
        return
    build_file(file_name)
