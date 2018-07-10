#!/bin/bash
#set -x
cd /root/data/yuqing/irain_tools_web;
pid=`ps -ef|grep irain_tools_web.py|grep -v grep|sed -n '1P'|awk '{print $2}'`

echo `date` "check alive of irain_tools_web..." $pid

if [ -z "$pid" ]; then
    echo `date` "process irain_tools_web not found, restart!"
    /usr/local/bin/python ./irain_tools_web.py >> ./server.log
fi
