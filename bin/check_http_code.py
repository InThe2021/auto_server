#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
#20201215
import requests
from bin.log_module import logs
def http_status(appurl,app_name):  # 定义获取http请求的返回状态码函数
    code = 0
    try:
        html = requests.get(appurl)#请求url
        code = html.status_code#获取状态码
    except Exception as e:
        logs(e)
    finally:
        if code == 200:
            return code
        else:
            logs('[%s]当前http请求状态码为:%s' % (app_name, code))
            return code