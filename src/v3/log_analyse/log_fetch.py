# coding: utf-8
import os
from enum import Enum
import datetime
import threading
import tarfile
import shutil
import posixpath


class IRainLogType(Enum):
    PARK_IN, PARK_OUT, SYNC_IDATA = range(3)


log_type_dict = {
    IRainLogType.PARK_IN: 'irain_park_in',
    IRainLogType.PARK_OUT: 'irain_park_out',
    IRainLogType.SYNC_IDATA: 'irain_sync_idata'
}

V3_LOG_DIR = '/home/park/log'


def log_file_name(log_type, log_date):
    return '%s.log.%s' % (log_type_dict[log_type], str(log_date))


def fetch(sftp, log_type, log_date, store_path):
    """
    This is a blocking call
    :param sftp: paramiko.SFTP
    :param log_type: IRainLogType
    :param log_date: datetime.date，精确到天
    :return: 返回file_path
    """
    l_logfile_path = os.path.join(store_path, log_file_name(log_type, log_date))
    if os.path.exists(l_logfile_path):
        os.remove(l_logfile_path)

    today = datetime.date.today()
    if log_date > today:
        raise Exception("Invalid log_time")

    if log_date == today:
        r_f_path = posixpath.join(V3_LOG_DIR, '%s.log' % log_type_dict[log_type])
        l_f_path = os.path.join(store_path, log_file_name(log_type, log_date))
        return _fetch_file(sftp, r_f_path, l_f_path)

    else:
        r_tar_path = posixpath.join(V3_LOG_DIR, 'arm%s.tar.gz' % log_date.strftime('%Y%m%d')[2:])
        l_tar_path = os.path.join(store_path, 'arm%s.tar.gz' % log_date.strftime('%Y%m%d')[2:])
        return _handle_tar_log(sftp, r_tar_path, l_tar_path, log_type, log_date)


def _fetch_file(sftp, r_file_path, l_file_path):
    sftp.get(r_file_path, l_file_path)
    return l_file_path


def _fetch_and_untar(sftp, r_tar_path, l_tar_path, log_date):
    if os.path.exists(l_tar_path):
        os.remove(l_tar_path)

    sftp.get(r_tar_path, l_tar_path)
    desire_dir = os.path.dirname(l_tar_path)
    with tarfile.open(l_tar_path) as tmp_tar:
        if os.path.exists(os.path.join(l_tar_path, 'arm%s' % log_date.strftime('%Y%m%d')[2:])):
            shutil.rmtree(os.path.join(l_tar_path, 'arm%s' % log_date.strftime('%Y%m%d')[2:]))
        tmp_tar.extractall(desire_dir)
        return tmp_tar.getnames()


def _handle_tar_log(sftp, r_tar_path, l_tar_path, log_type, log_date):
    f_list = _fetch_and_untar(sftp, r_tar_path, l_tar_path, log_date)
    os.remove(l_tar_path)

    for f_name in f_list:
        ori_f_path = os.path.join(os.path.dirname(l_tar_path), f_name)
        now_f_path = os.path.join(os.path.dirname(l_tar_path), os.path.basename(f_name))
        shutil.move(ori_f_path, now_f_path)

    shutil.rmtree(os.path.join(os.path.dirname(l_tar_path), 'arm%s' % log_date.strftime('%Y%m%d')[2:]))

    desired_f_name = filter(lambda x: x.find(log_type_dict[log_type]) != -1, f_list)[0]
    desired_f = os.path.join(os.path.dirname(l_tar_path), os.path.basename(desired_f_name))
    return desired_f


def r_file_exist(sftp, file_path):
    try:
        sftp.stat(file_path)
    except IOError:
        return False
    return True


def test():
    os.chdir('../../../')
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    client.connect('121.199.49.228', 11265, 'root', 'iraindev10241GB')

    log_date = datetime.date.today() - datetime.timedelta(1)

    fetch(client.open_sftp(), IRainLogType.PARK_OUT, log_date, 'log_file/121.199.49.228.10265/')


if __name__ == '__main__':
    test()
