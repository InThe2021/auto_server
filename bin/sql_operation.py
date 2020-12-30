#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
#20201215
from bin.database_conn import mysql_conn
from bin.log_module import logs
from config.config import host_ip
def app_info():#获取app的hostname,ip,port,application,cmds信息
    connects = mysql_conn()
    with connects.cursor() as cursor:
        cursor = connects.cursor()
        cursor.execute('select hostname,ip,port,application,cmds from app_info where ip="%s" and open_status=1;' % host_ip)  # 查询数据库项目列表
        connects.commit()
        info = cursor.fetchall()
        if len(info) < 1:
            print('当前服务器未在数据库配置应用参数信息！')
            logs('当前服务器未在数据库配置应用参数信息！')
        connects.close()
        return info

def cluster_status(app_name):#查询app_name是否集群
    connects = mysql_conn()
    with connects.cursor() as cursor:
        cursor = connects.cursor()
        cursor.execute('select count(1) from app_info where application="%s" and open_status=1;' % app_name)  # 查询数据库项目列表
        connects.commit()
        info_num = cursor.fetchone()
        connects.close()
        return info_num[0]

def online_status(app_name):#查询app_name在线数率
    connects = mysql_conn()
    with connects.cursor() as cursor:
        cursor = connects.cursor()
        cursor.execute('select count(1) from app_info where application="%s" and status=1 and open_status=1;' % app_name)  # 查询数据库项目列表
        connects.commit()
        online_num = cursor.fetchone()

        cursor.execute('select count(1) from app_info where application="%s" and status=0 and open_status=1;' % app_name)  # 查询数据库项目列表
        connects.commit()
        offline_num = cursor.fetchone()

        cursor.execute('select count(1) from app_info where application="%s" and open_status=1;' % app_name)  # 查询数据库项目列表
        connects.commit()
        count_num = cursor.fetchone()
        online_percent = (online_num[0]/count_num[0])*100
        connects.close()
        return round(online_percent,2)

def update_status(status,host_ip,app_name): #更新状态
    connects = mysql_conn()
    with connects.cursor() as cursor:
        cursor.execute("update app_info set status=%s where ip='%s' and application='%s' and open_status=1;" % (status,host_ip,app_name))  # 更新状态
        connects.commit()
        connects.close()

def update_scan_err_time(dates,host_ip,app_name): #更新last_scan_err_time
    connects = mysql_conn()
    with connects.cursor() as cursor:
        cursor.execute("update app_info set before_scan_err_time=last_scan_err_time where ip='%s' and application='%s' and open_status=1;" % (host_ip, app_name))  # 更新before_scan_time
        connects.commit()
        cursor.execute("update app_info set last_scan_err_time='%s' where ip='%s' and application='%s' and open_status=1;" % (dates,host_ip,app_name))  # 更新更新last_scan_time状态
        connects.commit()
        connects.close()

def update_last_startup_time(start_time,times,http_code,host_ip,app_name): #更新last_startup_time
    connects = mysql_conn()
    with connects.cursor() as cursor:
        cursor.execute("update app_info set before_startup_time = last_startup_time where ip='%s' and application='%s' and open_status=1;" % (host_ip, app_name))  # before_startup_time
        connects.commit()
        cursor.execute("update app_info set last_startup_time = '%s',startup_times = %s,http_code = %s where ip='%s' and application='%s' and open_status=1;" % (start_time,times,http_code,host_ip,app_name))  # 更新更新start_time,times,http_code
        connects.commit()
        connects.close()
