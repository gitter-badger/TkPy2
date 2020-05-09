# -*- coding: UTF-8 -*-
# 项目的名称: TkPy2
# 文件的名称: setup
# 创建时的用户的登录名: 用户
# 创建时的的日期: 2020/5/9-9:08
# 创建时的IDE名称: PyCharm

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TkPy2",  # Replace with your own username
    version="0.0.1",
    author="chenmy",
    author_email="chenmy10@outlook.com",
    description="A Python IDE",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.7',
)
