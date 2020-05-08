# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: tkpy_file
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/4/29-20:18
# 创建时的IDE名称: PyCharm

from pickleshare import PickleShareDB


class read_tkpy_file(object):
    def __init__(self, file_name: str, path: str = '~/.tkpy2'):
        super(read_tkpy_file, self).__init__()
        self.file_name = file_name
        self.path = path
        self.db = PickleShareDB(path)

    def read(self, key=None):
        if key is not None:
            return self.db[self.file_name][key]
        return self.db[self.file_name]


class tkpy_file(object):
    def __init__(self, configs=None, path: str = '~/.tkpy2', file_name='config', init=False):
        self.db = PickleShareDB(path)
        self.file_name = file_name
        if file_name not in self.db or init:
            self.db[file_name] = configs

    def write(self, key=None, value=None, file_name=None):
        if file_name is None:
            file_name = self.file_name
        config = self.db[file_name]
        if key:
            config[key] = value
        else:
            config = value
        self.db[file_name] = config

    def read(self, key=None):
        if key:
            return self.db[key]
        else:
            return self.db

    def delete(self, key):
        del self.db[key]
