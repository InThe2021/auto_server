#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# yzx20200819



import requests
import psutil
#import dns.resolver
#import os
#import http.client
import time
import threading
import json
import logging
import subprocess
import pymysql
import socket
import sys
import importlib
importlib.reload(sys)
sys.setdefaultencoding('utf-8')
__author__ = 'yzx'


def hostip():#获取本地IP
    ip_list = socket.gethostbyname_ex(socket.gethostname())
    for ips in ip_list:
        if type(ips) == list and len(ips) != 0:
            IPlist = ips
    return IPlist[0]


def logs(log_text):#日志输出
    logger = logging.getLogger('yzx')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %R:%S')
    if not logger.handlers:  # handlers属性，控制重复输出.因为logger的name被固定，所以当你第一次为logger对象添加FileHandler对象之后，如果没有移除上一次的FileHandler对象，第二次logger对象就会再次获得相同的FileHandler对象，即拥有两个FileHandler对象，最终造成打印两次，同样，如果此时没有立即移除上一次的FileHandler对象，第三次logger对象就会再次获得相同的FileHandler对象，即拥有三个FileHandler象，最终打印3次........
        file_out = logging.FileHandler('system_auto_restart.log')  # 用于输出至文件
        # logger.setLevel(logging.INFO)
        file_out.setFormatter(formatter)
        logger.addHandler(file_out)  # logger绑定处理对象
    logger.info(log_text)


def mysql_conn(dbip,username,pws,dbname):#定义mysql_conn函数，ip,username,pws为形参
    try:
        connects= pymysql.connect(host=dbip, port=3306, user=username, passwd=pws,db=dbname)
    except Exception:#异常报错返回
        # print("IP:%s Could not connect to MySQL server."%ip)
        logs("IP:%s Could not connect to MySQL server."%dbip)
    return connects


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



def app_info():#获取app的hostname,ip,port,application,cmds信息
    connects = mysql_conn(dbip, username, pws, dbname)
    with connects.cursor() as cursor:
        cursor = connects.cursor()
        cursor.execute('select hostname,ip,port,application,cmds,is_restart_now from app_info where ip="%s" and open_status=1;' % host_ip)  # 查询数据库项目列表
        connects.commit()
        info = cursor.fetchall()
        if len(info) < 1:
            print('当前服务器未在数据库配置应用参数信息！')
            logs('当前服务器未在数据库配置应用参数信息！')
        connects.close()
        return info

def cluster_status(app_name):#查询app_name是否集群
    connects = mysql_conn(dbip, username, pws, dbname)
    with connects.cursor() as cursor:
        cursor = connects.cursor()
        cursor.execute('select count(1) from app_info where application="%s" and open_status=1;' % app_name)  # 查询数据库项目列表
        connects.commit()
        info_num = cursor.fetchone()
        connects.close()
        return info_num[0]

def online_status(app_name):#查询app_name在线数率
    connects = mysql_conn(dbip, username, pws, dbname)
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
    connects = mysql_conn(dbip, username, pws, dbname)
    with connects.cursor() as cursor:
        cursor.execute("update app_info set status=%s where ip='%s' and application='%s' and open_status=1;" % (status,host_ip,app_name))  # 更新状态
        connects.commit()
        connects.close()

def logs_to_db(host_ip,app_name): #
    dates = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    connects = mysql_conn(dbip, username, pws, dbname)
    with connects.cursor() as cursor:
        cursor.execute("INSERT INTO logs_info (username,operation,date) VALUES('system','%s','%s');" % ('[Auto-Restart]:'+app_name+'_'+host_ip,dates))
        connects.commit()
        connects.close()

def update_scan_err_time(dates,host_ip,app_name): #更新last_scan_err_time
    connects = mysql_conn(dbip, username, pws, dbname)
    with connects.cursor() as cursor:
        cursor.execute("update app_info set before_scan_err_time=last_scan_err_time where ip='%s' and application='%s' and open_status=1;" % (host_ip, app_name))  # 更新before_scan_time
        connects.commit()
        cursor.execute("update app_info set last_scan_err_time='%s' where ip='%s' and application='%s' and open_status=1;" % (dates,host_ip,app_name))  # 更新更新last_scan_time状态
        connects.commit()
        connects.close()

