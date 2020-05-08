# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: default_config
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/24-14:55
# 创建时的IDE名称: PyCharm
import copy
import platform
from tkpy2_tools.tkpy_file import tkpy_file

init_title = "TkPy2 (Python {})".format(platform.python_version())  # 初始化题目
DefaultRunCodeCommand = "import os; \
number = os.system(\'{python_name} \\\"{file_name}\\\"'); \
input('\\n\\n终端进程已退出,退出代码: \\033[36m'+str(number)+'\\033[0m。按回车键以退出。')"  # 运行的时候执行的命令
AssertPep8Command = \
    'pycodestyle {} --format="\'%(path)s\', %(row)d, %(col)d, \'%(code)s\', \'%(text)s\'"'  # 检查PEP8时的命令
showxcrollbar = True  # 显示X轴滚动条
auto_save = True  # 是否启用自动保存
conda_activate = True  # conda激活环境
text_widget_weigth = 100
text_widget_height = 30
open_x_y = [200, 150]
open_and_save_file_auto_chdir = True  # 自动换目录
Htmlshowlinenumbers = True  # 转换成Html是是否显示行号
conda_activate_code = "conda activate {}"  # 激活命令
conda_python_name = 'base'  # conda默认环境名
open_autocomplete = True  # 开启自动补全
serverconfig = {"host": "127.0.0.1", "port": 8080}  # 服务器端口
new_file_text = "# -*- coding: utf-8 -*-\n"  # 新建文件时的文字
text_long_size = 79
DefaultEncoding = 'utf-8'  # 默认编码
DefaultPythonCommand = 'python'  # 默认Python命令
ShowAskDialogToRun = False  # 显示保存dialog
TkPy_icon_name = 'TkPy.ico'  # 徽标名称
TabSize = 4  # 缩进大小(空格单位)
TkPy_path = []  # TkPy的环境变量
default_html_css_name = 'default'
FormattingToolsName = 'autopep8'  # 格式化工具(还有一个选项:yapf)
ShowPep8Warning = False  # 显示PEP8警告
DefaultRunArgvCodeCommand = "import os; \
number = os.system(\'{python_name} \\\"{file_name}\\\" {argv}'); \
input('\\n\\n终端进程已退出,退出代码: \\033[36m'+str(number)+'\\033[0m。按回车键以退出。')"
showlinenumbers = True
font_name = '新宋体'  # 字体名称
font_size = 10  # 字体大小
format_code_on_save = True
events = {
    'autocomplete': ['Control-space', '自动补全'],
    'save': ['Control-s', '保存'],
    'saveas': ['Control-Shift-S', '另存为'],
    'new_file': ['Control-n', '新建文件'],
    'return_html': ['Control-Shift-H', '转换Html文档'],
    'new_window': ['Control-Shift-N', '打开一个新窗口'],
    'reload_window': ['Control-r', '重启'],
    'open_file': ['Control-o', '打开文件'],
    'exit_all_window': ['Control-d', '退出程序'],
    'exit_window': ['Control-w', '关闭窗口'],
    'replace_text': ['Control-h', '替换'],
    'find_text': ['Control-f', '查找'],
    'run_auto_pep8': ['Control-Alt-L', '使用AutoPEP8格式化文档'],
    'format_pep8_with_yapf': ['Control-Alt-F', '使用Yapf格式化文档'],
    'untab': ['Shift-Tab', '取消缩进'],
    'go_to_line': ['Control-l'],
    'run_code': ['F5', '运行'],
    'run_code_add_argv': ['Alt-F5', '运行时添加Argv'],
    'run_code_with_file': ['Control-F5', '从文件运行'],
    'help': ['F1', '获取TkPy的帮助'],
    'help_python_doc': ['Control-F1', '获取Python包的帮助'],
    'undo': ['Control-z', '撤回'],
    'redo': ['Control-y', '撤销']
}
config_locals = copy.copy(locals())  # 所有设置选项
try:
    del config_locals["__name__"]
    del config_locals["__doc__"]
    del config_locals["__package__"]
    del config_locals["__loader__"]
    del config_locals["__spec__"]
    del config_locals['__builtins__']
    del config_locals['__file__']
    del config_locals['__cached__']
    del config_locals['platform']
    del config_locals['copy']
    del config_locals['tkpy_file']
except (KeyError, NameError):
    pass
tkpy_file(config_locals)
