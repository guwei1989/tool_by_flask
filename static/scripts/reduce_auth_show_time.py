# coding:utf-8

import MySQLdb
import traceback
from helper import info, start, end, err, progress, get_mysql_addr


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
        cursor.execute("update new_auth_group set eday = DATE_SUB(eday, INTERVAL 1 DAY)"
                       " where time_range = '00:00:00,23:59:59' and week='1,2,3,4,5,6,7' and auth_no"
                       " in (select auth_no from new_auth_charge where DATE(eday) != DATE(validity_end))")

        cursor.execute("update new_auth_charge set eday = DATE_SUB(eday, INTERVAL 1 DAY)"
                       " where auth_no in (select auth_no from new_auth_group where "
                       "time_range = '00:00:00,23:59:59' and week='1,2,3,4,5,6,7')"
                       " and DATE(eday) != DATE(validity_end)")
        conn.commit()

        progress(100)
        info("success")

    except Exception as e:
        err("reduce auth show time failuer %s\n%s" % (e, traceback.format_exc()))

    end()
