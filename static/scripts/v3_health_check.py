# -*- coding:utf-8 -*-
import re
import os
import traceback
import MySQLdb
import ConfigParser
from helper import info, err, start, end, progress, get_all_terminals_addr, get_mysql_addr, get_local_ip, debug, \
    set_prefix

"""
todo:
    rinetd check
"""


def check_disk_space():
    r_handle = os.popen('df -hl')
    result = r_handle.read()
    r_handle.close()
    # debug(result)

    patt = re.compile('.*?/dev/root.*?(\d+)%.*?', re.I)
    temp = patt.findall(result)
    if temp:
        value = int(temp[0])
        if value > 90:
            err(u'磁盘占用：%i%%, 存储满，请手动清理。' % value)
        else:
            info(u'磁盘占用：%i%%, 正常。' % value)
    else:
        err(u'磁盘空间检查失败，无法获取到磁盘占用')


def check_vpr_config(db_cursor, local_ip, db_ip):
    cp = ConfigParser.ConfigParser()
    cp.read('/home/park/config/config.cfg')

    vpr_in_cfg = cp.get('vpr', 'in_ip').strip()
    vpr_in_cfg2 = cp.get('vpr', 'in_ip2').strip()
    vpr_out_cfg = cp.get('vpr', 'out_ip').strip()
    vpr_out_cfg2 = cp.get('vpr', 'out_ip2').strip()
    vpr_type = cp.get('vpr', 'vpr_type').strip()
    db_server = cp.get('mysql', 'host').strip()

    db_cursor.execute(
        'select depot_site.vpr_ip, depot_site.vpr_1_ip from depot_site,depot_terminal where depot_site.terminal_id = '
        'depot_terminal.id and depot_terminal.ip = "%s" and depot_site.is_in_site = 1; '
        % local_ip)

    value = db_cursor.fetchall()
    if value:
        vpr_in_db = value[0][0].strip()
        vpr_in_db2 = value[0][1].strip()
    else:
        vpr_in_db = ''
        vpr_in_db2 = ''

    db_cursor.execute(
        'select depot_site.vpr_ip, depot_site.vpr_1_ip from depot_site,depot_terminal where '
        'depot_site.terminal_id = depot_terminal.id and depot_terminal.ip = "%s" and depot_site.is_in_site = 0; '
        % local_ip)
    value = db_cursor.fetchall()

    if value:
        vpr_out_db = value[0][0].strip()
        vpr_out_db2 = value[0][1].strip()
    else:
        vpr_out_db = ''
        vpr_out_db2 = ''

    flag = 0
    if vpr_in_cfg != vpr_in_db:
        err(u'进口主相机ip配置不一致，页面配置值：%s，config文件值：%s，请同步页面配置值到config.cfg文件。' %
            (vpr_in_db, vpr_in_cfg))
        flag = 1
    if vpr_in_cfg2 != vpr_in_db2:
        err(u'进口辅相机ip配置不一致，页面配置值：%s，config文件值：%s，请同步页面配置值到config.cfg文件。' %
            (vpr_in_db2, vpr_in_cfg2))
        flag = 1
    if vpr_out_cfg != vpr_out_db:
        err(u'出口主相机ip配置不一致，页面配置值：%s，config文件值：%s，请同步页面配置值到config.cfg文件。' %
            (vpr_out_db, vpr_out_cfg))
        flag = 1
    if vpr_out_cfg2 != vpr_out_db2:
        err(u'出口辅相机ip配置不一致，页面配置值：%s，config文件值：%s，请同步页面配置值到config.cfg文件。' %
            (vpr_out_db2, vpr_out_cfg2))
        flag = 1

    if not flag:
        info(u'V3 相机配置一致性检查结果:正常。')


def check_processes():
    r_handle = os.popen("ps -ef|grep python")
    result = r_handle.read()
    r_handle.close()
    err_proc_list = []
    # key_list = ['mails', 'code', 'codes', 'exchange']
    key_list = [
        'irain_park', 'irain_web', 'irain_websocket', 'irain_sync',
        'irain_celery'
    ]
    for item in key_list:
        if result.find(item) == -1:
            err_proc_list.append(item)

    r_handle = os.popen("ps -ef|grep vpr_ser")
    result = r_handle.read()
    r_handle.close()

    if result.find('vpr_server') == -1:
        err_proc_list.append('vpr_server')
    if not err_proc_list:
        info(u'关键进程检查结果：正常。')
    else:
        err(u'关键进程检查结果：异常，缺少以下关键进程：%s。' % err_proc_list)


