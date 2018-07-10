# coding:utf-8
import os
import MySQLdb
import paramiko
import traceback
import time
from datetime import date, datetime, timedelta
from datetime import time as datetime_time
from helper import info, start, end, err, progress, get_mysql_addr


class ObjectDict(dict):
    """
    A GetAttr object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.

        >>> o = ObjectDict(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        >>>

    """

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError(k)

    def __repr__(self):
        return dict.__repr__(self)


def _time2str(time_obj):
    """Convert Datetime to String"""
    if isinstance(time_obj, datetime):
        time_str = format(time_obj, "%Y-%m-%d %X")
    elif isinstance(time_obj, date):
        time_str = format(time_obj, "%Y-%m-%d")
    elif isinstance(time_obj, datetime_time):
        time_str = str(time_obj).split(".")[0]
    elif isinstance(time_obj, basestring):
        time_str = time_obj
    else:
        time_str = ""
    return time_str


def _str2time(time_str):
    """Convert String to Datetime"""
    if isinstance(time_str, basestring):
        if "-" in time_str and ":" in time_str:
            _datetime = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        elif ":" in time_str:
            new_time_str = _now_str()[:11] + time_str
            _datetime = datetime.strptime(new_time_str, "%Y-%m-%d %X")
        else:
            _datetime = datetime.strptime(time_str, "%Y-%m-%d")
        return _datetime
    else:
        return time_str


def _daterange(start_date, end_date):
    """生成器: 处理日期遍历"""
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


def _dateslice(date_list):
    """给不连续的时间序列分段"""
    tmp = []
    for index, _ in enumerate(date_list):
        if index == 0 or date_list[index] - date_list[index - 1] != timedelta(1):
            tmp.append([date_list[index]])
        else:
            tmp[-1].append(date_list[index])
    return tmp


def _now_str():
    """Get Current Datetime String"""
    return str(_now())[:19]


def _now():
    """Get Current Datetime"""
    return datetime.now()


def set_more_validity_time(sday, eday, time_range, week):
    """授权记录拆分成连续时间段的多条记录
        (一天内不可以有两段授权时间段
        跨夜除外, 示例:
            传入:
                sday="2017-10-24",
                eday="2017-10-24",
                time_range="20:00:00, 08:00:00",
                week="1,2,3,4,5,6,7"
            返回:
                validity_start="2017-10-24 20:00:00",
                validity_end="2017-10-25 08:00:00"
        )

    :param sday: 有效期开始日期
    :type sady: Date String
    :param eday: 有效期截止日期
    :type eday: Date String
    :param time_range: 有效期时间段
    :type time_range: Str
    :param week: 一周的哪几天
    :type week: Str

    :return:
        :param validity_count: 有效期条数
        :param validity_list: 有效期列表
        :type List
            :param sday: 有效期开始日期
            :type sady: Date String
            :param eday: 有效期截止日期
            :type eday: Date String
            :param time_range: 有效期时间段
            :type time_range: Str
            :param validity_start: 有效开始时间
            :type validity_start: DateTime String
            :param validity_end: 有效截止时间
            :type validity_end: DateTime String
    """
    # print(u"[set_more_validity_time]入参: \n"
    #         u"开始日期:%s, 截止日期:%s, 时间段:%s, 周:%s" % (sday, eday, time_range, str(week)))
    result = ObjectDict(validity_count=0, validity_list=[])

    if isinstance(time_range, basestring):
        start_time, end_time = time_range.split(",")
    else:
        start_time, end_time = time_range
    if isinstance(week, basestring):
        weekdays = map(int, week.split(","))
    else:
        weekdays = map(int, week)
    valid_dates = filter(lambda x: x.isoweekday() in weekdays,
                         _daterange(
                             _str2time(sday) if isinstance(sday, basestring) else sday,
                             _str2time(eday) if isinstance(eday, basestring) else eday
                         ))
    # print(u"[set_more_validity_time]经解析后的时间数据: \n"
    #         u"开始日期:%s, 截止日期:%s, 时间段:%s, 周:%s" % (sday, eday, time_range, week))
    if len(valid_dates) > 10:
        valid_dates_log = [valid_dates[:5], "......", valid_dates[-5:]]
    else:
        valid_dates_log = valid_dates
    # print(u"[set_more_validity_time]有效的日期列表:\n %s" % valid_dates_log)
    if start_time < end_time:
        # 还要判断时间是否连续 00:00:00 23:59:59;
        now = _now_str()
        if start_time == "00:00:00" and end_time == "23:59:59":
            result.validity_list = map(lambda x: ObjectDict(
                sday=_time2str(x[0]),
                eday=_time2str(x[-1]),
                time_range=time_range,
                validity_start="{0} {1}".format(_time2str(x[0])[:10], start_time),
                validity_end="{0} {1}".format(_time2str(x[-1])[:10], end_time),
            ), _dateslice(valid_dates))
        else:
            result.validity_list = map(lambda x: ObjectDict(
                sday=_time2str(x[0]),
                eday=_time2str(x[-1]),
                time_range=time_range,
                validity_start="{0} {1}".format(_time2str(x[0])[:10], start_time),
                validity_end="{0} {1}".format(_time2str(x[-1])[:10], end_time),
            ), map(lambda x: (x, x), valid_dates))
    else:
        result.validity_list = map(lambda x: ObjectDict(
            sday=_time2str(x),
            eday=_time2str(x),
            time_range=time_range,
            validity_start="{0} {1}".format(_time2str(x)[:10], start_time),
            validity_end="{0} {1}".format(_time2str(x + timedelta(1))[:10], end_time),
        ), valid_dates)
    if len(result.validity_list) > 10:
        valid_datetime_log = [result.validity_list[:5], "......", result.validity_list[-5:]]
    else:
        valid_datetime_log = result.validity_list
    # print(u"[set_more_validity_time]得到的有效时间列表: \n %s" % valid_datetime_log)
    result.validity_count = len(result.validity_list)
    # print ("u*******result: \n %s" % result)
    return result


