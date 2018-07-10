# coding: utf-8
import datetime
import threading
import os
import traceback as trace

job_percentage = 0
log_lock = threading.RLock()
p_lock = threading.Lock()
prefix = ''


def _log(msg, logtype='INFO'):
    # 1.convert msg to str
    # 2.when there is '\n' in msg, _log() for every line
    with log_lock:
        msg_str = str(msg)
        for each in msg_str.split('\n'):
            print '[%d][%s][%s]:%s %s' % (job_percentage, logtype,
                                          datetime.datetime.now(), prefix, str(each))


def info(msg):
    _log(msg, 'INFO')


def err(msg):
    _log(msg, 'ERR')


def debug(msg):
    _log(msg, 'DEBUG')


def start():
    if job_percentage != 0:
        progress(0)
    _log('', 'START')


def end():
    if job_percentage != 100:
        progress(100)
    _log('', 'END')


def progress(p=None, msg=None):
    global job_percentage
    if p is None:
        return job_percentage

    if p > job_percentage and 0 <= p <= 100:
        p_lock.acquire()
        job_percentage = p
        p_lock.release()

    if msg is not None:
        info(msg)


def set_prefix(p):
    global prefix
    prefix = p


def get_mysql_addr():
    """
    :return:
        tuple
        ( '192.168.0.5', 3306)
    """
    if pia_version() == 3:
        out = os.popen("cat /home/park/config/config.cfg |grep -A5 '\[mysql\]' | grep -v mysql | awk "
                       "'{print $3}'")
        output = out.readlines()
        addr = output[0].replace('\n', '')
        port = int(output[3])
        out.close()
        return addr, port
    else:
        out = os.popen("cat /mnt/nfs/local/wacs/etc/device.conf |grep -E 'db_server '|awk '{print $3}'")
        output = out.readlines()
        addr = output[0].replace('\n', '')
        addr = "127.0.0.1" if addr == 'localhost' else addr
        out2 = os.popen("cat /mnt/nfs/local/wacs/etc/device.conf |grep -E 'db_server_port '|awk '{print $3}'")
        output2 = out2.readlines()
        port = output2[0].replace('\n', '')
        out.close()
        out2.close()
        return addr, port


def get_all_terminals_addr():
    """
    :return:
        list
        [
            '192.168.0.1',
            '192.168.0.2'
        ]
    """
    if pia_version() == 3:
        mysql, _ = get_mysql_addr()
        out = os.popen('mysql -h%s -s -N -uroot -piraindb10241GB irain_park -e "select ip from depot_terminal"' % mysql)
        result = out.readlines()
        out.close()
        return result
    else:
        mysql, _ = get_mysql_addr()
        out = os.popen('mysql -h%s -s -N -uroot -pa1b2c3 acdbs -e "select ip from hostlist"' % mysql)
        result = out.readlines()
        out.close()
        return result


def get_local_ip():
    """
        :return:
            str
            '192.168.55.248'
        """
    out = os.popen("""ifconfig eth0 | grep 'inet addr'|awk '{print $2}'|awk -F':' '{print $2}'""")
    result = out.read()
    out.close()
    return result.replace('\n', '').strip()


def traceback():
    return trace.format_exc()


def pia_version():
    # return 2 or 3
    if os.path.exists('/home/park/log'):
        return 3
    else:
        return 2


def l_exec_cmd(command):
    out = os.popen(command)

    line = out.readline()
    while line:
        yield line.strip()
        line = out.readline()


if __name__ == '__main__':
    info('qweqweqw\nrewrew')
