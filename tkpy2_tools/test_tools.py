# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: test_tools
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/30-19:53
# 创建时的IDE名称: PyCharm

import tkinter as tk
from tkinter import ttk


def get_event(*chrs) -> str:
    if len(chrs) == 1:
        return '<' + chrs[0] + '>'
    return '<' + '-'.join(chrs) + '>'


def test(function, test_type='tkinter'):
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Test for TkPy')
    tk.Label(root, bitmap='info' if function.__doc__ else '', compound=tk.LEFT)\
            .pack()
    tk.Label(root, text='TkPy test', font=('微软黑体', 30)).pack()
    tk.Label(root,
             text="Help for this test:\n\n" + function.__doc__ if function.__doc__ is not None else 'No help',
             font=('黑体', 15), justify=tk.LEFT).pack(fill=tk.BOTH, side=tk.TOP)
    if test_type == 'tkinter':
        ttk.Button(root, text='Test (Ctrl-R)',
                   command=lambda: function(root)).pack(fill=tk.X, side=tk.BOTTOM)
        root.bind(get_event('Control', 'r'), lambda event: function(root))
    elif test_type == 'terminal':
        ttk.Button(root, text='Test (Ctrl-R)',
                   command=lambda: function()).pack(fill=tk.X, side=tk.BOTTOM)
        root.bind(get_event('Control', 'r'), lambda event: function())
    root.mainloop()


if __name__ == "__main__":
    test(test, test_type='terminal')