def active_connect(ip, port, name, pwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, name, pwd, timeout=20)
    return ssh


if __name__ == "__main__":

    progress(0)
    start()

    try:
        db_ip, db_port = get_mysql_addr()
        arm_ip = os.popen(
            "ifconfig | grep 'inet addr:' | grep -v '127.0.0.1' | cut -d: -f2 | awk '{print $1}' | head -1").read()
    except Exception as e:
        err("init param exception %s\n%s" % (e, traceback.format_exc()))

    try:
        info("mysqldump start")

        tool_run_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        ssh = active_connect(str(arm_ip), 22, "root", "iraindev10241GB")
        ssh.exec_command(
            "mysqldump -h%s -uroot -piraindb10241GB irain_park new_auth_charge > /home/park/new_auth_charge_%s.sql"
            % (db_ip, tool_run_time))

        info("mysqldump new_auth_charge end")

    except Exception as e:
        err("dump new_auth_charge failed：%s" % e)

    try:
        info("operate mysql start")

        conn = MySQLdb.connect(host=db_ip, port=db_port, user='root', passwd='iraindb10241GB', db='irain_park',
                               charset='utf8')
        cursor = conn.cursor()
        new_auth_charge_list = cursor.execute(
            "select a.* from new_auth_charge as a left join new_auth_group as b on a.auth_no=b.auth_no where"
            " a.time_range='00:00:00,23:59:59' and b.week = '1,2,3,4,5,6,7' and DATE(a.eday) != DATE(a.validity_end);")
        new_auth_charge_list = cursor.fetchall()

        for charge in list(new_auth_charge_list):
            cursor.execute("delete from new_auth_charge where auth_no = '%s'" % str(charge[1]))
            conn.commit()

            result_list = set_more_validity_time(charge[3], charge[4], charge[5], "1,2,3,4,5,6,7")
            for result in result_list["validity_list"]:
                cursor.execute(
                    "INSERT INTO new_auth_charge "
                    "(auth_no, auth_type, sday, eday, time_range, validity_start, validity_end, serial_no, "
                    "register, op_type, op_time, save_time, valid_flag) "
                    "VALUES ('%s', %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', %d);"
                    % (str(charge[1]), int(charge[2]), datetime.strptime(result["sday"], '%Y-%m-%d %H:%M:%S'),
                       datetime.strptime(result["eday"], '%Y-%m-%d %H:%M:%S'), str(result["time_range"]),
                       datetime.strptime(result["validity_start"], '%Y-%m-%d %H:%M:%S'),
                       datetime.strptime(result["validity_end"], '%Y-%m-%d %H:%M:%S'),
                       str(charge[8]), str(charge[9]), int(charge[10]), str(charge[11]), str(charge[12]), int(charge[13])))
                conn.commit()

        info("operate mysql end")

        progress(100)
        info("success")
    except Exception as e:
        err("mysql operate new_auth_charge failed %s" % e)

    end()
