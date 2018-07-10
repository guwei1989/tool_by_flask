# coding: utf-8
from src.job.job import Job
from src.job.job_system import jobsystem


class FanOutJob(Job):
    def __init__(self, *jobs):
        Job.__init__(self)
        self.jobs = [j for j in jobs]
        self.args = [() for x in jobs]

    def run(self, *args):
        self._p_start()
        for job_index in range(len(self.jobs)):
            job = self.jobs[job_index]
            job_args = self.args[job_index]
            if isinstance(job, Job):
                jobsystem.add_job(job)
                jobsystem.run(job.job_id, args=job_args)
                for log in jobsystem.read_all(job.job_id):
                    self._info(log)
        self._p_end()

    def add(self, job, job_args):
        """
        add should be called before run so all jobs will be guaranteed to run
        :param job:
        :param job_args:
        :return:
        """
        self.jobs.append(job)
        self.args.append(job_args)
