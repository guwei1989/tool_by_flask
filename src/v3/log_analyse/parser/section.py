# coding: utf-8
import datetime


class Section(object):
    def __init__(self, lines, parser):
        self._lines = lines
        self._logs = []
        self._parser = parser
        self._parse()

    @classmethod
    def from_lines(cls, lines, parser):
        s = Section(lines, parser)
        return s

    def lines(self):
        return self._lines

    def logs(self):
        return self._logs

    def duration(self):
        try:
            e_time = datetime.datetime.strptime(self._logs[-1][0], '%Y-%m-%d %H:%M:%S,%f')
            s_time = datetime.datetime.strptime(self._logs[0][0], '%Y-%m-%d %H:%M:%S,%f')
        except IndexError:
            return 0

        return e_time - s_time

    def _parse(self):
        for line_no in range(len(self._lines)):
            log = self._parser(self._lines[line_no], line_no, self._lines)
            if isinstance(log, tuple):
                self._logs.append(log)


