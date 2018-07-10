# coding=utf-8
import datetime
import os
import tarfile

from helper import pia_version


class LogFile:
    ParkIn = 'irain_park_in'
    ParkOut = 'irain_park_out'
    IData = 'irain_sync_idata'
    SYNC = 'irain_sync'


def read_log_lines(log_name, log_date):
    if pia_version() == 3:
        # today
        if log_date == datetime.date.today():
            return open(os.path.join('/home/park/log', '%s.log' % log_name)).readlines()
        # history log
        else:
            tar_name = os.path.join('/home/park/log', 'arm%s.tar.gz' % log_date.strftime('%y%m%d'))
            if not os.path.exists(tar_name):
                raise Exception("""%s not found on disk""" % tar_name)
            with tarfile.open(tar_name) as tar_f:
                for member_f in tar_f.getmembers():
                    if log_name in member_f.path:
                        return tar_f.extractfile(member_f).readlines()
        # didn't find anything
        raise Exception("""Didn't find %s in tar %s""" % (log_name, tar_name))
    else:
        # only support v3 now
        raise Exception("""Only support v3 now""")
