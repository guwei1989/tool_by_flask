# coding: utf-8
from paramiko import SSHException

from src.frp import frp
from src.job.job import Job, JobStatus
from src.job.job_system import jobsystem
from src.job.remote_script_job import RemoteScriptOutputParser, RemoteScriptJob


class AllArmJob(Job):
    """
    user should call self.progress_end() at appropriate time to indicate system the job is ended
    """

    def __init__(self, ssh_client):
        Job.__init__(self)
        self.ssh_client = ssh_client

        self._raw_output = []
        self._last_log = None

        self._parser = RemoteScriptOutputParser()

    def run(self, func):
        self._p_start()
        all_arm = self._get_all_arm()
        for arm_ip in all_arm:
            tunnel, ver = frp.make_tunnel(self.ssh_client, arm_ip)
            func(tunnel, arm_ip)

    def _get_all_arm(self):
        j = RemoteScriptJob(self.ssh_client, 'static/scripts/get_all_arm_ip.py')
        jobsystem.add_job(j)
        jobsystem.run(j.job_id)
        output = []

        for j_log in j.read_all():
            msg = j_log.str.strip()
            if msg != '':
                output.append(msg)

        return output
