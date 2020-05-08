# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: build
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/3-9:01
# 创建时的IDE名称: PyCharm
from tkpy2_tools.tkpy_file import read_tkpy_file
import os
import tkinter.messagebox as tkMessageBox
from subprocess import run
encoding = read_tkpy_file('config').read('DefaultEncoding')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_file(file_paths: list):
    file_text = f"""# -*- coding: utf-8 -*-
from distutils.core import setup
import os
from Cython.Build import cythonize
for path in {file_paths}:
    setup(ext_modules=cythonize(path.split('/')[-1]))
"""
    file_path = file_paths[0].replace('\\', '/')
    os.chdir('/'.join(file_path.split('/')[0:-1]))
    with open('setup_pyd.py', 'w', encoding=encoding) as f:
        f.write(file_text)
    returncode = run(['python', 'setup_pyd.py', 'build_ext', '--inplace'])
    if returncode.returncode:
        tkMessageBox.showerror('出错了', '在生成的时候出现了错误。')
