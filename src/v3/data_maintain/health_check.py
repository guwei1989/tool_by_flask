# coding: utf-8
from src.job.job import Job, JobStatus, LogType
from src.job.remote_script_job import RemoteScriptJob
from src.job.job_system import jobsystem
import paramiko


class HealthCheckJob(Job):
    def __init__(self, ssh_client):
        Job.__init__(self)
        self._client = ssh_client

        self._all_arms = None

    def run(self, *args):
        self._p_start()

        all_arms = self._get_all_arms()
        self.progress(5, '所有ARM:')
        self._info('\n'.join(all_arms))

        progress_per_arm = (100 - 10) / len(all_arms)

        for arm in all_arms:
            self._info('')
            self.progress(self.progress() + 1, '开始体检 %s' % arm)
            self._do_check(arm)
            self.progress(self.progress() + progress_per_arm)

        self._p_end()

    def _get_all_arms(self):
        if self._all_arms:
            return self._all_arms

        j = RemoteScriptJob(self._client, 'static/scripts/get_all_arm_ip.py')
        jobsystem.add_job(j)
        jobsystem.run(j.job_id)
        output = []

        while j.status != JobStatus.STOPPED or j.readable():
            msg = j.get_new_log().str.strip()
            if msg != '':
                output.append(msg)

        return output

    def _do_check(self, arm_ip):
        chan = self._client.get_transport().open_channel('direct-tcpip', (arm_ip, 22), ('localhost', 44444))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        c.connect(None, username='root', password='iraindev10241GB', sock=chan)

        j = RemoteScriptJob(c, 'static/scripts/v3_health_check.py')
        jobsystem.add_job(j)
        jobsystem.run(j.job_id)
        while j.status != JobStatus.STOPPED or j.readable():
            log = j.get_new_log()
            if log.log_type != LogType.START and log.log_type != LogType.END:
                log.progress = self._p
                self._info(log)


def test():
    import os
    from src.job.job_system import jobsystem as js

    os.chdir('../../')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname='121.199.49.228',
        port=10200,
        username='root',
        password='iraindev10241GB',
        timeout=10)
    # j = RemoteScriptJob(conn, 'static/scripts/get_all_arm_ip.py')
    # j = RemoteScriptJob(conn, 'static/scripts/a.py')
    j = HealthCheckJob(client)

    j_id = js.add_job(j)
    js.run(j_id)
    while j._status != JobStatus.STOPPED or j.readable():
        print j.get_new_log()


if __name__ == '__main__':
    test()
