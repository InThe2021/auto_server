#!/bin/bash
ps -ef | grep 'auto_restart.py' | grep -v grep | awk {'print $2'} | xargs kill -9
#sadsadsa