def check_boa_and_serial(db_cursor, local_ip):
    db_cursor.execute(
        "select id from depot_terminal where ip = '%s'" % local_ip)
    terminal_id = db_cursor.fetchall()[0][0]
    db_cursor.execute(
        'select conf_value from depot_terminal_detail where terminal_id = %d and conf_type = "img_server_port";'
        % terminal_id)
    boa_port_conf = ''
    value = db_cursor.fetchall()
    if value:
        boa_port_conf = value[0][0]

    with open('/etc/boa/boa.conf', 'rb') as r_handle:
        text = r_handle.read()

    patt = re.compile('.*?Port\s+(\d+).*?', re.I)
    temp = patt.findall(text)
    value = ''
    if temp:
        value = temp[0]

    if boa_port_conf == value:
        info(u'boa 配置检查结果, 正常。')
    else:
        err(u'boa 配置检查结果：错误，系统配置值:%s, boa.conf配置值:%s' % (boa_port_conf, value))

    serial_trans_flag = '0'
    db_cursor.execute(
        'select conf_value from depot_terminal_detail where terminal_id = %d and conf_type = '
        '"serial_trans_camera_flag"; ' % terminal_id)
    boa_port_conf = ''
    value = db_cursor.fetchall()
    if value:
        serial_trans_flag = value[0][0]

    if serial_trans_flag == '1':
        info(u'车场透传标志校验结果：正常。')
    else:
        err(u'车场透传标志校验结果：未开启，请确认此终端是否为非透传模式。')


def check_paramiko():
    r_handle = os.popen('python -c "import paramiko;"')
    result = r_handle.read()
    r_handle.close()
    if result.find('No module named') == -1:
        info(u'paramiko包检查结果：正常。')
    else:
        err(u'paramiko包检查结果：异常，请手动安装，否则会导致无法自动清理存储空间。')


def check_network_connection():
    r_handle_in = os.popen("ping -c 1 sc.parkingwang.com")
    result = r_handle_in.read()
    r_handle_in.close()
    lost_per = ''
    index = result.rfind('% packet loss,')
    if index != -1:
        index_begin = result[:index].rfind(' ')
        if index_begin != -1:
            lost_per = result[index_begin + 1:index]
    if lost_per and int(lost_per) > 0:
        err(u'外网检测异常，请检查网络连接和DNS。')
    else:
        info(u'外网检测正常。')


def check_rinetd():
    # with open('/etc/rinetd.conf', 'rb') as r_handle:
    #     text = r_handle.read()
    # if text.find(value) == -1:
    #     info(u'rinted 配置检查结果, 正常。')
    # else:
    #     err(u'rinted 配置检查结果：错误，请手动进行修改。')

    pass


def check_link_file():
    r_handle = os.popen(
        '''python -c "import os,sys,irain_lib; print sys.modules['irain_lib'].__version__"'''
    )
    result = r_handle.read().strip()
    r_handle.close()
    info('版本检查: %s' % result)
    err_list = []
    file_list = [
        '/usr/local/lib/python2.7/dist-packages/irain_park-%s-py2.7.egg/irain_web/app/static/xls'
        % result
    ]
    for item in file_list:
        if not (not os.path.isfile(item) and os.path.exists(item)):
            err_list.append(item)
    if not err_list:
        info(u'V3 链接文件检查结果：正常。')
    else:
        err(u'V3 链接文件检查结果：异常，缺少以下文件：%s。' % err_list)


def main():
    local_ip = get_local_ip()
    set_prefix(local_ip)
    progress(5, '本机地址: %s' % local_ip)

    db_ip, db_port = get_mysql_addr()
    progress(15, '数据库地址: %s:%d' % (db_ip, db_port))

    try:
        check_disk_space()

        conn = MySQLdb.connect(
            host=db_ip,
            user='root',
            passwd='iraindb10241GB',
            db='irain_park',
            charset='utf8')
        cursor = conn.cursor()

        cursor.execute(
            'select depot_terminal.name from depot_terminal where depot_terminal.ip = "%s"; ' % local_ip)
        name = cursor.fetchall()

        progress(20, "板子名称：%s" % name[0])
        check_processes()

        progress(30)
        check_vpr_config(cursor, local_ip, db_ip)

        progress(40)
        check_boa_and_serial(cursor, local_ip)

        progress(50)
        check_paramiko()

        progress(60)
        check_network_connection()

        progress(70)
        check_rinetd()

        progress(80)
        check_link_file()

    except Exception, e:
        err("exception![%s]\n%s" % (str(e), traceback.format_exc()))


if __name__ == '__main__':
    start()
    main()
    end()
