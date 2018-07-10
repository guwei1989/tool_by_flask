# coding: utf-8
import datetime
import re
import sys

from log_helper import read_log_lines, LogFile
from v3_helper import run_sql
from helper import start, end, info


def in_sync(park_in_id, lines):
    """
    :return
        sync_succeed_time or None
    """
    re_pat = r"""\[recordid\]:(.*?),"""
    suc_pat = 'park_in_id=%s 记录已发送' % park_in_id
    pat = '参数[param]:[msgid]:4002'
    for l_no in range(len(lines)):
        line = lines[l_no]
        if pat in line:
            match = re.search(re_pat, line)
            if match:
                in_id = match.group(1)
                if in_id == park_in_id:
                    for i in range(100):
                        s_line = lines[l_no + i]
                        if suc_pat in s_line:
                            return datetime.datetime.strptime(line[:23], '%Y-%m-%d %H:%M:%S,%f')


def out_sync(park_in_id, lines):
    """
    :return
        sync_succeed_time or None
    """
    re_pat = r"""\[recordid\]:(.*?),"""
    suc_pat = 'park_in_id=%s 记录已发送' % park_in_id
    pat = '参数[param]:[msgid]:4036'
    for l_no in range(len(lines)):
        line = lines[l_no]
        if pat in line:
            match = re.search(re_pat, line)
            if match:
                in_id = match.group(1)
                if in_id == park_in_id:
                    for i in range(100):
                        s_line = lines[l_no + i]
                        if suc_pat in s_line:
                            return datetime.datetime.strptime(line[:23], '%Y-%m-%d %H:%M:%S,%f')


def main():
    park_in_id = sys.argv[1]

    sql = """select in_time, out_time from records_inout where park_in_id=%s""" % park_in_id
    in_time, out_time = run_sql(sql)[0].split('\t')
    in_date = datetime.datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S').date()
    out_date = datetime.datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S').date()

    in_st = in_sync(park_in_id, read_log_lines(LogFile.SYNC, in_date))
    out_st = out_sync(park_in_id, read_log_lines(LogFile.SYNC, out_date))

    d = {}
    if in_st:
        d[u'入场记录上报时间'] = in_st
    if out_st:
        d[u'出场记录上报时间'] = out_st

    info(d.__repr__())


if __name__ == '__main__':
    start()
    main()
    end()
