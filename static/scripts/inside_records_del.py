#!/usr/bin/env python
# coding: utf-8

import MySQLdb
import traceback
import time
import sys
import os
from helper import info, start, end, err, progress, get_mysql_addr, get_local_ip

if __name__ == "__main__":

    progress(0)
    start()

    try:
        db_ip, db_port = get_mysql_addr()
        end_time = sys.argv[1]
    except Exception as e:
        err("init param exception %s\n%s" % (e, traceback.format_exc()))

    try:
        if not os.path.exists("./db_dump"):
            os.mkdir("./db_dump")
        tool_run_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        f_path = os.path.join("./db_dump", "irain_parkin_inside_'%s'.sql" % tool_run_time)
        os.system("mysqldump - h'%s' - uroot - piraindb10241GB irain_park park_in park_inside "
                         "> %s" % (db_ip, f_path))

        info("dump park_inside success: %s: %s" % (get_local_ip(), f_path))

    except Exception as e:
        err("dump mysql park_inside failed")

    try:
        conn = MySQLdb.connect(host=db_ip, port=db_port, user='root', passwd='iraindb10241GB', db='irain_park',
                               charset='utf8')
        cursor = conn.cursor()
        cursor.execute("delete from park_inside where park_in_id in "
                       "(select id from park_in where in_time <= '%s')" % end_time)
        cursor.execute("delete from park_in where in_time <= '%s'" % end_time)
        conn.commit()

        progress(100)
        info("success")

    except Exception as e:
        err("connect mysql exception %s\n%s" % (e, traceback.format_exc()))
    end()
