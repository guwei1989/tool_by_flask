# coding=utf-8
import traceback

from src.job.job import Job, JobLog, LogType
from log_manager import get_log
from log_fetch import IRainLogType
from parser.park_out import parse_all, parse_plate


class ParkOutAnalyseJob(Job):
    def __init__(self):
        Job.__init__(self)
        self._sections = None

    def run(self, *args):
        self._p_start()
        try:
            self._safe_run(*args)
        except Exception, err:
            self._err(u'解析过程遇到错误 %s\n%s' % (str(err), traceback.format_exc()))
        self._p_end()

    def _safe_run(self, park_name, log_date, ssh_client=None, vpr='', force_download=False):
        self._info(u'正在下载日志...')
        log_path = get_log(IRainLogType.PARK_OUT, log_date, park_name, force_download=force_download,
                           ssh_client=ssh_client)
        self._info(u'开始解析...')
        with open(log_path) as f:
            if vpr:
                self._parse_plate(f, vpr)
            else:
                self._parse_file(f)

    def _parse_file(self, f):
        lines = f.readlines()
        sections = parse_all(lines)
        self._sections = sections
        for section in sections:
            for each_log in section.logs():
                extra = u'  '.join(
                    [u'%s: %s' % (k, v if isinstance(v, unicode) else str(v)) for k, v in each_log[2].items()])
                log_item = JobLog(50, LogType.INFO, each_log[0], u'%s %s' % (each_log[1], extra))
                self._info(log_item)

    def _parse_plate(self, f, plate):
        lines = f.readlines()
        all_records = parse_plate(lines, plate)
        self._sections = all_records
        for record in all_records:
            log_item = JobLog(50, LogType.INFO, record[u'出场时间'], str(record[u'出场时间']).decode('utf-8'), record)
            self._info(log_item)

    def sections(self):
        return self._sections


def test():
    from src.job.job_system import jobsystem
    import datetime
    import os

    os.chdir('../../../')
    j = ParkOutAnalyseJob()
    jobsystem.add_job(j)
    jobsystem.run(j.job_id, (u'龙城大院', datetime.date.today()))
    while not jobsystem.is_finished(j.job_id) or jobsystem.readable(j.job_id):
        print jobsystem.job_news(j.job_id, blocking=True)

    for section in j.sections():
        print 'duration: ', section.duration()


if __name__ == '__main__':
    test()
