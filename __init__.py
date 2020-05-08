# -*- coding: utf-8 -*-
"""
TkPy2 一个升级版的TkPy IDE
---------------------------
帮助:
    在命令行中使用:
        python -m TkPy : 打开一个新的TkPy窗口
        python -m TkPy -h : 显示TkPy命令行帮助
    特殊功能帮助:
        文件菜单:
            自动保存:
                自动保存文件: 默认为打开状态
            重启:
                重启TkPy
            退出:
                关闭所有窗口
                ⚠:这个功能不会保存文件,请保存文件后在退出。
        编辑菜单:
            样式菜单:
                运行AutoPEP8:
                    快捷键:
                        Ctrl-Alt-L
        工具菜单:
            程序包:
                安装包:
                    安装某一个包
注意:
    有些内容已移到TkPy2的Web页面了。 (单击帮助按钮以打开。)
"""
import copy
import os
import platform
import sys
# Start pygments
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from pygments import highlight
# End pygments
from idlelib.editor import TK_TABWIDTH_DEFAULT
import psutil
import chardet
import webbrowser
from multiprocessing import Process
from importlib import import_module
# Start tkinter
from tkinter import ttk
import tkinter.simpledialog
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.tix as tk
# End tkinter
import jedi

TkPy_Path = os.path.dirname(os.path.abspath(__file__))  # TkPy的安装目录
sys.path.append(TkPy_Path)  # 添加进环境变量
sys.path.append(os.path.dirname(TkPy_Path))  # 添加进环境变量


# Start tkpy extensions
try:
    from default_config import config_locals, serverconfig, AssertPep8Command
except ModuleNotFoundError:
    if __name__ == "__main__":
        tk.Tk().withdraw()
        tkMessageBox.showerror('错误', '没有配置文件,现在退出。')
        sys.exit(-1)
from Extensions import Extensions
from TkPyDoc import runserver
from formatting_tools import autopep8
from formatting_tools.yapf.yapflib.yapf_api import FormatCode
from tkpy2_tools.linter import Flake8Linter
from tkpy2_tools.line_numbers import TkPyTextWidget
from tkpy2_tools.text import insert_char, assert_text, code_color
from tkpy2_tools.bar import ToolsBar
from tkpy2_tools import (
    replace,
    find,
    get_css,
    line_numbers,
    showtraceback,
    get_all_packages, compile_pyc, config as tkpyConfig, TkPyWindowConfig
)
from tkpy2_tools.tkpy_file import tkpy_file
from tkpy2_tools.bind import get_key_name, get_event, get_event_key
# end tkpy extensions


PythonVersion = platform.python_version_tuple()  # Python版本
os_name = os.name  # 系统名称
__version__ = '5.0.0'
is_anaconda = os.path.exists(os.path.join(
    sys.prefix, 'conda-meta'))  # 是不是Anaconda
cpu_numbers = psutil.cpu_count()  # CPU逻辑数量
Tab_Text = chr(9)

TkPyVersions = f'TkPy version: {__version__} Tkinter version: {tk.TkVersion} System name: ' \
               f'{platform.system()} System version: {platform.version()}'


class doc_server(object):
    def __init__(self):
        super().__init__()
        self.p = Process(target=self.runserver)

    def start_doc_server(self):
        try:
            self.p.start()
        except AssertionError:
            return False

    def runserver(self, host=serverconfig['host'], port=serverconfig['port']):
        try:
            runserver(host=host, port=port)
        except Exception:
            tk.Tk().withdraw()
            tkMessageBox.showerror(
                "错误", '服务器端口被占中,端口:{}'.format(port))
            sys.exit()

    def stop_doc_server(self):
        self.p.terminate()


def get_environment():
    """Get the environment in which TkPy is running

    Returns
    -------
    str
        Environment name
    """
    try:
        from IPython import get_ipython
    except ImportError:
        return 'terminal'

    try:
        shell = get_ipython().__class__.__name__

        if shell == 'ZMQInteractiveShell':  # Jupyter notebook or qtconsole
            return 'jupyter'
        elif shell == 'TerminalInteractiveShell':  # Terminal running IPython
            return 'ipython'
        elif shell == 'PyDevTerminalInteractiveShell':  # Terminal running pydev
            return 'pydev'
        else:
            return 'terminal'  # Other type (?)

    except NameError:
        return 'terminal'


def assert_pep8(file_name):
    if "pycodestyle" in get_all_packages():
        return os.popen(AssertPep8Command.format(file_name)).read().replace('\n', ' | ').split(' | ')
    else:
        return 'not install'


history = []


def get_CPU_percent():
    return psutil.virtual_memory().percent


def get_encoding(text):
    return chardet.detect(text)


server = doc_server()

data_root = tk.Tk()
data_root.withdraw()
WinNum = 0
sys.path.append(os.path.join(TkPy_Path, 'formatting_tools'))


