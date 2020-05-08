# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: bind
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/30-16:34
# 创建时的IDE名称: PyCharm

import re
import tkinter as tk
from tkinter import ttk
from .tkpy_file import read_tkpy_file

event_locals = read_tkpy_file('config').read('events')


def get_event(*chrs) -> str:
    if chrs[0] in event_locals:
        return "<" + str(event_locals[chrs[0]][0]) + '>' \
            if event_locals[chrs[0]][0] else ''
    if len(chrs) == 1:
        return '<' + chrs[0] + '>'
    return '<' + '-'.join(chrs) + '>'


def get_event_key(event_name):
    event_key = get_event(event_name).replace('<', '>').replace('>', '')
    event_key = event_key.replace('Control', 'Ctrl')
    for i in re.findall(r'[a-z]+', event_key):
        if len(i) == 1 and event_key.count(i) == 1:
            event_key = event_key.replace(i, i.upper())
        elif i == event_key[-1]:
            event_key = event_key[0:-1] + i.upper()
    return event_key


def get_key_name(*args):
    tkinter_key: str = '-'.join(args) if len(args) > 1 else '-'.join(args[0].split('-'))
    tkinter_key = tkinter_key.replace('Control', 'Ctrl')
    tkinter_key = tkinter_key.replace('tab', 'Tab')
    tkinter_key = tkinter_key.replace('shift', 'Shift')
    tkinter_key.replace('KeyRelease', 'Key')
    tkinter_key.replace('alt', 'Alt')
    tkinter_key.replace('Key', '')
    for i in re.findall(r'[a-z]+', tkinter_key):
        if len(i) == 1:
            tkinter_key = tkinter_key.replace(i, i.upper())
    return tkinter_key


def _test(base_root):
    """TkPy bind tools"""
    root = tk.Toplevel(base_root)
    root.geometry('300x100')
    root.resizable(0, 0)
    root.title('Get tkinter key name')
    LabelFrame = tk.LabelFrame(root, text='请输入绑定名称: ')
    Entry = ttk.Entry(LabelFrame)
    View = tk.Label(root)
    LabelFrame.pack(fill=tk.X, expand=True)
    Entry.pack(fill=tk.X, expand=True)
    Entry.bind(get_event('KeyRelease'), lambda event: View.config(text=get_key_name(*Entry.get().split('-'))))
    View.pack(fill=tk.X, expand=True)
