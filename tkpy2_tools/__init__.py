# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: __init__.py
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/29-14:10
# 创建时的IDE名称: PyCharm

"""Replace dialog for TkPy2. Inherits SearchDialogBase for GUI.
Uses TkPy2.tkpy_tools.SearchDialogBase for search capability.
Defines various replace related functions like replace, replace all,
and replace+find.
"""
import os
import py_compile
import re
import sys
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import traceback
from idlelib import searchengine
from tkinter import StringVar, TclError, Toplevel, Tk
from tkinter.constants import *
from tkinter.ttk import Frame, Entry, Label, Button, Checkbutton, Radiobutton
import default_config
from pip._internal.utils.misc import get_installed_distributions
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import STYLE_MAP


class SearchDialogBase:
    """Create most of a 3 or 4 row, 3 column search dialog.

    The left and wide middle column contain:
    1 or 2 labeled text entry lines (make_entry, create_entries);
    a row of standard Checkbuttons (make_frame, create_option_buttons),
    each of which corresponds to a search engine Variable;
    a row of dialog-specific Check/Radiobuttons (create_other_buttons).

    The narrow right column contains command buttons
    (make_button, create_command_buttons).
    These are bound to functions that execute the command.

    Except for command buttons, this base class is not limited to items
    common to all three subclasses.  Rather, it is the Find dialog minus
    the "Find Next" command, its execution function, and the
    default_command attribute needed in create_widgets. The other
    dialogs override attributes and methods, the latter to replace and
    add widgets.
    """

    title = "查找"  # replace in subclasses
    icon = "Search"
    needwrapbutton = 1  # not in Find in Files

    def __init__(self, root, engine):
        """Initialize root, engine, and top attributes.

        top (level widget): set in create_widgets() called from open().
        text (Text searched): set in open(), only used in subclasses().
        ent (ry): created in make_entry() called from create_entry().
        row (of grid): 0 in create_widgets(), +1 in make_entry/frame().
        default_command: set in subclasses, used in create_widgets().

        title (of dialog): class attribute, override in subclasses.
        icon (of dialog): ditto, use unclear if cannot minimize dialog.
        """
        self.root = root
        self.bell = root.bell
        self.engine = engine
        self.top = None

    def open(self, text, searchphrase=None):
        """Make dialog visible on top of others and ready to use."""
        self.text = text
        if not self.top:
            self.create_widgets()
        else:
            self.top.deiconify()
            self.top.tkraise()
        self.top.transient(text.winfo_toplevel())
        if searchphrase:
            self.ent.delete(0, "end")
            self.ent.insert("end", searchphrase)
        self.ent.focus_set()
        self.ent.selection_range(0, "end")
        self.ent.icursor(0)
        self.top.grab_set()

    def close(self, event=None):
        """Put dialog away for later use."""
        if self.top:
            self.top.grab_release()
            self.top.transient('')
            self.top.withdraw()

    def create_widgets(self):
        """Create basic 3 row x 3 col search (find) dialog.

        Other dialogs override subsidiary create_x methods as needed.
        Replace and Find-in-Files add another entry row.
        """
        top = Toplevel(self.root)
        top.bind("<Return>", self.default_command)
        top.bind("<Escape>", self.close)
        top.protocol("WM_DELETE_WINDOW", self.close)
        top.wm_title(self.title)
        top.wm_iconname(self.icon)
        self.top = top

        self.row = 0
        self.top.grid_columnconfigure(0, pad=2, weight=0)
        self.top.grid_columnconfigure(1, pad=2, minsize=100, weight=100)

        self.create_entries()  # row 0 (and maybe 1), cols 0, 1
        self.create_option_buttons()  # next row, cols 0, 1
        self.create_other_buttons()  # next row, cols 0, 1
        self.create_command_buttons()  # col 2, all rows

    def make_entry(self, label_text, var):
        """Return (entry, label), .

        entry - gridded labeled Entry for text entry.
        label - Label widget, returned for testing.
        """
        label = Label(self.top, text=label_text)
        label.grid(row=self.row, column=0, sticky="nw")
        entry = Entry(self.top, textvariable=var, exportselection=0)
        entry.grid(row=self.row, column=1, sticky="nwe")
        self.row = self.row + 1
        return entry, label

    def create_entries(self):
        "Create one or more entry lines with make_entry."
        self.ent = self.make_entry("查找内容:", self.engine.patvar)[0]

    def make_frame(self, labeltext=None):
        '''Return (frame, label).

        frame - gridded labeled Frame for option or other buttons.
        label - Label widget, returned for testing.
        '''
        if labeltext:
            label = Label(self.top, text=labeltext)
            label.grid(row=self.row, column=0, sticky="nw")
        else:
            label = ''
        frame = Frame(self.top)
        frame.grid(row=self.row, column=1, columnspan=1, sticky="nwe")
        self.row = self.row + 1
        return frame, label

    def create_option_buttons(self):
        '''Return (filled frame, options) for testing.

        Options is a list of searchengine booleanvar, label pairs.
        A gridded frame from make_frame is filled with a Checkbutton
        for each pair, bound to the var, with the corresponding label.
        '''
        frame = self.make_frame("选项: ")[0]
        engine = self.engine
        options = [(engine.revar, "使用正则表达式"),
                   (engine.casevar, "区分大小写"),
                   (engine.wordvar, "全字比配")]
        if self.needwrapbutton:
            options.append((engine.wrapvar, "环绕寻找"))
        for var, label in options:
            btn = Checkbutton(frame, variable=var, text=label)
            btn.pack(side="left", fill="both")
        return frame, options

    def create_other_buttons(self):
        '''Return (frame, others) for testing.

        Others is a list of value, label pairs.
        A gridded frame from make_frame is filled with radio buttons.
        '''
        frame = self.make_frame("查找方向: ")[0]
        var = self.engine.backvar
        others = [(1, '上'), (0, '下')]
        for val, label in others:
            btn = Radiobutton(frame, variable=var, value=val, text=label)
            btn.pack(side="left", fill="both")
        return frame, others

    def make_button(self, label, command, isdef=0):
        "Return command button gridded in command frame."
        b = Button(self.buttonframe,
                   text=label, command=command,
                   default=isdef and "active" or "normal")
        cols, rows = self.buttonframe.grid_size()
        b.grid(pady=1, row=rows, column=0, sticky="ew")
        self.buttonframe.grid(rowspan=rows + 1)
        return b

    def create_command_buttons(self):
        "Place buttons in vertical command frame gridded on right."
        f = self.buttonframe = Frame(self.top)
        f.grid(row=0, column=2, padx=2, pady=2, ipadx=2, ipady=2)

        b = self.make_button("关闭", self.close)
        b.lower()


