# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: __init__.py
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/30-18:49
# 创建时的IDE名称: PyCharm
from aip import AipOcr
import tkinter.tix as tk
from tkinter import ttk
from tkpy2_tools import test_tools
from tkpy2_tools.text import text_view

import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from .id import APP_ID, API_KEY, SECRET_KEY


def get_text(path):
    try:
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        f = open(path, 'rb')
        image = f.read()
        message = client.basicGeneral(image)
        return_list = []
        for i in message.get('words_result'):
            return_list.append(i.get('words'))
    except:
        tkMessageBox.showerror('出错了', '百度ID的识别次数用完了,请明天再试。')
    else:
        return '\n'.join(return_list)


class Tools(object):
    def __init__(self, base_root=None):
        self.root = tk.Toplevel(base_root)
        self.root.transient(base_root)
        self.root.minsize(400, 50)
        self.root.resizable(0, 0)
        self.all_file_types = [('图片文件', ('.png', '.jpg', '.jpeg'))]
        self.root.title('文字识别')
        self.Frame = tk.Frame(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL)
        self.LabelFrame = ttk.LabelFrame(self.root, text='文件目录: ')
        self.Entry = ttk.Entry(self.LabelFrame, xscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.Entry.xview)
        self.Entry.config(state=tk.DISABLED)
        self.Button = ttk.Button(self.Frame, text='选择文件', command=self.askfile)
        self.submmitButton = ttk.Button(self.Frame, text='识别', command=lambda: self.ok(self.Entry.get()))

    def get_start(self):
        self.LabelFrame.pack(fill=tk.BOTH, expand=True)
        self.Entry.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
        self.scrollbar.pack(fill=tk.X)
        self.Button.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.submmitButton.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        self.Frame.pack(fill=tk.X, expand=True, side=tk.BOTTOM)

    def askfile(self):
        file_name = tkFileDialog.askopenfilename(title='选择文件', filetypes=self.all_file_types)
        if not file_name:
            return
        self.Entry.config(state=tk.NORMAL)
        self.Entry.delete(0, tk.END)
        self.Entry.insert(tk.END, file_name)
        self.Entry.config(state=tk.DISABLED)
        if not tkMessageBox.askokcancel('问题', '是否生成文字?'):
            return
        self.ok(file_name)

    def ok(self, file_name):
        if not file_name:
            return
        text = get_text(file_name)
        text_view(text, base_root=self.root)

    def mainloop(self, n=0):
        self.root.mainloop(n)


def _test(base_root):
    """TkPy文字识别"""
    root = Tools(base_root)
    root.get_start()
    if __name__ == '__main__':
        root.mainloop()


def main():
    root = Tools()
    root.get_start()


if __name__ == "__main__":
    test_tools.test(_test)
