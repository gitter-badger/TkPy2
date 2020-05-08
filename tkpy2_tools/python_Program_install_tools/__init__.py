# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: __init__.py
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/5-11:10
# 创建时的IDE名称: PyCharm

import requests
from pip._internal.main import main as PipMain
from bs4 import BeautifulSoup

url = 'https://pypi.org/simple/'

head = {
    'User-agent':
        'User-Agent:Mozilla/5.0 '
        '(Macintosh; U; Intel Mac OS X 10_6_8; en-us) '
        'AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}


def install(program_name: str, version):
    if PipMain(['install', program_name + f'=={version}', '--timeout', '1000']):
        return False
    return True


class InstallTools(object):
    def __init__(self):
        super(InstallTools, self).__init__()
        self.r = requests.get(url, headers=head, timeout=100)
        self.r.encoding = self.r.apparent_encoding
        self.soup = BeautifulSoup(self.r.text, 'html.parser')

    def __iter__(self):
        for url in self.soup.find_all('a'):
            yield url.get('href')

    def __call__(self, *args, **kwargs):
        return self.soup

    def get_names(self):
        for url in self.__iter__():
            yield url.replace('/simple', '').replace('/', '')

    def search(self, key):
        for name in self.get_names():
            if name.count(key):
                yield name


if __name__ == "__main__":
    Tools = InstallTools()
    with open('Test_python_program.txt', 'w') as f:
        for link in Tools.get_names():
            f.write(link + '\n')
