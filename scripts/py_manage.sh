#!/bin/bash
rootPath="$(pwd)"
catalina="tomcat/bin/catalina.sh"
logFile="tomcat/logs/catalina.out"
#JAVA_OPTS="-server -Xms2048m -Xmx2048m -Xmn1024m -Djava.awt.headless=true -XX:MaxPermSize=256m -XX:PermSize=128m"
#JAVA_OPTS="$JAVA_OPTS -server -Xms4096m -Xmx8191m -Xmn1024m -Djava.awt.headless=true -XX:MetaspaceSize=512m -Dcom.sun.management.jmxremote"
#export JAVA_OPTS

#根据唯一标识取项目pid
getPid()
{
    echo "$(ps -ef|grep /$1/tomcat|grep -v -E "tail|grep"|awk '{print $2}')"
}
#根据唯一标识取项目状态
getStatus()
{
    pid="$(getPid $1)"
    path="$(ls -lh /proc/$pid|grep cwd|awk '{print $NF}')"
    echo -e "[[ $pid ]] $path"
}
#关闭项目tomcat，确保最后使用kill -9 杀死进程
stopPro()
{
    projectName="$1"
    pid=$(getPid "$projectName")
    #如果pid不为空，则执行关闭操作
    if [[ -n "$pid" ]]
    then
        echo -e "...... old pid is:[[ $pid ]] ......"
        nohup "$catalina" stop >/dev/null 2>&1 &
        echo -e "...... sleep 5s ......"
        sleep 5
        pid=$(getPid "$projectName")
        num=0
        while [[ -n "$pid" ]]
        do
            let num=num+1
            echo -e "...... kill $pid $num ......"
            kill "$pid" >/dev/null 2>&1
            echo -e "...... sleep 3s ......"
            sleep 3
            pid=$(getPid "$projectName")
            if [[ "$num" -ge 10 && -n "$pid" ]]
            then
                echo -e "...... kill -9 $pid ......"
                kill -9 "$pid"
                sleep 3
                echo -e "...... sleep 3s ......"
                break
            fi
        done
        pid=$(getPid "$projectName")
        if [[ -n "$pid" ]]
        then
            #如果pid不为空，表示关闭异常，返回状态1
            return 1
        else
            #如果pid为空，表示关闭正常，返回状态0
            return 0
        fi
    else
        #如果pid为空，则提示未运行,返回状态0
        echo -e "...... $projectName is no running ......"
        return 0
    fi
}

startPro()
{
    projectName="$1"
    cd "$rootPath/$projectName"
    pid=$(getPid "$projectName")
    if [[ -z "$pid" ]]
    then
        echo -e "...... now start $projectName ......"
        nohup "$catalina" start >/dev/null 2>&1 &
        echo -e "...... sleep 3s ......"
        sleep 3
        pid=$(getPid "$projectName")
        if [[ -n "$pid" ]]
        then
            echo -e "...... new pid is:[[ $pid ]] ......"
            return 0
        else
            return 1
        fi
    else
        echo -e "...... $projectName is running as:[[ $pid ]] ......\n"
        return 1
    fi
}

restartPro()
{
    projectName="$1"
    stopPro "$projectName"
    if [[ "$?" -eq 0 ]]
    then
        startPro "$projectName"
        if [[ "$?" -eq 0 ]]
        then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

action="$1"
projectName=$(echo "$2"|tr -d '/')

case "$action" in
stop)
    stopPro "$projectName"
    if [[ "$?" -eq 0 ]]
    then
        echo -e "...... stop $projectName successfully ......\n"
    else
        echo -e "...... stop $projectName unsuccessfully ......\n"
    fi
    ;;
start)
    startPro "$projectName"
    if [[ "$?" -eq 0 ]]
    then
        echo -e "...... start $projectName successfully ......\n"
    else
        echo -e "...... start $projectName unsuccessfully ......\n"
    fi
    ;;
restart)
    restartPro "$projectName"
    if [[ "$?" -eq 0 ]]
    then
        echo -e "...... restart $projectName successfully ......\n"
        #cd "$rootPath" && tail -f "$projectName/$logFile"
    else
        echo -e "...... restart $projectName unsuccessfully ......\n"
    fi
    ;;
status)
    getStatus "$projectName"
    ;;
*)
    echo -e "pls usage:$0 { status | start | stop | restart } { projectDirName }" && exit 0
    ;;
esac