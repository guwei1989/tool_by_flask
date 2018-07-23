# coding=utf-8
import uuid
from Queue import Queue
from threading import Lock
import datetime
from enum import Enum


class JobStatus(Enum):
    INIT, RUNNING, STOPPED = range(3)


class LogType(Enum):
    START, INFO, ERR, DEBUG, END, UNKNOWN, WARN = range(7)


class Job(object):
    """
    public api
    """
    def __init__(self):
        self.job_id = str(uuid.uuid4())
        self._status = JobStatus.INIT

        # job progress
        self._p = 0
        self._p_lock = Lock()

        self._buffer = Queue()

    def run(self, *args, **kwargs):
        """
        Subclass must override it and it should be a blocking call.
        :return None
        """
        raise Exception('Method not implemented')

    # def readable(self):
    #     """
    #     Return a bool to indicate that whether there is/will be some data can be read.
    #     :return bool
    #     """
    #     return not self._buffer.empty() or self.status < JobStatus.STOPPED

    def read(self, block=True):
        """
        Read logs from buffer.
            block: Wait for data if buffer is empty and job is not stopped.
        :return [JobLog...]
        """
        re = []

        if block and self._status != JobStatus.STOPPED and self._buffer.empty():
            re.append(self._buffer.get(block=True))

        while not self._buffer.empty():
            re.append(self._buffer.get(block=False))

        return re

    def read_all(self):
        while True:
            logs = self.read(True)
            if logs:
                for log in logs:
                    if log.log_type != LogType.START and log.log_type != LogType.END:
                        yield log
            else:
                return

    def _set_progress(self, p):
        if p < self._p or p < 0 or p > 100:
            return

        self._p_lock.acquire()
        self._p = p
        self._p_lock.release()

    def _p_start(self):
        self._status = JobStatus.RUNNING
        self._set_progress(0)
        self._log('', LogType.START)

    def _p_end(self):
        self._status = JobStatus.STOPPED
        self._set_progress(100)
        self._log('', LogType.END)

    def progress(self):
        return self._p

    def _info(self, msg):
        self._log(msg, LogType.INFO)

    def _err(self, msg):
        self._log(msg, LogType.ERR)

    def _warn(self, msg):
        self._log(msg, LogType.WARN)

    def _log(self, log='', log_type=LogType.INFO):
        if isinstance(log, JobLog):
            self._buffer.put(log)
            return

        for each_line in log.split('\n'):
            if isinstance(each_line, str):
                each_line = log.decode('utf-8')
            parsed_log = JobLog(self._p, log_type, datetime.datetime.now(), each_line)
            self._buffer.put(parsed_log)

    # def buffer_empty(self):
    #     return self._buffer.empty()
    #
    # def get_new_log(self, blocking=True):
    #     return self._buffer.get(block=blocking)
    #
    # def get_new_logs(self, blocking=False):
    #     # set blocking to True only works when buffer is empty
    #     logs = []
    #
    #     if self.buffer_empty() and blocking:
    #         log = self.get_new_log(blocking)
    #         logs.append(log)
    #     else:
    #         while not self.buffer_empty():
    #             log = self.get_new_log(blocking=False)
    #             logs.append(log)
    #
    #     return logs if len(logs) != 0 else None


class JobLog(object):
    def __init__(self, progress, log_type, log_time, log_str, value=''):
        self.progress = progress
        self.log_type = log_type
        self.time = log_time
        self.str = log_str.replace('\r', '')
        self.value = value

    def __repr__(self):
        return "[%d][%s][%s]:%s" % (self.progress, self.log_type.name, self.time,
                                    self.str)


def test():
    import threading
    j = Job()
    j._info("pre 1")
    j._info("pre 2")

    def producer():
        import time
        for i in range(5):
            time.sleep(1)
            j._info('hello')
        j._status = JobStatus.STOPPED

    threading.Thread(target=producer).start()

    for l in j.read_all():
        print l


if __name__ == '__main__':
    test()
