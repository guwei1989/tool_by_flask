#!/usr/bin/env python
# coding: utf-8

import traceback
import MySQLdb
import sys
from helper import info, start, end, err, progress, get_mysql_addr


if __name__ == "__main__":

    progress(0)
    start()

    try:
        db_ip, db_port = get_mysql_addr()
        abnomal_num = sys.argv[1]
    except Exception as e:
        err("init param exception %s\n%s" % (e, traceback.format_exc()))

    try:
        conn = MySQLdb.connect(host=db_ip, port=db_port, user='root', passwd='iraindb10241GB', db='irain_park',
                               charset='utf8')
    except Exception as e:
        err("connect mysql exception %s\n%s" % (e, traceback.format_exc()))

    try:
        cursor = conn.cursor()
        cursor.execute("update project_conf set value = %s where name = 'abnormal_inout_display_num';" % abnomal_num)
        conn.commit()

        progress(100)
        info("success")

    except Exception as e:
        err("update abnormal inout num failuer %s\n%s" % (e, traceback.format_exc()))

    end()