class _searchbase(SearchDialogBase):  # htest #
    "Create auto-opening dialog with no text connection."

    def __init__(self, parent):
        self.root = parent
        self.engine = searchengine.get(parent)
        self.create_widgets()
        print(parent.geometry())
        width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
        self.top.geometry("+%d+%d" % (x + 40, y + 175))

    def default_command(self, dummy): pass


def replace(text):
    """Create or reuse a singleton ReplaceDialog instance.

    The singleton dialog saves user entries and preferences
    across instances.

    Args:
        text: Text widget containing the text to be searched.
    """
    root = text._root()
    engine = searchengine.get(root)
    if not hasattr(engine, "_replacedialog"):
        engine._replacedialog = ReplaceDialog(root, engine)
    dialog = engine._replacedialog
    dialog.open(text)


class ReplaceDialog(SearchDialogBase):
    "Dialog for finding and replacing a pattern in text."

    title = "替换"
    icon = "Replace"

    def __init__(self, root, engine):
        """Create search dialog for finding and replacing text.

        Uses SearchDialogBase as the basis for the GUI and a
        searchengine instance to prepare the search.

        Attributes:
            replvar: StringVar containing 'Replace with:' value.
            replent: Entry widget for replvar.  Created in
                create_entries().
            ok: Boolean used in searchengine.search_text to indicate
                whether the search includes the selection.
        """
        super().__init__(root, engine)
        self.replvar = StringVar(root)

    def open(self, text):
        """Make dialog visible on top of others and ready to use.

        Also, highlight the currently selected text and set the
        search to include the current selection (self.ok).

        Args:
            text: Text widget being searched.
        """
        SearchDialogBase.open(self, text)
        try:
            first = text.index("sel.first")
        except TclError:
            first = None
        try:
            last = text.index("sel.last")
        except TclError:
            last = None
        first = first or text.index("insert")
        last = last or first
        self.show_hit(first, last)
        self.ok = True

    def create_entries(self):
        "Create base and additional label and text entry widgets."
        SearchDialogBase.create_entries(self)
        self.replent = self.make_entry("替换文字:", self.replvar)[0]

    def create_command_buttons(self):
        """Create base and additional command buttons.

        The additional buttons are for Find, Replace,
        Replace+Find, and Replace All.
        """
        SearchDialogBase.create_command_buttons(self)
        self.make_button("查找下一个", self.find_it)
        self.make_button("替换下一个", self.replace_it)
        self.make_button("查找并替换下一个", self.default_command, isdef=True)
        self.make_button("替换全部", self.replace_all)

    def find_it(self, event=None):
        "Handle the Find button."
        self.do_find(False)

    def replace_it(self, event=None):
        """Handle the Replace button.

        If the find is successful, then perform replace.
        """
        if self.do_find(self.ok):
            self.do_replace()

    def default_command(self, event=None):
        """Handle the Replace+Find button as the default command.

        First performs a replace and then, if the replace was
        successful, a find next.
        """
        if self.do_find(self.ok):
            if self.do_replace():  # Only find next match if replace succeeded.
                # A bad re can cause it to fail.
                self.do_find(False)

    def _replace_expand(self, m, repl):
        "Expand replacement text if regular expression."
        if self.engine.isre():
            try:
                new = m.expand(repl)
            except re.error:
                self.engine.report_error(repl, 'Invalid Replace Expression')
                new = None
        else:
            new = repl

        return new

    def replace_all(self, event=None):
        """Handle the Replace All button.

        Search text for occurrences of the Find value and replace
        each of them.  The 'wrap around' value controls the start
        point for searching.  If wrap isn't set, then the searching
        starts at the first occurrence after the current selection;
        if wrap is set, the replacement starts at the first line.
        The replacement is always done top-to-bottom in the text.
        """
        prog = self.engine.getprog()
        if not prog:
            return
        repl = self.replvar.get()
        text = self.text
        res = self.engine.search_text(text, prog)
        if not res:
            self.bell()
            return
        text.tag_remove("sel", "1.0", "end")
        text.tag_remove("hit", "1.0", "end")
        line = res[0]
        col = res[1].start()
        if self.engine.iswrap():
            line = 1
            col = 0
        ok = True
        first = last = None
        # XXX ought to replace circular instead of top-to-bottom when wrapping
        text.undo_block_start()
        while True:
            res = self.engine.search_forward(text, prog, line, col,
                                             wrap=False, ok=ok)
            if not res:
                break
            line, m = res
            chars = text.get("%d.0" % line, "%d.0" % (line + 1))
            orig = m.group()
            new = self._replace_expand(m, repl)
            if new is None:
                break
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            if new == orig:
                text.mark_set("insert", last)
            else:
                text.mark_set("insert", first)
                if first != last:
                    text.delete(first, last)
                if new:
                    text.insert(first, new)
            col = i + len(new)
            ok = False
        text.undo_block_stop()
        if first and last:
            self.show_hit(first, last)
        self.close()

    def do_find(self, ok=False):
        """Search for and highlight next occurrence of pattern in text.

        No text replacement is done with this option.
        """
        if not self.engine.getprog():
            return False
        text = self.text
        res = self.engine.search_text(text, None, ok)
        if not res:
            self.bell()
            return False
        line, m = res
        i, j = m.span()
        first = "%d.%d" % (line, i)
        last = "%d.%d" % (line, j)
        self.show_hit(first, last)
        self.ok = True
        return True

    def do_replace(self):
        "Replace search pattern in text with replacement value."
        prog = self.engine.getprog()
        if not prog:
            return False
        text = self.text
        try:
            first = pos = text.index("sel.first")
            last = text.index("sel.last")
        except TclError:
            pos = None
        if not pos:
            first = last = pos = text.index("insert")
        line, col = searchengine.get_line_col(pos)
        chars = text.get("%d.0" % line, "%d.0" % (line + 1))
        m = prog.match(chars, col)
        if not prog:
            return False
        new = self._replace_expand(m, self.replvar.get())
        if new is None:
            return False
        text.mark_set("insert", first)
        text.undo_block_start()
        if m.group():
            text.delete(first, last)
        if new:
            text.insert(first, new)
        text.undo_block_stop()
        self.show_hit(first, text.index("insert"))
        self.ok = False
        return True

    def show_hit(self, first, last):
        """Highlight text between first and last indices.

        Text is highlighted via the 'hit' tag and the marked
        section is brought into view.

        The colors from the 'hit' tag aren't currently shown
        when the text is displayed.  This is due to the 'sel'
        tag being added first, so the colors in the 'sel'
        config are seen instead of the colors for 'hit'.
        """
        text = self.text
        text.mark_set("insert", first)
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", first, last)
        text.tag_remove("hit", "1.0", "end")
        if first == last:
            text.tag_add("hit", first)
        else:
            text.tag_add("hit", first, last)
        text.see("insert")
        text.update_idletasks()

    def close(self, event=None):
        "Close the dialog and remove hit tags."
        SearchDialogBase.close(self, event)
        self.text.tag_remove("hit", "1.0", "end")


