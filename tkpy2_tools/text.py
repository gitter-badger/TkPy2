# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: text
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/30-19:15
# 创建时的IDE名称: PyCharm
import builtins
import io
import keyword
import tkinter.tix as tk
import tokenize
from idlelib.colorizer import color_config, ColorDelegator
from idlelib.percolator import Percolator

from pygments import lex
from pygments.lexers.python import PythonLexer
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Whitespace
from pygments.styles import get_style_by_name
from tkinter import ttk
import pyperclip
from pygments.token import Token
from tkpy2_tools.tkpy_file import read_tkpy_file
from diff_match_patch import diff_match_patch

highlight_name = read_tkpy_file('config').read('default_html_css_name')


def text_view(view_text: str,
              title='TkPy text view',
              geometry=None,
              min_size=None,
              max_size=None,
              base_root=None):
    def Copy():
        copy_text = text.get(tk.SEL_FIRST, tk.SEL_LAST) or text.get(0.0, tk.END)
        pyperclip.copy(copy_text)

    root = tk.Toplevel(base_root)
    root.transient(base_root)
    root.title(title)
    root.resizable(0, 0)
    if geometry is not None:
        root.geometry(geometry)
    if min_size:
        root.minsize(*min_size)
    if max_size:
        root.maxsize(max_size)
    text = tk.Text(root)
    ycrollbar = tk.Scrollbar(root)
    Frame = tk.Frame(root)
    CopyButton = ttk.Button(Frame, text='复制', command=Copy)
    CloseButton = ttk.Button(Frame, text='关闭', command=root.destroy)
    text.insert(tk.END, view_text)
    CopyButton.pack(fill=tk.X, expand=True, side=tk.RIGHT)
    CloseButton.pack(fill=tk.X, expand=True, side=tk.LEFT)
    ycrollbar.config(command=text.yview)
    Frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    ycrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(fill=tk.BOTH, expand=True)
    text.config(yscrollcommand=ycrollbar.set, state=tk.DISABLED)
    root.mainloop()


def insert_char(text: tk.Text, char: str, raw: str = '', go=True):
    index = str(text.index(tk.INSERT)).split('.')
    if text.get(f'{index[0]}.{int(index[1])}') == char:
        if char == raw:
            text.mark_set(tk.INSERT, f'{index[0]}.{int(index[1]) + 1}')
            text.see(tk.INSERT)
            return 'break'
    if raw:
        text.insert(tk.INSERT, raw)
        if (char != raw) or (char == '"') or char == "'":
            text.insert(tk.INSERT, char)
    if go:
        text.mark_set(tk.INSERT, f'{index[0]}.{int(index[1]) + 1}')
        text.see(tk.INSERT)
    return 'break'


def assert_text(old_text, new_text):
    dmp = diff_match_patch()
    patches = dmp.patch_make(old_text, new_text)
    diff = dmp.patch_toText(patches)

    patches = dmp.patch_fromText(diff)
    new_text, _ = dmp.patch_apply(patches, old_text)
    return bool(_)


def code_color(text: tk.Text):
    color_config(text)
    p = Percolator(text)
    d = ColorDelegator()
    p.insertfilter(d)
