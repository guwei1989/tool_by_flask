#!/usr/bin/env python
# coding: utf-8

import traceback
import MySQLdb
import paramiko
from helper import info, start, end, err, progress, get_mysql_addr
import threading

if __name__ == "__main__":

    progress(0)
    start()

    try:
        db_ip, db_port = get_mysql_addr()
    except Exception as e:
        err("init param exception %s\n%s" % (e, traceback.format_exc()))

    try:
        conn = MySQLdb.connect(host=db_ip, port=db_port, user='root', passwd='iraindb10241GB', db='irain_park',
                               charset='utf8')
    except Exception as e:
        err("connect mysql exception %s\n%s" % (e, traceback.format_exc()))

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ip FROM depot_terminal;")
        ip_list = cursor.fetchall()
    except Exception as e:
        err("check terminal ip failuer %s\n%s" % (e, traceback.format_exc()))

    try:
        threads = []

        def work(addr):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(addr[0], port=22, username='root', password='iraindev10241GB', timeout=60)
            _, stdout, _ = ssh.exec_command("cd /home/park;sh restart.sh")
            stdout.read()

        for ip in ip_list:
            t = threading.Thread(target=work, args=(ip,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        progress(100)
        info("success")

    except Exception as e:
        err("restart failuer: %s\n%s" % (e, traceback.format_exc()))

    end()