def _setup(text):
    """Return the new or existing singleton SearchDialog instance.

    The singleton dialog saves user entries and preferences
    across instances.

    Args:
        text: Text widget containing the text to be searched.
    """
    root = text._root()
    engine = searchengine.get(root)
    if not hasattr(engine, "_searchdialog"):
        engine._searchdialog = SearchDialog(root, engine)
    return engine._searchdialog


def find(text):
    """Open the search dialog.

    Module-level function to access the singleton SearchDialog
    instance and open the dialog.  If text is selected, it is
    used as the search phrase; otherwise, the previous entry
    is used.  No search is done with this command.
    """
    pat = text.get("sel.first", "sel.last")
    return _setup(text).open(text, pat)  # Open is inherited from SDBase.


def find_again(text):
    """Repeat the search for the last pattern and preferences.

    Module-level function to access the singleton SearchDialog
    instance to search again using the user entries and preferences
    from the last dialog.  If there was no prior search, open the
    search dialog; otherwise, perform the search without showing the
    dialog.
    """
    return _setup(text).find_again(text)


def find_selection(text):
    """Search for the selected pattern in the text.

    Module-level function to access the singleton SearchDialog
    instance to search using the selected text.  With a text
    selection, perform the search without displaying the dialog.
    Without a selection, use the prior entry as the search phrase
    and don't display the dialog.  If there has been no prior
    search, open the search dialog.
    """
    return _setup(text).find_selection(text)


