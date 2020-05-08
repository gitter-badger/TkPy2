# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: __init__.py
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/4-9:52
# 创建时的IDE名称: PyCharm

import tkinter.tix as tk
import tkinter.font as tkFont
from tkinter import ttk

from tkpy2_tools import TkPyWindowConfig
from tkpy2_tools.tkpy_file import tkpy_file, read_tkpy_file
from default_config import config_locals

set_config = tkpy_file(config_locals)
config = read_tkpy_file('config').read()

class ConfigWindow(tk.Toplevel, TkPyWindowConfig):
    def __init__(self, master=None, *args, **kwargs):
        super(ConfigWindow, self).__init__(master, *args, **kwargs)
        self.transient(master)

    def get_start(self):
        pass

    def mainloop(self, n=0):
        self.resizable(False, False)
        super(ConfigWindow, self).mainloop(n)


def Show(master=None):
    root = ConfigWindow(master)
    root.get_start()
    return root


if __name__ == "__main__":
    root = Show()
    root.mainloop()