class MainWindow(TkPyWindowConfig):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口类"""
        global WinNum
        WinNum += 1
        super().__init__()
        self.set_config = tkpy_file(config_locals)
        self.set_history = tkpy_file(history, file_name='history')
        self.config = self.set_config.read('config')
        self.Extensions = Extensions
        self.history = self.set_history.read('history')
        self.out_html_file_types = [("Html文件", '.html')]  # Html保存类型
        self.all_file_types = [
            ('所有支持的文件', ('.py', '.pyw', '.pyx')),
            ("Python源文件", '.py'),
            ('Python无窗口源文件', '.pyw'),
            ('Cython源文件', '.pyx')
        ]
        self.encoding = self.config['DefaultEncoding']  # 默认编码
        self.code_save = True  # 一样
        self.yesnosavefile = False  # 未保存文件
        self.file_name = ''
        self.root = tk.Toplevel(data_root)  # 主窗口
        self.yesnoopenautosave = tk.BooleanVar()
        self.DefaultPythonCommandVar = tk.StringVar()
        self.DefaultPythonCommandVar.set(self.get_python_name(self.config['DefaultPythonCommand']))
        self.yesnoopenautosave.set(self.config['auto_save'])
        self.root.protocol("WM_DELETE_WINDOW", self.ExitWarning)
        self.root.title(self.config['init_title'])  # 设置题目
        self.Menu = tk.Menu(self.root, tearoff=False)  # 主菜单
        self.FileMenu = tk.Menu(self.Menu, tearoff=False)  # 文件菜单
        self.HistoryMenu = tk.Menu(self.FileMenu, tearoff=False)  # 历史菜单
        self.EditMenu = tk.Menu(self.Menu, tearoff=False)  # 编辑菜单
        self.GotoMenu = tk.Menu(self.Menu, tearoff=False)  # 转到菜单
        self.RunMenu = tk.Menu(self.Menu, tearoff=False)  # 运行菜单
        self.codingMenu = tk.Menu(self.EditMenu, tearoff=False)  # 代码菜单
        self.TerminalMenu = tk.Menu(self.Menu, tearoff=False)  # 终端菜单
        self.HelpMenu = tk.Menu(self.Menu, tearoff=False)  # 帮助菜单
        self.CodeMenu = tk.Menu(self.EditMenu, tearoff=False)  # 代码菜单
        self.pep8Menu = tk.Menu(self.CodeMenu, tearoff=False)  # PEP8菜单
        self.ErrorMenu = tk.Menu(self.CodeMenu, tearoff=False)  # 错误菜单
        self.ExtensionMenu = tk.Menu(self.Menu, tearoff=False)  # 拓展菜单
        self.POPMenu = tk.Menu(self.root, tearoff=False)  # 右键菜单
        self.RunPythonMenu = tk.Menu(
            self.RunMenu, tearoff=False)  # 选择Python菜单
        self.root.config(menu=self.Menu)  # 显示菜单
        self.root.geometry('+{}+{}'.format(*self.config['open_x_y']))
        self.PanedWindow = ttk.PanedWindow(self.root)
        self.EditFrame = ttk.Frame(self.root)
        self.text = TkPyTextWidget(self.EditFrame, undo=True, bd=0,
                                   font=(self.config['font_name'],
                                         self.config['font_size']),
                                   width=self.config['text_widget_weigth'],
                                   height=self.config['text_widget_height'])
        self.CommandHelpLabel = tk.Label(self.root, justify=tk.LEFT)
        self.system_info_Label = tk.Label(self.root, justify=tk.RIGHT)
        self.tools_bar = ToolsBar(self.root)
        self.tip = tk.Balloon(self.root, initwait=0, statusbar=self.CommandHelpLabel)
        self.tools_bar.bind_tip(self.tip)
        self.linenumbers = line_numbers.TextLineNumbers(self.EditFrame, width=20)
        self.xcrollbar = tk.Scrollbar(self.EditFrame, orient=tk.HORIZONTAL)  # X轴滚动条
        self.ycrollbar = tk.Scrollbar(self.EditFrame)  # X轴滚动条

    def ExitWarning(self, editWin=None, info=None, exit_main=True):
        global WinNum
        try:
            if os.path.isdir(os.environ['TMP']):
                os.removedirs(os.path.join(os.environ['TMP'], 'tkpy2'))
        except (FileNotFoundError, FileExistsError, KeyError, OSError):
            pass
        if editWin is None:
            editWin = self.root
        if info == 'reload':
            if not self.code_save:
                if not tkMessageBox.askyesno("问题-文件未保存", '还有文件未保存,是否重启'):
                    return
            editWin.destroy()
            self.new_window()
            WinNum -= 1
            return
        elif info == 'exit_all':
            if not tkMessageBox.askyesno("问题-实验性功能", '本功能不会保存文件，确认使用?'):
                return
            editWin.destroy()
            server.stop_doc_server()
            sys.exit()
        if not self.code_save:
            res = tkMessageBox.askyesnocancel('问题-文件未保存', '还有文件未保存,是否保存?')
            if res is None:
                return
            elif res is True:
                if not self.save(command='exit'):
                    return

        editWin.destroy()
        WinNum -= 1
        if not WinNum:
            if exit_main:
                sys.exit(server.stop_doc_server())

    def get_python_name(self, name):
        if name == 'python':
            return 'CPython'
        elif name == 'ipython':
            return 'IPython'
        elif name == 'ptpython':
            return 'PtPython'
        elif name == 'bpython':
            return 'BPython'

    def goto_package(self):
        text = tkinter.simpledialog.askstring('问题', '请输入一个Python包名,\nTkPy会在sys.path中进行查找。')
        if text:
            try:
                data = import_module(text)
            except ModuleNotFoundError:
                tkMessageBox.showinfo('提示', '未找到此包,可以把path添加到sys.path,然后再查找。')
            else:
                try:
                    file = data.__file__
                except AssertionError:
                    tkMessageBox.showinfo('提示', '这个模块不是由Python编写,无法查看源码。')
                    return
                else:
                    root = self.new_window()
                    root.open(file)

    def get_start(self):
        """准备开始"""
        self.PanedWindow.add(self.tools_bar)
        self.PanedWindow.add(self.EditFrame)
        self.PanedWindow.pack(fill=tk.BOTH, expand=True)
        self.CommandHelpLabel.pack(side=tk.LEFT)
        self.system_info_Label.pack(side=tk.RIGHT)
        if self.config['showlinenumbers']:
            self.linenumbers.pack(fill=tk.Y, side=tk.LEFT)
            self.linenumbers.config(bg=self.text.cget('background'))
            self.linenumbers.attach(self.text)
        if self.config['showxcrollbar']:
            self.text.config(xscrollcommand=self.xcrollbar.set,
                             wrap='none')  # 设置文字组件
            self.xcrollbar.config(command=self.text.xview)  # 设置X轴运动条
            self.xcrollbar.pack(side=tk.BOTTOM, fill=tk.X)  # 显示X轴滚动条
        self.text.config(yscrollcommand=self.ycrollbar.set)
        self.ycrollbar.config(command=self.text.yview)
        self.ycrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        try:
            self.root.iconbitmap(os.path.join(TkPy_Path, self.config["TkPy_icon_name"]))
        except:
            pass
        self.system_info_Label.config(text=TkPyVersions)
        self.text.bind("<<Change>>", lambda event: self.linenumbers.redraw())
        self.text.bind("<Configure>", lambda event: self.linenumbers.redraw())
        self.text.bind('"', lambda event: insert_char(self.text, '"', '"'))
        self.text.bind("'", lambda event: insert_char(self.text, "'", "'"))
        self.text.bind("(", lambda event: insert_char(self.text, ")", '('))
        self.text.bind("[", lambda event: insert_char(self.text, "]", '['))
        self.text.bind("{", lambda event: insert_char(self.text, "}", '{'))

        self.text.bind(")", lambda event: insert_char(self.text, ")", ')'))
        self.text.bind("]", lambda event: insert_char(self.text, "]", ']'))
        self.text.bind("}", lambda event: insert_char(self.text, "}", '}'))
        self.text.bind(get_event('BackSpace'), lambda event: self.BackSpace())
        self.text.undo_block_start = lambda: None
        self.text.undo_block_stop = lambda: None
        self.text.bind(get_event('autocomplete'), self.autoJEDIInput)
        self.set_tk_tabwidth(self.config["TabSize"])
        self.text.pack(fill=tk.BOTH, expand=True)  # 显示文字组件
        self.text.bind(get_event('Button-3'), self.open_pop_Menu)
        self.text.insert(tk.END, self.config["new_file_text"])  # 插入文字
        self.text.bind(get_event('KeyRelease'), lambda event: self.assert_text())
        code_color(self.text)  # 启用代码高亮
        # -------------------------------------------------------------------
        self.Menu.add_cascade(label="文件", menu=self.FileMenu)  # 添加文件菜单
        self.Menu.add_cascade(label="编辑", menu=self.EditMenu)  # 添加编辑菜单
        self.Menu.add_cascade(label="转到", menu=self.GotoMenu)  # 添加转到菜单
        self.Menu.add_cascade(label="运行", menu=self.RunMenu)  # 添加运行菜单
        self.Menu.add_cascade(label="终端", menu=self.TerminalMenu)  # 添加终端菜单
        self.Menu.add_cascade(label='帮助', menu=self.HelpMenu)  # 添加帮助菜单
        if self.Extensions:
            self.Menu.add_cascade(label='拓展', menu=self.ExtensionMenu)
            for key in self.Extensions:
                if 'bind_key' in key:
                    self.ExtensionMenu.add_command(label=key['name'] + ' (' + get_key_name(key['bind_key']) + ')',
                                                   command=key['command'])
                    self.root.bind(get_event(key['bind_key']), lambda event: key['command']())
                else:
                    self.ExtensionMenu.add_command(label=key['name'], command=(key['command']))
        # -------------------------------------------------------------------
        self.FileMenu.add_command(
            label=f"打开 ({get_event_key('open_file')})", command=self.open)  # 添加打开选项
        # self.FileMenu.add_cascade(label='文件历史记录', menu=self.HistoryMenu)
        self.FileMenu.add_command(
            label=f"新建 ({get_event_key('new_file')})", command=self.new_file)  # 添加新建选项
        self.FileMenu.add_command(label='新建快速文件', command=self.new_scratch_file)
        self.FileMenu.add_separator()  # 添加分割线
        self.FileMenu.add_command(
            label=f"保存 ({get_event_key('save')})", command=lambda: self.save(format_pep8=True))  # 添加保存选项
        self.FileMenu.add_command(
            label=f"另存为 ({get_event_key('saveas')})",
            command=lambda: self.save("saveas", format_pep8=True))  # 添加另存为选项
        self.FileMenu.add_command(
            label=f"输出为Html ({get_event_key('return_html')})", command=self.out_for_html)  # 添加输出为Html选项
        self.FileMenu.add_checkbutton(
            label="自动保存", command=lambda:
            self.save("autosave"), variable=self.yesnoopenautosave)  # 添加自动保存选项
        self.FileMenu.add_separator()  # 添加分割线
        self.FileMenu.add_command(
            label=f"重启这个窗口 ({get_event_key('reload_window')})", command=lambda:
            self.ExitWarning(info="reload"))  # 添加重启选项
        self.FileMenu.add_command(
            label=f"关闭这个窗口 ({get_event_key('exit_window')})", command=self.ExitWarning)  # 添加关闭选项
        self.FileMenu.add_command(
            label=f"退出所有窗口 ({get_event_key('exit_all_window')})", command=lambda:
            self.ExitWarning(info='exit_all'))  # 添加退出所有窗口选项
        self.FileMenu.add_command(
            label=f'打开一个新窗口 ({get_event_key("new_window")})', command=self.new_window)
        self.root.bind(get_event('new_window'),
                       lambda event: self.new_window())
        self.root.bind(get_event('save'), lambda event: self.save(format_pep8=True))
        self.root.bind(get_event('saveas'),
                       lambda event: self.save('saveas', format_pep8=True))
        self.text.bind(get_event('new_file'), lambda event: self.new_file())
        self.text.bind(get_event('open_file'), lambda event: self.open())
        self.root.bind(get_event('reload_window'),
                       lambda event: self.ExitWarning(info='reload'))
        self.text.bind(get_event('return_html'),
                       lambda event: self.out_for_html())
        self.root.bind(get_event('exit_window'),
                       lambda event: self.ExitWarning())
        self.root.bind(get_event('exit_all_window'),
                       lambda event: self.ExitWarning(info='exit_all'))
        # -------------------------------------------------------------------
        self.HistoryMenu.add_command(label='删除所有历史记录', command=self.RemoveAllHistory)
        self.HistoryMenu.add_separator()
        for i in self.history:
            if os.path.isfile(i):
                self.HistoryMenu.add_command(label=i, command=lambda: self.open(i))
        self.EditMenu.add_command(
            label='复制 (Ctrl-C)', command=self.Copy)
        self.EditMenu.add_command(
            label='粘贴 (Ctrl-V)', command=self.Paste)
        self.EditMenu.add_command(
            label='剪切 (Ctrl-X)', command=self.Cut)
        self.EditMenu.add_separator()  # 添加分割线
        self.EditMenu.add_command(label=f'撤销 ({get_event_key("undo")})', command=self.Undo)
        self.EditMenu.add_command(label=f"撤回 ({get_event_key('redo')})", command=self.Redo)
        self.EditMenu.add_separator()
        self.EditMenu.add_command(label=f'查找 ({get_event_key("find_text")})', command=self.find_text)
        self.EditMenu.add_command(
            label=f'替换 ({get_event_key("replace_text")})', command=self.replace_text)
        self.EditMenu.add_separator()  # 添加分割线
        self.EditMenu.add_cascade(label="代码", menu=self.CodeMenu)  # 添加代码菜单
        self.text.bind(get_event('replace_text'), lambda event: self.replace_text(True))
        self.text.bind(get_event('undo'), lambda event: self.Undo())
        self.text.bind(get_event('redo'), lambda event: self.Redo())
        self.text.bind(get_event('find_text'), lambda event: self.find_text())
        # -------------------------------------------------------------------
        self.CodeMenu.add_cascade(label='PEP8功能', menu=self.pep8Menu)
        self.CodeMenu.add_cascade(label='错误检测', menu=self.ErrorMenu)
        self.CodeMenu.add_command(label=f'移除缩进 ({get_event_key("untab")})', command=self.unTab)
        self.CodeMenu.add_command(label='转到包的源码', command=self.goto_package)
        self.root.bind(get_event('untab'), lambda event: self.unTab())
        # -------------------------------------------------------------------
        self.ErrorMenu.add_command(label='Flake8检测', command=self.RunFlake8Linter)
        # -------------------------------------------------------------------
        self.pep8Menu.add_command(
            label=f'运行AutoPEP8 ({get_event_key("run_auto_pep8")})', command=self.PEP8_format_code)
        self.pep8Menu.add_command(
            label=f'使用Yapf格式化文档 ({get_event_key("format_pep8_with_yapf")})', command=self.yapf_format_pep8)
        self.pep8Menu.add_command(
            label='移除尾部空格', command=self.Remove_trailing_space)
        self.pep8Menu.add_command(label='显示代码风格警告', command=self.ShowPep8Warning)
        self.root.bind(get_event('run_auto_pep8'),
                       lambda event: self.PEP8_format_code())
        self.root.bind(get_event("format_pep8_with_yapf"),
                       lambda event: self.yapf_format_pep8())
        # -------------------------------------------------------------------
        self.GotoMenu.add_command(
            label=f"转到行 ({get_event_key('go_to_line')})", command=self.goto_line)
        self.root.bind(get_event('go_to_line'), lambda event: self.goto_line())
        # -------------------------------------------------------------------
        self.RunMenu.add_command(label=f"在终端运行 ({get_event_key('run_code')})",
                                 command=self.RunCode)
        self.RunMenu.add_command(label=f'运行时添加sys.argv ({get_event_key("run_code_add_argv")})',
                                 command=lambda: self.RunCode('run with sys.argv'))
        self.RunMenu.add_command(label=f"从文件运行 ({get_event_key('run_code_with_file')})",
                                 command=self.RunWithFile)
        self.RunMenu.add_separator()  # 添加分割线
        self.RunMenu.add_cascade(label='选择Python', menu=self.RunPythonMenu)  # 添加选择Python菜单
        self.root.bind(get_event('run_code'), lambda event: self.RunCode())
        self.root.bind(get_event('run_code_add_argv'), lambda event: self.RunCode('run with sys.argv'))
        self.root.bind(get_event('run_code_with_file'), lambda event: self.RunWithFile())
        # -------------------------------------------------------------------
        self.RunPythonMenu.add_radiobutton(label='CPython',
                                           command=lambda: self.RunCode(
                                               info='set_python',
                                               python_name='python'),
                                           variable=self.DefaultPythonCommandVar)
        if self.get_install('ipython'):
            self.RunPythonMenu.add_radiobutton(label='IPython',
                                               command=lambda: self.RunCode(
                                                   info='set_python',
                                                   python_name='ipython'),
                                               variable=self.DefaultPythonCommandVar)
        if self.get_install('ptpython'):
            self.RunPythonMenu.add_radiobutton(label='PtPython',
                                               command=lambda: self.RunCode(
                                                   info='set_python',
                                                   python_name='ptpython'),
                                               variable=self.DefaultPythonCommandVar)
        # -------------------------------------------------------------------
        self.TerminalMenu.add_command(label='编辑Python Path', command=self.config_sys_path)
        self.TerminalMenu.add_command(label='生成Pyc文件', command=compile_pyc)
        self.TerminalMenu.add_separator()
        self.TerminalMenu.add_command(label='设置TkPy2', command=lambda: tkpyConfig.Show(self.root))
        # -------------------------------------------------------------------
        self.HelpMenu.add_command(label=f'打开联机帮助 ({get_event_key("help")})', command=self.web_help)
        self.HelpMenu.add_command(label=f'联机Python包帮助 ({get_event_key("help_python_doc")})',
                                  command=lambda: self.web_help('look python doc'))
        self.root.bind(get_event('help'), lambda event: self.web_help())
        self.root.bind(get_event('help_python_doc'), lambda event: self.web_help('look python doc'))
        # -------------------------------------------------------------------
        self.POPMenu.add_command(label='复制 (Ctrl-C)', command=self.Copy)
        self.POPMenu.add_command(label='粘贴 (Ctrl-V)', command=self.Paste)
        self.POPMenu.add_command(label='剪切 (Ctrl-X)', command=self.Cut)
        self.POPMenu.add_separator()  # 添加分割线
        self.POPMenu.add_command(label='撤销 (Ctrl-Z)', command=self.Undo)
        self.POPMenu.add_command(label="撤回 (Ctrl-Y)", command=self.Redo)
        # -------------------------------------------------------------------
        self.tools_bar.add_command(label='打开', command=self.open, statusmsg='打开文件')
        self.tools_bar.add_command(label='新建', command=self.new_file, statusmsg='新建文件')
        self.tools_bar.add_command(label='新建快速文件', command=self.new_scratch_file, statusmsg='新建快速文件')
        self.tools_bar.add_separator()
        self.tools_bar.add_command(label='保存', command=self.save, statusmsg='保存文件')
        self.tools_bar.add_command(label='另存为', command=lambda: self.save('saveas'), statusmsg='另存为文件')
        self.tools_bar.add_separator()
        self.tools_bar.add_command(label='查找', command=self.find_text, statusmsg='使用查找工具查找')
        self.tools_bar.add_command(label='替换', command=self.replace_text, statusmsg='替换比配项')
        self.tools_bar.add_separator()
        self.tools_bar.add_command(label='格式化文档', command=self.PEP8_format_code, statusmsg='使用AutoPEP8格式化文档')
        self.tools_bar.add_separator()
        self.tools_bar.add_command(label='帮助', command=self.web_help, statusmsg='打开TkPy的Web版帮助',
                                   balloonmsg=__doc__)
        # -------------------------------------------------------------------
        self.tip.bind_widget(self.PanedWindow, statusmsg='调整高度')

    def Redo(self):
        self.text.edit_redo()

    def Undo(self):
        self.text.edit_undo()

    def get_tk_tabwidth(self):
        current = self.text['tabs'] or TK_TABWIDTH_DEFAULT
        return int(current)

    def BackSpace(self):
        index = str(self.text.index(tk.INSERT)).split('.')
        index[1] = str(int(index[1]) - 1 if int(index[1]) - 1 >= 0 else 0)
        if float('.'.join(index)) < float(f'{index[0]}.{int(index[1]) + 1}'):
            if self.text.get(f'{index[0]}.{int(index[1]) + 1}') in (')', ']', '}', '"', "'") and self.text.get(
                    f'{index[0]}.{int(index[1])}') in ('(', '[', '{', '"', "'"):
                self.text.delete(f'{index[0]}.{int(index[1]) + 1}')
                self.text.delete(f'{index[0]}.{int(index[1])}')
                return 'break'

    def go_to_line_row(self, col, row=0):
        self.text.mark_set(tk.INSERT, f'{col}.{row}')
        self.text.see(tk.INSERT)

    def RemoveAllHistory(self):
        global history
        if not tkMessageBox.askokcancel('问题', '是否删除全部历史记录?'):
            return
        self.HistoryMenu.delete(2, tk.END)
        history = []
        self.set_history.write(value=history)

    def unTab(self):
        try:
            text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) \
                .replace(Tab_Text, self.get_tk_tabwidth()).split('\n')
            for i in range(len(text)):
                text[i] = text[5:-1]
        except:
            pass
        else:
            text = '\n'.join(text)
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert('insert', text)

    def new_scratch_file(self):
        def del_file():
            name = file_name.format(i)
            os.remove(os.path.join(file_path, name))
            root.root.destroy()

        file_path = os.path.join(os.environ['TMP'], 'tkpy2')
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        file_name = 'python_scratch{}.py'
        i = 0
        while True:
            if not os.path.isfile(os.path.join(file_path, file_name.format(i))):
                break
            i += 1
        open(os.path.join(file_path, file_name.format(i)), 'w').close()
        root = self.new_window()
        root.root.protocol('WM_DELETE_WINDOW', del_file)
        root.open(os.path.join(file_path, file_name.format(i)))

    def RunFlake8Linter(self):
        if not self.file_name:
            return tkMessageBox.showinfo('提示', '需要打开文件')
        code = Flake8Linter(self.file_name)
        Errors = code.get_statistics('E')
        Warnings = code.get_statistics('W')
        Infos = code.get_statistics('F')
        if Errors:
            print('Errors:\n')
            for i in Errors:
                print(i)
        if Warnings:
            print('Warnings:\n')
            for i in Warnings:
                print(i)
        if Infos:
            print('Infos:\n')
            for i in Infos:
                print(i)

    def Remove_trailing_space(self):
        code = self.text.get(0.0, tk.END).rstrip()
        self.text.delete(0.0, tk.END)
        self.text.insert(tk.END, code)

    def ShowPep8Warning(self):
        if not self.yesnosavefile:
            tkMessageBox.showinfo('提示', '未打开文件,需要打开文件再查看。')
            return
        root = tk.Toplevel()
        root.title('PEP8 警告')
        tree = ttk.Treeview(root, columns=('文件名', '行', '列', '错误代码', '错误文本'))
        tree.heading('#0', text='文件名')
        tree.heading('#1', text='行')
        tree.heading('#2', text='列')
        tree.heading('#3', text='错误代码')
        tree.heading('#4', text='错误文本')
        tree.pack(fill=tk.BOTH, expand=True)
        assert_data = assert_pep8(self.file_name)
        if assert_data != 'not install':
            for i in assert_data:
                try:
                    tree.insert('', indxe=tk.END, text=i[0], values=(i[1], i[2], i[3], i[4]))
                except:
                    tkMessageBox.showinfo('提示', '你的代码没有任何PEP8警告。')
                    root.destroy()
        else:
            tkMessageBox.showinfo('提示', '检测工具未安装。')
            root.destroy()

    def set_tk_tabwidth(self, newtabwidth):
        text = self.text
        if self.get_tk_tabwidth() != newtabwidth:
            # Set text widget tab width
            pixels = text.tk.call("font", "measure", text["font"],
                                  "-displayof", text.master,
                                  "n" * newtabwidth)
            text.configure(tabs=pixels)

    def open_pop_Menu(self, event):
        self.POPMenu.post(event.x_root, event.y_root)

    def get_install(self, name: str):
        return name in get_all_packages()

    def Copy(self):
        self.text.event_generate('<<Copy>>')

    def Cut(self):
        self.text.event_generate('<<Cut>>')
        self.assert_text()

    def Paste(self):
        self.text.event_generate("<<Paste>>")
        self.assert_text()

    def assert_text(self):
        self.linenumbers.redraw()
        if self.yesnosavefile:
            if self.yesnoopenautosave.get():
                self.save()
                self.code_save = True
            else:
                try:
                    with open(self.file_name, encoding=self.encoding) as f:
                        if assert_text(f.read() + '\n', self.text.get(0.0, tk.END)):
                            self.root.title(self.config['init_title'] + ' ' + self.file_name + ' (未保存文件)')
                            self.code_save = False
                        else:
                            self.code_save = True
                            self.root.title(self.config['init_title'] + ' ' + self.file_name)
                except (FileExistsError, FileNotFoundError):
                    tkMessageBox.showinfo('提示', '文件被移动、删除或被重命名。')
                    self.code_save = False
                    self.yesnosavefile = False
                    self.assert_text()
        else:
            data = assert_text(self.config['new_file_text'] + '\n', self.text.get(0.0, tk.END))
            if data:
                self.root.title(self.config['init_title'] + ' (未保存文件)')
                self.code_save = False
            else:
                self.root.title(self.config['init_title'])
                self.code_save = True

    def config_sys_path(self):
        def add(mode='user'):
            if mode == 'all':
                for item in sys.path:
                    lb.insert(tk.END, item)
                return
            elif mode == 'user':
                name = tkFileDialog.askdirectory(title='请选择目录')
                if name:
                    lb.insert(tk.END, name)

        def getIndex(event):
            lb.index = lb.nearest(event.y)

        def dragJob(event):
            newIndex = lb.nearest(event.y)
            if newIndex < lb.index:
                x = lb.get(newIndex)
                lb.delete(newIndex)
                lb.insert(newIndex + 1, x)
                lb.index = newIndex
            elif newIndex > lb.index:
                x = lb.get(newIndex)
                lb.delete(newIndex)
                lb.insert(newIndex - 1, x)
                lb.index = newIndex

        def remove(mode='user'):
            if mode == 'all':
                lb.delete(0, tk.END)
            elif mode == 'user':
                try:
                    index = lb.curselection()
                    lb.delete(index)
                except:
                    pass

        def save():
            sys.path = list(lb.get(0, tk.END))

        def ExitMessage():
            if sys.path == list(lb.get(0, tk.END)):
                root.destroy()
            else:
                res = tkMessageBox.askyesnocancel('问题-未保存', '设置尚未保存,是否退出?')
                if res is None:
                    return
                elif not res:
                    root.destroy()
                elif res:
                    save()
                    root.destroy()

        def open_with():
            try:
                index = lb.curselection()
                os.system(f'explorer.exe {lb.get(index)}')
            except:
                pass

        root = tk.Toplevel()
        root.transient(self.root)
        tip = tk.Balloon(root, initwait=0)
        root.protocol('WM_DELETE_WINDOW', ExitMessage)
        root.bind(get_event('Control', 's'), lambda event: save())
        popMenu = tk.Menu(root, tearoff=False)
        popMenu.add_command(label='添加', command=add)
        popMenu.add_command(label='移除选定项', command=remove)
        if os_name == 'nt':
            popMenu.add_command(label='使用资源管理器打开', command=open_with)
        root.bind(get_event('Button', '3'), lambda event: popMenu.post(event.x_root, event.y_root))
        root.bind(get_event('Control', 'a'), lambda event: add())
        root.bind(get_event('Control', 'r'), lambda event: remove())
        root.bind(get_event('Control', 'o'), lambda event: open_with())
        root.minsize(600, 300)
        root.title('Python Path管理器')
        Frame = tk.Frame(root)
        lb = tk.Listbox(Frame)
        ycrollbar = tk.Scrollbar(Frame)
        ycrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lb.config(yscrollcommand=ycrollbar.set)
        ycrollbar.config(command=lb.yview)
        lb.pack(fill=tk.BOTH, expand=True)
        lb.bind(get_event('Button', '1'), getIndex)
        lb.bind(get_event('B1', 'Motion'), dragJob)
        open_with_explorerButton = ttk.Button(root, text='使用资源管理器打开 (Ctrl-O)', command=open_with)
        tip.bind_widget(open_with_explorerButton,
                        balloonmsg='使用Windows资源管理器打开')
        addButton = ttk.Button(root, text='添加 (Ctrl-A)', command=add)
        tip.bind_widget(addButton, balloonmsg='添加一个Python变量')
        saveButton = ttk.Button(root, text='保存 (Ctrl-S)', command=save)
        tip.bind_widget(saveButton, balloonmsg='保存所有的更改')
        removeButton = ttk.Button(root, text='移除选定项 (Ctrl-R)', command=remove)
        tip.bind_widget(removeButton, balloonmsg='删除选择的变量')
        Frame.pack(fill=tk.BOTH, expand=True)
        addButton.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        saveButton.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        if os_name == 'nt':
            open_with_explorerButton.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        removeButton.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        add('all')

    def find_text(self):
        find(self.text)

    def replace_text(self, event=False):
        if event:
            self.text.insert('insert', '\n')
        replace(self.text)
        self.assert_text()

    def RunWithFile(self):
        file_name = tkFileDialog.askopenfilename(title='打开文件',
                                                 filetypes=self.all_file_types).replace('\\', '/')
        run_command = self.config["DefaultRunCodeCommand"]
        dir_name = os.getcwd()
        if file_name:
            os.chdir("/".join(file_name.split('/')[0:-1]))
            data = f"start python -c \"{run_command}\"".format(
                python_name=self.config['DefaultPythonCommand'], file_name=file_name)
            os.system(data)
        os.chdir(dir_name)

    def RunCode(self, info=None, python_name=None):
        run_command = self.config["DefaultRunCodeCommand"]
        if info:
            if info == 'set_python':
                self.set_config.write('DefaultPythonCommand', python_name)
            elif info == 'run with sys.argv':
                if not self.config["ShowAskDialogToRun"]:
                    self.save()
                else:
                    if not tkMessageBox.askyesno('问题', '是否保存文件然后再运行?'):
                        return
                    self.save()
                if self.file_name == "":
                    return
                run_command = self.config["DefaultRunArgvCodeCommand"]
                argv = tkinter.simpledialog.askstring('问题', '请输入sys.argv:')
                if not argv:
                    return
                data = f"start python -c \"{run_command}\"".format(
                    python_name=self.config['DefaultPythonCommand'], file_name=self.file_name, argv=argv)
                os.chdir("/".join(self.file_name.split('/')[0:-1]))
                os.system(data)
        else:
            if not self.config["ShowAskDialogToRun"]:
                self.save()
            else:
                if not tkMessageBox.askyesno('问题', '是否保存文件然后再运行?'):
                    return
                self.save()
            if self.file_name == "":
                return
            data = f"start python -c \"{run_command}\"".format(
                python_name=self.config['DefaultPythonCommand'], file_name=self.file_name)
            os.chdir("/".join(self.file_name.split('/')[0:-1]))
            os.system(data)

    def web_help(self, name=None):
        """打开帮助"""
        if name is None:
            webbrowser.open(f"http://{serverconfig['host']}:{serverconfig['port']}")
        elif name == 'look python doc':
            name = tkinter.simpledialog.askstring('问题', '请输入包名,TkPy会寻找帮助:')
            if name:
                try:
                    import_module(name)
                except:
                    if not tkMessageBox.askyesno('问题', '在计算机上未找到此包,是否打开网页?'):
                        return
                webbrowser \
                    .open(f'http://{serverconfig["host"]}:{serverconfig["port"]}/TkPy/doc/python?name={name}')

    def autoJEDIInput(self, event=0):
        """JEDI补全"""

        def ok(event):
            try:
                obj = event.widget
                get_data = ""
                items = obj.curselection()
                for line in items:
                    get_data = (ListBox.get(line))
                if len(get_data):
                    data = input_data[get_data]
                    self.text.insert("insert", data)
                self.text.focus_set()
                Frame.place_forget()
            except (IndexError, tk.TclError):
                pass

        source = self.text.get(0.0, self.text.index("insert"))
        script = jedi.Script(source, path='<TkPy2>' if not self.file_name else self.file_name)
        completions = script.completions()
        if len(completions) == 1:
            self.text.insert("insert", completions[0].complete)
            return
        elif len(completions) == 0:
            return
        input_data = {}
        root = tk.Toplevel()
        root.overrideredirect(True)
        Frame = tk.Frame(root)
        scrollbar = tk.Scrollbar(Frame)
        ListBox = tk.Listbox(Frame)
        ListBox.bind(get_event('Double', 'Button', '1'), ok)
        ListBox.bind(get_event('Return'), ok)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        ListBox.pack(fill=tk.BOTH, expand=True)
        ListBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=ListBox.yview)
        Frame.pack(fill=tk.BOTH, expand=True)
        root.geometry("400x200+30+50")
        root.focus_set()
        ListBox.focus_set()
        root.bind("<FocusOut>", lambda event: root.destroy())
        for i in range(len(completions)):
            input_data[completions[i].name] = completions[i].complete
            if completions[i].complete != "":
                print(self.text.get(tk.INSERT))
                ListBox.insert(tk.END, completions[i].name)
        return 'break'

    def out_for_html(self):
        """输出Html的Python代码"""
        code = self.text.get(0.0, tk.END)
        return_data = '<style type="text/css">\n' + \
                      get_css.out_for_css(self.config['default_html_css_name']) + "</style>" \
                      + \
                      highlight(code, PythonLexer(),
                                HtmlFormatter(
                                    linenos=self.config['Htmlshowlinenumbers']))
        out_file_name = tkFileDialog.asksaveasfilename(
            title="另存为Html文件", filetypes=self.out_html_file_types,
            defaultextension='.html')
        if out_file_name != "":
            with open(out_file_name, 'w', encoding=self.encoding) as f:
                f.write(return_data)

    def new_file(self):
        if not self.code_save:
            res = tkMessageBox.askyesnocancel('问题-文件未保存', '文件未保存,是否保存文件再新建文件?')
            if res:
                self.save()
                if self.file_name == '':
                    return
            elif res is None:
                return
        self.code_save = True
        self.yesnosavefile = False
        self.text.config(state=tk.NORMAL)
        self.text.delete(0.0, tk.END)
        self.text.insert(tk.END, self.config['new_file_text'])
        self.assert_text()

    def PEP8_format_code(self):
        try:
            text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not text:
                raise
        except:
            text = self.text.get(0.0, tk.END)
        else:
            code = autopep8.fix_code(text)[0:-1]
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert('insert', code)
            self.assert_text()
            return
        index = self.text.index('insert')
        code = autopep8.fix_code(text)
        self.text.delete(0.0, tk.END)
        self.text.insert(tk.END, code)
        self.assert_text()
        self.text.mark_set("insert", f"{index}")
        self.text.see("insert")

    def yapf_format_pep8(self):
        try:
            text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not text:
                raise
        except:
            text = self.text.get(0.0, tk.END)
        else:
            code = FormatCode(text)[0][0:-1]
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert('insert', code)
            self.assert_text()
            return
        try:
            code = FormatCode(text)[0]
        except:
            tkMessageBox.showerror('提示', '你的代码里有错,请检查你的代码。')
            return
        index = self.text.index('insert')
        self.text.delete(0.0, tk.END)
        self.text.insert(tk.END, code)
        self.assert_text()
        self.text.mark_set("insert", f"{index}")
        self.text.see("insert")

    def new_window(self):
        root = MainWindow()
        root.get_start()
        return root

    def open(self, file_name=None):
        global history
        if not self.code_save:
            if tkMessageBox.askyesno('问题', '还有文件未保存,是否保存?'):
                self.save()
        if file_name is None:
            self.file_name = tkFileDialog.askopenfilename(
                title="打开文件",
                filetypes=self.all_file_types, parent=self.root)  # 打开文件
        else:
            self.file_name = file_name
        self.file_name = self.file_name.replace('\\', '/')
        if self.file_name != '':
            self.text.config(state=tk.NORMAL)
            if not os.path.isfile(self.file_name):
                tkMessageBox.showinfo('提示', '文件被移动、删除或被重命名。')
                return
            if self.file_name not in self.history:
                history.append(self.file_name)
                self.HistoryMenu.add_command(label=self.file_name,
                                             command=lambda: self.open(copy.copy(self.file_name)))
                self.set_history.write(value=set(history) | set(self.history))
            self.root.title(self.config['init_title'] + ' ' + self.file_name)
            self.text.delete(0.0, tk.END)
            self.file = open(self.file_name, 'rb')  # 字节码打开文件
            self.encoding = 'utf-8'  # if get_encoding(
            # self.file.read())['confidence'] < 0.96 else get_encoding(
            # self.file.read())['encoding']  # 获取编码
            self.file = open(self.file_name, encoding=self.encoding)
            self.text.insert(tk.END, self.file.read())
            self.file.close()  # 关闭源文件
            if self.config['open_and_save_file_auto_chdir']:
                os.chdir('/'.join(self.file_name.split('/')[0:-2]))
            self.yesnosavefile = True  # 已保存文件
            self.code_save = True  # 已经一样
            self.save()
            self.assert_text()

    def save(self, command='save', format_pep8=False):
        global auto_save
        if format_pep8:
            if self.config['format_code_on_save']:
                self.PEP8_format_code()
        if command == 'autosave':
            auto_save = self.yesnoopenautosave.get()
            self.set_config.write('auto_save', auto_save)
            self.assert_text()
        elif command == 'save':
            if self.yesnosavefile:
                try:
                    with open(self.file_name, 'w', encoding=self.encoding) as f:
                        f.write(self.text.get(0.0, tk.END))
                except PermissionError:
                    self.text.config(state=tk.DISABLED)
                else:
                    self.text.config(state=tk.NORMAL)
                self.code_save = True
                self.root.title(self.config['init_title'] + ' ' + self.file_name)
                if self.config['open_and_save_file_auto_chdir']:
                    os.chdir('/'.join(self.file_name.split('/')[0:-2]))
            else:
                self.file_name = tkFileDialog.asksaveasfilename(
                    title="保存", filetypes=self.all_file_types,
                    defaultextension='.py')
                self.file_name = self.file_name.replace('\\', '/')
                if self.file_name != '':
                    if self.file_name not in self.history:
                        history.append(self.file_name)
                        self.HistoryMenu.add_command(label=self.file_name,
                                                     command=lambda: self.open(copy.copy(self.file_name)))
                        self.set_history.write(value=set(history) | set(self.history))
                    self.root.title(self.config['init_title'] + ' ' + self.file_name)
                    try:
                        with open(self.file_name, 'w', encoding=self.encoding) as f:
                            f.write(self.text.get(0.0, tk.END))
                    except PermissionError:
                        tkMessageBox.showerror('提示', '保存失败,因为无权利访问。')
                    self.yesnosavefile = True
                    self.code_save = True
                    if self.config['open_and_save_file_auto_chdir']:
                        os.chdir('/'.join(self.file_name.split('/')[0:-2]))
        elif command == 'saveas':
            self.file_name = tkFileDialog.asksaveasfilename(
                title='另存为', filetypes=self.all_file_types,
                defaultextension='.py')
            if self.file_name != '':
                if self.file_name not in self.history:
                    history.append(self.file_name)
                    self.HistoryMenu.add_command(label=self.file_name,
                                                 command=lambda: self.open(copy.copy(self.file_name)))
                    self.set_history.write(value=set(history) | set(self.history))
                self.root.title(self.config['init_title'] + ' ' + self.file_name)
                try:
                    with open(self.file_name, 'w', encoding=self.encoding) as f:
                        f.write(self.text.get(0.0, tk.END))
                except PermissionError:
                    tkMessageBox.showerror('提示', '保存失败,因为无权利访问。')
                self.yesnosavefile = True
                self.code_save = True
                if self.config['open_and_save_file_auto_chdir']:
                    os.chdir('/'.join(self.file_name.split('/')[0:-2]))
        elif command == 'exit':
            self.save()
            if self.file_name == '':
                return False
            return True

    def goto_line(self, lineno=None):
        """转到行"""
        text = self.text
        if not lineno:
            lineno = tkinter.simpledialog.askinteger("转到",
                                                     "请输入行:", parent=text)
        if lineno is None:
            return "break"

        text.mark_set("insert", "%d.0" % lineno)
        text.see("insert")
        return "break"

    def mainloop(self, n=0):
        """进入主循环"""
        self.root.mainloop(n)  # 进入主循环
        return n


def main():
    try:
        server.start_doc_server()
        root = MainWindow()
        root.get_start()
        data_root.mainloop()
        server.stop_doc_server()
    except KeyboardInterrupt:
        return -1
    return 0


if __name__ == "__main__":
    main()
