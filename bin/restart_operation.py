#!/usr/bin/env python3
# -*- coding:utf-8 -*-
__author__ = 'yzx'
#20201215
import subprocess
import time
from bin.log_module import logs
from bin.sql_operation import update_scan_err_time,update_status,cluster_status,online_status,update_last_startup_time
from bin.send_msg_module import send_msg
def restart(restart_cmd,app_name,home_path,appurl,host_ip,msg_ip_port): #重启函数
    jstack = subprocess.Popen(
        'jstack -F -l $(ps -ef| grep %s/tomcat | grep -v grep  | awk "{print $2}") > %s/jstack_$(date +"%s").log;' % (
        app_name, home_path, '%Y%m%d%H%M%S'),
        shell=True, stderr=subprocess.PIPE) #生产jstack到应用程序目录
    jstack_repl = str(jstack.stderr.read(), encoding='utf8')

    jmap = subprocess.Popen(
        "cd %s && sh jmap.sh $(ps -ef| grep %s/tomcat | grep -v grep  | awk '{print $2}');" % (home_path, app_name),
        shell=True, stdout=subprocess.PIPE)#调用jmap.sh生成jmap信息
    jmap_repl = str(jmap.stdout.read(), encoding='utf8')

    start_date = time.strftime(u'%d-%b-%Y %H:%M', time.localtime(time.time()))  # 定义开始时间 日-月(英文简写)-年 时：分：秒
    date_tmp = start_date.split(':')
    start_date_5 = date_tmp[0] + ':' + str(int(date_tmp[1])+5)#启动时间加5分钟，方便sed根据时间过滤出startup in日志
    counts = 0 #计数计时器（1个为2秒）
    restart = subprocess.Popen(restart_cmd, shell=True, stdout=subprocess.PIPE)  # 系统中重启应用的命令
    # os.system("python /home/www/scripts/sendMsg.py '''[通知]操作开始时间：%s\n当前域：zbfastcom首页\n动作：重启www前台'''" )
    restart_repl = str(restart.stdout.read(), encoding='utf8')
    logs(restart_repl)
    while True:  # 获取到startup后退出循环
        startup_logs = subprocess.Popen(u"sed -n '/%s/,/%s/p' %s/tomcat/logs/catalina.out | grep 'startup in' | tail -1" % (
        start_date, start_date_5, home_path), shell=True, stdout=subprocess.PIPE)#获取startup in日志
        startup_repl = str(startup_logs.stdout.read(),encoding='utf-8')  # 转str
        str_format_code = u'%{http_code}'  # Popen中不支持%{，这个直接转换为全字符传，以便调用不出错
        http_code = subprocess.Popen(u"curl -I -m 10 -o /dev/null -s -w %s %s" % (str_format_code, appurl), shell=True,stdout=subprocess.PIPE)  # 执行命令获取状态码
        http_code_rpel = str(http_code.stdout.read(),encoding='utf8')  # 状态码
        if len(startup_repl) > 10 and http_code_rpel == '200':  # 获取到startup日志（正常startup in 日志超过10个字符），并且状态码正常执行更新sql
            repl_list = startup_repl.split(' ')  # 分割日志
            start_time = repl_list[0] + ' ' + repl_list[1]  # startup in时间
            times = repl_list[-2]  # 耗时
            update_last_startup_time(start_time, times, http_code_rpel, host_ip, app_name)#更新重启时间
            update_status('1', host_ip, app_name)#更新状态，在线
            logs('%s Server Restart Successfully' % app_name)  # 日志记录重启
            break

        if counts>90: #程序初始化超时（3分钟内未获取到startup in日志）
            # #短信告警接口
            error_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
            msg_text = ('[告警]问题开始时间：%s\n触发器名称：%s重启失败(超时3分钟)\n主机：【%s-%s】 \n严重性：High'
                        % (error_date, app_name,app_name, host_ip))  # 格式化短信内容
            send_msg(msg_text,msg_ip_port) #socket发送内容到短信触发端
            dates = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 年-月-日 时：分：秒
            update_last_startup_time('Start_Error_'+dates, '0000', '0000', host_ip, app_name)#更新重启时间，耗时，状态码
            update_status('0', host_ip, app_name)  # 更新状态，离线
            logs('%s Restart %s Unsuccessfully' % (error_date, app_name))
            break
        time.sleep(2)
        counts += 1 #等待2秒计数加1