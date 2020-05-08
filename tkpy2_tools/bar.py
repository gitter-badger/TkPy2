# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: bar
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/2-16:24
# 创建时的IDE名称: PyCharm

import tkinter.tix as tk
from tkinter import ttk


class ToolsBar(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(ToolsBar, self).__init__(*args, **kwargs)
        self.tip = None

    def add_command(self, *, label=None, balloonmsg=None, statusmsg=None, **kwargs):
        widget = tk.Button(self, text=label, **kwargs)
        widget.pack(side=tk.LEFT, fill=tk.Y)
        if self.tip:
            self.tip.bind_widget(widget, balloonmsg=balloonmsg, statusmsg=statusmsg)

    def add_separator(self):
        ttk.Separator(self, orient=tk.VERTICAL).pack(fill=tk.Y, padx=5, side=tk.LEFT)

    def add_menu(self, **kwargs):
        Menu = tk.tkinter.Menubutton(self, **kwargs)
        Menu.pack(side=tk.LEFT, fill=tk.Y)
        return Menu

    def bind_tip(self, tip: tk.Balloon):
        self.tip = tip
