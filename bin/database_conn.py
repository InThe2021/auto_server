#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
#20201215
import pymysql
from config.config import mysqls
from bin.log_module import logs
def mysql_conn():#定义mysql_conn函数，ip,username,pws为形参
    try:
        connects= pymysql.connect(host=mysqls['dbip'], port=3306, user=mysqls['username'], passwd=mysqls['pwd'],db=mysqls['dbname'])
    except Exception:#异常报错返回
        # print("IP:%s Could not connect to MySQL server."%ip)
        logs("IP:%s Could not connect to MySQL server."%mysqls['dbip'])
    return connects