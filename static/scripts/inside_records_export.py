#!/usr/bin/env python
# coding:utf-8

import MySQLdb
import traceback
import xlwt
import os
import time
import sys
from helper import info, start, end, err, progress, get_mysql_addr


def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6

    style.font = font
    # style.borders = borders
    return style


if __name__ == "__main__":

    progress(0)
    start()

    try:
        progress(20)
        db_ip, db_port = get_mysql_addr()
        end_time = sys.argv[1]
    except Exception as e:
        err("init param exception %s\n%s" % (e, traceback.format_exc()))
        end()
        sys.exit(1)

    try:
        progress(40)
        conn = MySQLdb.connect(host=db_ip, port=db_port, user='root', passwd='iraindb10241GB', db='irain_park',
                               charset='utf8')
    except Exception as e:
        err("connect mysql exception %s\n%s" % (e, traceback.format_exc()))
        end()
        sys.exit(1)

    try:
        progress(60)
        cursor = conn.cursor()
        cursor.execute("select in_time, vpr_plate from park_inside "
                       "a left join park_in b on a.park_in_id = b.id where b.in_time <= '%s'" % end_time)

        result = cursor.fetchall()

        f = xlwt.Workbook()  # 创建工作簿
        sheet1 = f.add_sheet(u'场内记录', cell_overwrite_ok=True)  # 创建sheet
        row0 = [u'进场时间', u'车牌号']
        for i in range(0, len(row0)):
            sheet1.write(0, i, row0[i], set_style('Times New Roman', 220, True))
        for j in range(0, len(result)):
            sheet1.write(j + 1, 0, str(result[j][0]))
            sheet1.write(j + 1, 1, result[j][1])
        tool_run_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())

        if not os.path.exists("./excel"):
            os.mkdir("./excel")

        f_path = os.path.join("./excel", "inside_records_%s.xlsx" % tool_run_time)
        f.save(f_path)

        progress(80)
        info("FilePath:%s" % os.path.abspath(f_path))

        progress(100)
        info("success")

    except Exception as e:
        err("check terminal ip failuer %s\n%s" % (e, traceback.format_exc()))
        end()
        sys.exit(1)

    end()

