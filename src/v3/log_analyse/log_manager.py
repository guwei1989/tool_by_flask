# coding: utf-8
import os
from log_fetch import log_file_name, fetch
from src.frp.frp import frp
from src.utils.quick import get_local_ip, make_tunnel
from pypinyin import lazy_pinyin

LOCAL_LOG_DIR = 'log_file'


def park_log_path(park_name, arm_ip):
    return os.path.join(LOCAL_LOG_DIR, ''.join(lazy_pinyin(park_name)), arm_ip)


def has_log(park_name, arm_ip, log_type, log_date):
    log_path = os.path.join(park_log_path(park_name, arm_ip), log_file_name(log_type, log_date))
    return os.path.exists(log_path)


def get_log(log_type, log_date, park_name, force_download=False, ssh_client=None):
    """
    :param park_name:
    :param log_type:
    :param log_date:
    :param force_download: 是否强制重新下载日志（如果本地已缓存），常用于刷新当天日志
    :param ssh_client:
    :return: file path
    """
    if not ssh_client:
        ssh_client = frp.get_conn(park_name)
    if ssh_client is None:
        return None

    arm_ip = get_local_ip(ssh_client)

    log_dir = park_log_path(park_name, arm_ip)

    if not force_download and has_log(park_name, arm_ip, log_type, log_date):
        return os.path.join(log_dir, log_file_name(log_type, log_date))

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return fetch(ssh_client.open_sftp(), log_type, log_date, log_dir)


def test():
    os.chdir('../../../')
    from log_fetch import IRainLogType
    import datetime
    ssh_client, _ = frp.get_conn(u'凯德东')
    tunnel, _ = make_tunnel(ssh_client, '192.168.55.247')
    print get_log(IRainLogType.PARK_OUT, datetime.date.today(), u'凯德东', force_download=True, ssh_client=tunnel)


if __name__ == '__main__':
    test()
