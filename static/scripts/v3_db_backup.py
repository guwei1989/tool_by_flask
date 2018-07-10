# coding: utf-8
import datetime

from helper import get_mysql_addr, start, info, err, end, progress, traceback, get_local_ip
import os

bak_dir = 'db_backup/'
if __name__ == '__main__':
    try:
        start()

        db_user = 'root'
        db_pwd = 'iraindb10241GB'

        progress(5, '开始获取数据库地址')
        db_ip, db_port = get_mysql_addr()
        progress(10, '获取成功')

        info('数据库 %s : %d' % (db_ip, db_port))

        if not os.path.exists(bak_dir):
            progress(25, '未找到 %s 目录，自动创建该目录' % bak_dir)
            os.makedirs(bak_dir)

        progress(40, '开始进行备份，过程中将使得数据库不可用，进出车将无法正常工作')

        f_path = os.path.join(bak_dir, '%s.sql' % str(datetime.datetime.now()).replace(' ', '_'))
        os.system('mysqldump -u%s -p%s -h%s irain_park > %s' % (db_user, db_pwd, db_ip, f_path))

        progress(95, '备份成功')

        progress(98, '备份文件地址:%s:%s' % (get_local_ip(), f_path))

        end()
    except Exception, e:
        err(e)
        err(traceback())
        end()