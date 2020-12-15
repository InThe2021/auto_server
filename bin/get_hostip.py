#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
#20201215
import socket
def hostip():#获取本地IP
    ip_list = socket.gethostbyname_ex(socket.gethostname())
    for ips in ip_list:
        if type(ips) == list and len(ips) != 0:
            IPlist = ips
    return IPlist[0]