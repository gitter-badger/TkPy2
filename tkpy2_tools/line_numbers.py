# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: line_numbers
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/30-11:21
# 创建时的IDE名称: PyCharm

import tkinter.tix as tk

from .tkpy_file import read_tkpy_file

config = read_tkpy_file('config')


class TkPyTextWidget(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) ||
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

        self.comment = False


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self):
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            self.config(
                width=config.read('font_size') * max(
                    [len(str(i)) for i in range(len(self.textwidget.get(0.0, tk.END).split('\n')))]))
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            if linenum != str(self.textwidget.index(tk.INSERT)).split('.')[0]:
                self.create_text(5, y, anchor=tk.NW, text=linenum, fill='gray',
                                 font=(config.read('font_name'), config.read('font_size')))
            else:
                self.create_text(5, y, anchor=tk.NW, text=linenum,
                                 font=(config.read('font_name'), config.read('font_size')))
            i = self.textwidget.index("%s+1line" % i)
