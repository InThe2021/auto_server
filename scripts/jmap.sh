#!/bin/bash
pid="$1"
if [[ -z "$pid" ]]
then
    echo -e '----------------请输入进程号!----------------'
    exit 0
fi

#dump堆到文件,format指定输出格式，live指明是活着的对象,file指定文件名
#jmap -dump:live,format=b,file=jmap_live_dump.log "$pid"
#sleep 1

#导出内存信息
echo -e '----------------收集dump信息----------------'
jmap -dump:format=b,file=jmap_all_dump.log "$pid"
sleep 1

#打印heap的概要信息，GC使用的算法，heap的配置及使用情况，可以用此来判断内存目前的使用情况以及垃圾回收情况
echo -e '----------------收集heap信息----------------'
jmap -heap "$pid" > jmap_heap.log

#打印等待回收的对象信息
echo -e '----------------收集finalizerinfo信息----------------'
jmap -finalizerinfo "$pid" > jmap_finalizerinfo.log

#打印堆的对象统计，包括对象数、内存大小等等
echo -e '----------------收集histo信息----------------'
#jmap -histo:live "$pid" > jmap_histo.log
jmap -histo "$pid" > jmap_histo.log