class SearchDialog(SearchDialogBase):
    """Dialog for finding a pattern in text."""

    def create_widgets(self):
        "Create the base search dialog and add a button for Find Next."
        SearchDialogBase.create_widgets(self)
        # TODO - why is this here and not in a create_command_buttons?
        self.make_button("查找下一个", self.default_command, isdef=True)

    def default_command(self, event=None):
        "Handle the Find Next button as the default command."
        if not self.engine.getprog():
            return
        self.find_again(self.text)

    def find_again(self, text):
        """Repeat the last search.

        If no search was previously run, open a new search dialog.  In
        this case, no search is done.

        If a search was previously run, the search dialog won't be
        shown and the options from the previous search (including the
        search pattern) will be used to find the next occurrence
        of the pattern.  Next is relative based on direction.

        Position the window to display the located occurrence in the
        text.

        Return True if the search was successful and False otherwise.
        """
        if not self.engine.getpat():
            self.open(text)
            return False
        if not self.engine.getprog():
            return False
        res = self.engine.search_text(text)
        if res:
            line, m = res
            i, j = m.span()
            first = "%d.%d" % (line, i)
            last = "%d.%d" % (line, j)
            try:
                selfirst = text.index("sel.first")
                sellast = text.index("sel.last")
                if selfirst == first and sellast == last:
                    self.bell()
                    return False
            except TclError:
                pass
            text.tag_remove("sel", "1.0", "end")
            text.tag_add("sel", first, last)
            text.mark_set("insert", self.engine.isback() and first or last)
            text.see("insert")
            return True
        else:
            self.bell()
            return False

    def find_selection(self, text):
        """Search for selected text with previous dialog preferences.

        Instead of using the same pattern for searching (as Find
        Again does), this first resets the pattern to the currently
        selected text.  If the selected text isn't changed, then use
        the prior search phrase.
        """
        pat = text.get("sel.first", "sel.last")
        if pat:
            self.engine.setcookedpat(pat)
        return self.find_again(text)


