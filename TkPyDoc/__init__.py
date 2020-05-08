# -*- coding: utf-8 -*-
"""
TkPy doc
TkPy的官方文档服务器
==========

"""
from importlib import import_module

from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import uvicorn
import os
import webbrowser
import sys
try:
    from . import docs
except:
    import docs
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
@app.get('/TkPy/index')
@app.get('/TkPy/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, 'url': '/TkPy/help/', 'docs': docs.docs})


@app.get('/TkPy/help/')
def get_help(request: Request, name: str = ''):
    if name == '':
        return templates.TemplateResponse('help_index.html', {'request': request})
    if name[0:5] == 'help_':
        return templates.TemplateResponse('index.html', {'request': request, 'url':
            ('/TkPy/help/?name=render_' + name),
                                                         'docs': docs.docs})
    elif name[0:7] == 'render_':
        try:
            return templates.TemplateResponse(name.replace('render_', ''), {'request': request})
        except:
            return templates.TemplateResponse('404.html', {'request': request})
    else:
        return index(request)


@app.get('/TkPy/sys/path/')
def path(request: Request):
    return templates.TemplateResponse('sys.html', {'request': request, 'name': sys.path})


@app.get('/TkPy/help/html/python_doc/')
def python_help(request: Request, name: str = ''):
    if name:
        try:
            doc = import_module(name)
        except:
            return f'未找到此包,检查是否输入错误。 (输入的包名:{repr(name)})'
        try:
            path = doc.__file__
        except:
            path = ""
        return templates.TemplateResponse('python_doc.html',
                                          {'request': request,
                                           'doc': doc.__doc__ if doc.__doc__ else f'包{name}无文档',
                                           'title_name': name,
                                           'file_path': path if not path else path.replace('\\', '/')})


@app.get('/TkPy/open/file/')
def open(request: Request, path: str = ''):
    webbrowser.open("/".join(path.replace('\\', '/').split('/')[0:-1]))
    return templates.TemplateResponse('close.html', {'request': request})


@app.get('/TkPy/doc/python')
def python_help(request: Request, name: str = ''):
    try:
        text = import_module(name)
        file = text.__file__.replace('\\', '/')
        path = "/".join(file.split('/')[0:-1])
        doc = text.__doc__
    except:
        return f'404   你找的包不存在。输入的包名: {name}'
    else:
        return templates.TemplateResponse('python_doc.html',
                                          {
                                              'request': request,
                                              'title_name': name,
                                              'doc': doc if doc else '本包没有文档',
                                              'file_path': path if path else '',
                                              'file': file
                                          }
                                          )


def runserver(**kwargs):
    uvicorn.run(app, **kwargs)


if __name__ == "__main__":
    runserver(host="127.0.0.1", port=8087, debug=True, workers=True)
