# coding:utf-8
from helper import start, end, get_mysql_addr, info
import os

if __name__ == '__main__':
    start()
    db_ip, _ = get_mysql_addr()
    _, out = os.popen2(
        """mysql -uroot -piraindb10241GB -h%s -sN irain_park -e 'update project_conf set value = "http://img.parkingwang.com/picupload/" where id=3'""" % db_ip)
    info(out.read())

    _, out = os.popen2(
        """mysql -uroot -piraindb10241GB -h%s -sN irain_park -e 'select value from project_conf where id=3'""" % db_ip)
    info(out.read())

    end()