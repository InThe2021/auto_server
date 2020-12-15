#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
from bin.get_hostip import hostip
mysqls={
    "dbip": "172.16.100.157",
     "port": "3306",
    "username": "dbinfo",
    "pwd": "dbinfo@123456",
    "dbname": "dbinfo"
  }
host_ip = hostip()
# host_ip = '172.16.100.157'
msg_ip_port = ('172.16.100.157',8888)