def update_last_startup_time(start_time,times,http_code,host_ip,app_name): #更新last_startup_time
    connects = mysql_conn(dbip, username, pws, dbname)
    with connects.cursor() as cursor:
        cursor.execute("update app_info set before_startup_time = last_startup_time where ip='%s' and application='%s' and open_status=1;" % (host_ip, app_name))  # before_startup_time
        connects.commit()
        cursor.execute("update app_info set last_startup_time = '%s',startup_times = %s,http_code = %s where ip='%s' and application='%s' and open_status=1;" % (start_time,times,http_code,host_ip,app_name))  # 更新更新start_time,times,http_code
        connects.commit()
        connects.close()

def send_msg(msg_text,msg_ip_port):#发送短信
    sk = socket.socket()
    sk.connect(msg_ip_port)
    sk.sendall(str(msg_text).encode('utf8'))
    sk.close()

def restart(restart_cmd,app_name,home_path,appurl,host_ip,msg_ip_port): #重启函数
    #jstack = subprocess.Popen(u'jstack -F -l $(ps -ef| grep %s/tomcat | grep -v grep  | awk "{print $2}") > %s/jstack_$(date +"%s").log;' % (app_name, home_path, u'%Y%m%d%H%M%S'),shell=True, stderr=subprocess.PIPE) #生产jstack到应用程序目录
    #jstack_repl = unicode(jstack.stderr.read(), encoding=u'utf8')

    #jmap = subprocess.Popen(u"cd %s && sh py_jmap.sh $(ps -ef| grep %s/tomcat | grep -v grep  | awk '{print $2}');" % (home_path, app_name),shell=True, stdout=subprocess.PIPE)#调用jmap.sh生成jmap信息
    #jmap_repl = unicode(jmap.stdout.read(), encoding=u'utf8')

    start_date = time.strftime('%d-%b-%Y %H:%M', time.localtime(time.time()))  # 定义开始时间 日-月(英文简写)-年 时：分：秒
    date_tmp = start_date.split(':')
    start_date_5 = date_tmp[0] + ':' + str(int(date_tmp[1])+5)#启动时间加5分钟，方便sed根据时间过滤出startup in日志
    counts = 0 #计数计时器（1个为2秒）
    restart = subprocess.Popen(restart_cmd, shell=True, stdout=subprocess.PIPE)  # 系统中重启应用的命令
    # os.system("python /home/www/scripts/sendMsg.py '''[通知]操作开始时间：%s\n当前域：zbfastcom首页\n动作：重启www前台'''" )
    restart_repl = str(restart.stdout.read(), encoding='utf8')
    logs(restart_repl)
    while True:  # 获取到startup后退出循环
        logs('auto_restart-循环检验[%s]重启结果:%s次' % (app_name, counts))
        startup_logs = subprocess.Popen("sed -n '/%s/,/%s/p' %s/tomcat/logs/catalina.out | grep 'startup in' | tail -1" % (
        start_date, start_date_5, home_path), shell=True, stdout=subprocess.PIPE)#获取startup in日志
        startup_repl = str(startup_logs.stdout.read(),encoding='utf-8')  # 转str
        str_format_code = '%{http_code}'  # Popen中不支持%{，这个直接转换为全字符传，以便调用不出错
        http_code = subprocess.Popen("curl -I -m 1 -o /dev/null -s -w %s %s" % (str_format_code, appurl), shell=True,stdout=subprocess.PIPE)  # 执行命令获取状态码
        http_code_rpel = str(http_code.stdout.read(),encoding='utf8')  # 状态码
        if len(startup_repl) > 10 and http_code_rpel == '200':  # 获取到startup日志（正常startup in 日志超过10个字符），并且状态码正常执行更新sql
            repl_list = startup_repl.split(' ')  # 分割日志
            start_time = repl_list[0] + ' ' + repl_list[1]  # startup in时间
            times = repl_list[-2]  # 耗时
            update_last_startup_time(start_time, times, http_code_rpel, host_ip, app_name)#更新重启时间
            update_status('1', host_ip, app_name)#更新状态，在线
            logs('%s Server Restart Successfully' % app_name)  # 日志记录重启
            break
        elif counts>5: #循环5次退出，发送失败信息
            # #短信告警接口
            logs('auto_restart-[%s]重启超时检测次数:%s' % (app_name, counts))
            error_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
            msg_text = ('[Devops告警]问题开始时间：%s\n触发器名称：%s重启失败(初始化超时2分钟)\n主机：【%s-%s】 \n严重性：High'% (error_date, app_name,app_name, host_ip))  # 格式化短信内容
            send_msg(msg_text,msg_ip_port) #socket发送内容到短信触发端
            update_last_startup_time('Start_Error_'+dates, '0000', '0000', host_ip, app_name)#更新重启时间，耗时，状态码
            update_status('0', host_ip, app_name)  # 更新状态，离线
            logs('%s Restart %s Unsuccessfully' % (error_date, app_name))
            break
        else:
            time.sleep(20)
            counts += 1 #等待5秒计数加1



