# coding: utf-8
import threading
from src.utils.threadpool import ThreadPool
from remote_script_job import RemoteScriptJob
from job import JobStatus, LogType


class JobSystem(object):
    def __init__(self):
        self._jobs = {}
        self._threads = {}
        self._thread_pool = ThreadPool(4)

    def add_job(self, jb):
        self._jobs[jb.job_id] = jb
        return jb.job_id

    def run(self, j, args=()):
        self.add_job(j)

        t = threading.Thread(target=j.run, args=args)
        self._threads[j.job_id] = t
        t.start()

    def start_pool_job(self, job_id, args=()):
        j = self.get_job(job_id)
        if j is None:
            raise Exception("Job not found : %s" % job_id)

        self._thread_pool.new(target=j.run, args=args)

    def thread_pool(self):
        return self._thread_pool

    def job_progress(self, job_id):
        jb = self.get_job(job_id)
        if jb is None:
            raise Exception("Job not found : %s" % job_id)
        return jb.progress()

    def job_news(self, job_id, filter_func=None, blocking=False):
        job = self.get_job(job_id)

        if job is None:
            raise Exception("Job not found : %s" % job_id)

        raw = job.get_new_logs(blocking)

        if filter_func is not None and raw is not None:
            raw = filter(filter_func, raw)

        return raw

    def get_job(self, job_id):
        return self._jobs[job_id] if self._jobs.has_key(job_id) else None

    # def _get_thread(self, job_id):
    #     return self._threads[job_id] if self._threads.has_key(job_id) else None

    def create_rs_job(self, client, script_path):
        j = RemoteScriptJob(client, script_path)
        self.add_job(j)
        return j.job_id

    def is_finished(self, job_id):
        j = self.get_job(job_id)
        if j is None:
            raise Exception("Job not found : %s" % job_id)

        return j.status == JobStatus.STOPPED

    def readable(self, job_id):
        j = self.get_job(job_id)
        if j is None:
            raise Exception("Job not found : %s" % job_id)
        return j.status == JobStatus.INIT or j.status == JobStatus.RUNNING or not j.buffer_empty()

    def read_all(self, job_id):
        j = self.get_job(job_id)

        while self.readable(job_id) or not self.is_finished(job_id):
            raw = j.get_new_log(blocking=True)
            if raw.log_type != LogType.START and raw.log_type != LogType.END:
                yield raw
            if raw.log_type == LogType.END:
                return


jobsystem = JobSystem()


def test():
    js = JobSystem()

    import paramiko
    import os

    # monkey patch working directory
    os.chdir('../../')

    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(
        hostname='121.199.49.228',
        port=10200,
        username='root',
        password='iraindev10241GB',
        timeout=10)
    j = RemoteScriptJob(conn, 'static/scripts/get_all_arm_ip.py')
    # j = RemoteScriptJob(conn, 'static/scripts/a.py')

    j_id = js.add_job(j)
    js.run(j_id)
    # while j.status != JobStatus.STOPPED or j.readable():
    #     print j.get_new_log()
    for log in js.read_all(j.job_id):
        print log.str


if __name__ == '__main__':
    test()