class highlight(object):
    def __init__(self):
        super(highlight, self).__init__()

    def out_for_css(self, style=None, name='python') -> str:

        lexer = get_lexer_by_name(name)

        # 指定风格
        if style:
            formatter = HtmlFormatter(style=style)
        else:
            formatter = HtmlFormatter()

        # 获取css
        css = formatter.get_style_defs('.highlight')

        return css

    def get_all_css_name(self) -> list:
        return STYLE_MAP.keys()


get_css = highlight()


def showtraceback() -> str:
    """Display the exception that just occurred.

    We remove the first stack item because it is our own code.

    The output is written by tk.messagebox, below.

    """
    sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
    sys.last_traceback = last_tb
    try:
        lines = traceback.format_exception(ei[0], ei[1], last_tb.tb_next)
        if sys.excepthook is sys.__excepthook__:
            return ''.join(lines)
        else:
            # If someone has set sys.excepthook, we let that take precedence
            sys.excepthook(ei[0], ei[1], last_tb)
    finally:
        last_tb = ei = None


def get_all_packages():
    """获取所有安装的包"""
    installed_packages = get_installed_distributions()
    installed_packages_dict = {}
    for i in installed_packages:
        installed_packages_dict[i.key] = i.version
    return installed_packages_dict


def compile_pyc():
    file_paths = tkFileDialog.askopenfilenames(title='打开文件', filetypes=[('所有支持的文件', ('.py', '.pyw'))])
    if not file_paths:
        return
    try:
        files = []
        for file_path in file_paths:
            files.append(py_compile.compile(file_path))
        if tkMessageBox.askyesno('提示', "生成完成,文件:{}\n是否打开文件夹?".format('\n'.join(files))):
            for path in files:
                print(path)
                path = '/'.join(path.replace('\\', '/').split('/')[0:-1])
                print(path)
                os.startfile(path)
    except Exception:
        tkMessageBox.showerror('提示', '编译时出现了错误。')


class TkPyWindowConfig:
    def __repr__(self):
        return f'!.TkPy2 {repr(self.__class__.__name__)} object'

    def __str__(self):
        raise TypeError(self.__repr__() + '不支持转换成Str类型。') from None
