#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
import socket
def send_msg(msg_text,msg_ip_port):#发送短信
    sk = socket.socket()
    sk.connect(msg_ip_port)
    sk.sendall(bytes(msg_text, 'utf8'))
    sk.close()