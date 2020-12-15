#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
#20201215
from bin.sql_operation import app_info,update_scan_err_time,update_status,cluster_status,online_status
from bin.check_http_code import http_status
from bin.log_module import logs
import threading
from bin.send_msg_module import send_msg
from bin.restart_operation import restart
import time
from config.config import msg_ip_port
from config.config import host_ip
def main():
    threadind_list = []  # 作为线程名列表，存储线程名
    for i in app_info():#循环列出每个应用对应的url,应用名，重启命令
        appurl = 'http://' + i[1] + ':' + str(i[2])#url
        # print(appurl)
        app_name = i[3]#应用名
        # print(app_name)
        restart_cmd = i[4]#重启命令
        # print(restart_cmd)
        home_path = i[4].split(' ')[1] + i[3]#应用程序主目录
        # print(home_path)

        code = http_status(appurl,app_name) #获取状态值
        if code == 200: #200为正常，不做操作
            # print(app_name+' 正常 状态码:'+str(code))
            pass
        else:#状态码异常
            dates = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
            update_scan_err_time(dates, host_ip, app_name) #更新扫描出错时间
            update_status('0', host_ip, app_name)#更新状态码未0，离线
            cluster_num = cluster_status(app_name)#获取当前项目总个数
            online_status_percent = online_status(app_name)#获取当前项目在线率

            if cluster_num > 1:#应用属于集群
                if online_status_percent >= 50:#在线率大于50%重启
                    cmd_threading = threading.Thread(target=restart, args=(restart_cmd,app_name,home_path,appurl,host_ip,msg_ip_port,))  # 多线程运行socket_client
                    threadind_list.append(cmd_threading)  # 线程名追加到threadind_list
                    cmd_threading.start()
                else:#在线率小于于50%触发告警短信
                    error_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
                    msg_text = ('[告警]问题开始时间：%s\n触发器名称：%s应用在线不足50%s\n主机：【%s-%s】 \n当前值：【%s】\n严重性：High'
                                % (error_date, app_name,'%',app_name, host_ip,str(online_status_percent)+'%'))  # 格式化短信内容
                    send_msg(msg_text,msg_ip_port) #socket发送内容到短信触发端
                    logs('[%s] 项目在线率不足50%s,当前值：%s'%(app_name,'%',str(online_status_percent)+'%'))
                    # time.sleep(60)
            else:#应用不属于集群直接重启
                cmd_threading = threading.Thread(target=restart, args=(
                restart_cmd,app_name,home_path,appurl,host_ip,msg_ip_port,))  # 多线程运行socket_client
                threadind_list.append(cmd_threading)  # 线程名追加到threadind_list
                cmd_threading.start()

    for i in threadind_list:  # 等待线程结束
        i.join()