# coding: utf-8
from threading import RLock
from src.job.job import Job, LogType
from src.job.job_system import jobsystem
import paramiko
from src.frp.frp import frp
import traceback

from src.utils.threadpool import ThreadPool

log_lock = RLock()


class ChangeUploadURLJob(Job):
    def __init__(self):
        Job.__init__(self)
        self._pool = ThreadPool(30)

    def run(self, args=None):
        self._p_start()

        try:
            self._run()
        except Exception, e:
            self.progress(100, 'Caught Exception: %s\n%s' % (e, traceback.format_exc()))
            self._p_end()
            return

        self._p_end()

    def _run(self):
        all_conns = frp.get_all_conn_info()
        for conn_info in all_conns:
            self._pool.new(target=self._work, args=(conn_info,))
        self._pool.join()
        log('over')

    def _work(self, info):
        client, version = self._try_connect(info)
        if version == 3:
            self._v3(client, info)
        elif version == 2:
            self._v2(client, info)
        else:
            self._vunkown(client, info)

    def _v3(self, client, info):
        # log('v3 ' + info['host'] + ' : ' + str(info['port']))
        j = jobsystem.create_rs_job(client, 'static/scripts/20180509_v3_change_upload_url.py')
        jobsystem.run(j)
        while jobsystem.readable(j):
            news = jobsystem.job_news(j, blocking=True)
            if news is not None:
                for l in news:
                    if l.log_type == LogType.INFO:
                        log('v3 %s %d %s' %(info['host'], info['port'], l.str))
        client.close()

    def _v2(self, client, info):
        log('v2 %s %d' % (info['host'], info['port']))
        client.close()

    def _vunkown(self, client, info):
        log('?? %s %d' % (info['host'], info['port']))
        client.close()

    def _try_connect(self, info):
        version = None
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

        try:
            client.connect(info['host'], info['port'], 'root', 'iraindev10241GB')
            version = 3
        except paramiko.AuthenticationException:
            try:
                client.connect(info['host'], info['port'], 'root', '123456')
                version = 2
            except Exception:
                pass
        except Exception:
            pass

        return client, version


def log(msg):
    log_lock.acquire()
    print msg
    log_lock.release()


if __name__ == '__main__':
    import os

    os.chdir('../../..')

    j = ChangeUploadURLJob()
    j.run()