def main():
    threadind_list = []  # 作为线程名列表，存储线程名
    for i in app_info():#循环列出每个应用对应的url,应用名，重启命令
        cpu_p = psutil.cpu_percent(1)  # cpu使用率

        appurl = 'http://' + i[1] + ':' + str(i[2])#url
        # print(appurl)
        app_name = i[3]#应用名
        # print(app_name)
        restart_cmd = i[4]#重启命令
        # print(restart_cmd)
        home_path = i[4].split(' ')[1] + i[3]#应用程序主目录
        is_restart_now = i[5]
        code = http_status(appurl,app_name) #获取状态值
        #logs(u'cpu使用率：%s  状态码：%s' % (cpu_p,code))
        if is_restart_now == 0 :
            if code == 200 and cpu_p < 95: #200为正常，不做操作
                # print(app_name+' 正常 状态码:'+str(code))
                pass
            else:#状态码异常
                logs('cpu使用率：%s  状态码：%s' % (cpu_p,code))
                logs_to_db(host_ip, app_name)
                error_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
                msg_text = ('[DevOps-Scan]扫描时间：%s\n触发器名称：%s_Auto_Restart\n主机：【%s-%s】 \nCPU使用率：【%s】 \n状态码：【%s】\n严重性：High' % (error_date, app_name, app_name, host_ip, str(cpu_p) + '%',code))  # 格式化短信内容
                #send_msg(msg_text, msg_ip_port)  # socket发送内容到短信触发端
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
                        msg_text = ('[DevOps-告警]问题开始时间：%s\n触发器名称：%s应用在线不足50%s\n主机：【%s-%s】 \n当前值：【%s】\n严重性：High'% (error_date, app_name,'%',app_name, host_ip,str(online_status_percent)+'%'))  # 格式化短信内容
                        send_msg(msg_text,msg_ip_port) #socket发送内容到短信触发端
                        logs('[%s] 项目在线率不足50%s,当前值：%s'%(app_name,'%',str(online_status_percent)+'%'))
                        # time.sleep(60)
                else:#应用不属于集群直接重启
                    cmd_threading = threading.Thread(target=restart, args=(
                    restart_cmd,app_name,home_path,appurl,host_ip,msg_ip_port,))  # 多线程运行socket_client
                    threadind_list.append(cmd_threading)  # 线程名追加到threadind_list
                    cmd_threading.start()
        else:
            logs('[%s-%s]:DevOps正在重启应用，本次扫描跳过！'%(app_name,host_ip))

    for i in threadind_list:  # 等待线程结束
        i.join()
if __name__ == "__main__":
    host_ip = hostip()
    # host_ip = '172.16.100.157'
    dbip = '10.0.214.222'
    username ='zabbix'
    pws = 'zabbix@2017'
    dbname = 'zabbix'
    msg_ip_port = ('10.0.214.222',10057)
    while True:
        try:
            dates = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
            main()
            time.sleep(60)#等待一分钟开始下一次循环
        except Exception as e:
            logs(e)