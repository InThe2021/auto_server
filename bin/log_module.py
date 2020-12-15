#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
import logging
def logs(log_text):#日志输出
    logger = logging.getLogger('yzx')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %R:%S')
    if not logger.handlers:  # handlers属性，控制重复输出.因为logger的name被固定，所以当你第一次为logger对象添加FileHandler对象之后，如果没有移除上一次的FileHandler对象，第二次logger对象就会再次获得相同的FileHandler对象，即拥有两个FileHandler对象，最终造成打印两次，同样，如果此时没有立即移除上一次的FileHandler对象，第三次logger对象就会再次获得相同的FileHandler对象，即拥有三个FileHandler象，最终打印3次........
        file_out = logging.FileHandler('logs/auto_restart.log')  # 用于输出至文件
        # logger.setLevel(logging.INFO)
        file_out.setFormatter(formatter)
        logger.addHandler(file_out)  # logger绑定处理对象
    logger.info(log_text)