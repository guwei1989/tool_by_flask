# coding: utf-8
from remote_exec import execute_file
from job import Job, JobLog, JobStatus, LogType
import re


class RemoteScriptJob(Job):
    def __init__(self, ssh_client, script_path):
        Job.__init__(self)
        self.script_path = script_path
        self.ssh_client = ssh_client

        self._raw_output = []
        self._last_log = None

        self._parser = RemoteScriptOutputParser()

    def run(self, args=()):
        stdout = execute_file(self.ssh_client, self.script_path, args)
        while self._status != JobStatus.STOPPED:
            line = stdout.readline()
            self._raw_output.append(line)
            parsed_log = self._parser.parse(line)

            if parsed_log is None:
                # 当job已经开始时，所有无法解析的日志会按上条有效日志的格式打印
                if self._status != JobStatus.INIT and line.strip() != '':
                    parsed_log = JobLog(self._p, LogType.UNKNOWN,
                                        self._last_log.time,
                                        line.replace('\n', '').strip())
                    self._add_log(parsed_log)
                continue

            self._set_progress(parsed_log.progress)

            if parsed_log.log_type == LogType.START:
                self._status = JobStatus.RUNNING

            if parsed_log.log_type == LogType.END:
                self._status = JobStatus.STOPPED

            if parsed_log.log_type in [LogType.ERR, LogType.INFO
                                       ] and parsed_log.str.strip() == '':
                continue

            self._add_log(parsed_log)

    def _add_log(self, log):
        self._log(log)
        self._last_log = log


class RemoteScriptOutputParser(object):
    LOG_TYPES_LOOKUP = t = {e.name: e for e in LogType}

    def __init__(self):
        self.pattern = re.compile(r'''\[(.*)\]\[(.*)\]\[(.*)\]:(.*)''')

    def parse(self, one_line):
        search_result = re.match(self.pattern, one_line)
        if search_result is None:
            return None

        progress = int(search_result.group(1))
        log_type_str = search_result.group(2)
        log_type = self.LOG_TYPES_LOOKUP[
            log_type_str] if log_type_str in self.LOG_TYPES_LOOKUP else LogType.UNKNOWN
        log_time = search_result.group(3)
        log_str = search_result.group(4).strip()

        return JobLog(progress, log_type, log_time, log_str)


def test():
    from src.frp.frp import frp
    from job_system import jobsystem
    import os
    from src.utils.quick import make_tunnel

    os.chdir('../../')
    conn, _ = frp.get_conn(u'凯德东')
    tunnel, _ = make_tunnel(conn, '192.168.55.247')
    j = RemoteScriptJob(tunnel, 'static/scripts/park_info_extract.py')
    jobsystem.add_job(j)
    # jobsystem.start_job(j.job_id, ('陕A326CL', '"2018-06-10 16:23:03"'))
    jobsystem.run(j.job_id, ('陕AQ22K8', '"2018-06-06 00:17:20"'))

    for log in jobsystem.read_all(j.job_id):
        print log.str


if __name__ == '__main__':
    test()
