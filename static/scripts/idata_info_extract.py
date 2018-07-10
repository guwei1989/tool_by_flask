# coding=utf-8
import datetime
import re
import sys

from helper import start, end, info, err, traceback
from log_helper import read_log_lines, LogFile


def sync_info_extract(lines, charge_no):
    # 过滤section时只过滤plate
    # 解析section时，根据解析结果 out_datetime再进行第二次过滤
    if not charge_no:
        return None

    # [ (lines[], parse_func)... ]
    sections = []

    # 0: undefined
    # 1: 查费 4104/4141
    # 2: 支付成功  4148
    section_type = 0

    c_no = ''

    # stack half-matched section start line num
    stack = []

    for l_no in range(len(lines)):
        line = lines[l_no]

        if 'idata recv' in line:
            if len(stack) > 0 and c_no == charge_no and section_type == 1:
                s_ln = stack.pop()
                e_ln = l_no - 1
                sections.append((lines[s_ln:e_ln], charge_detail))
            elif len(stack) > 0 and c_no == charge_no and section_type == 2:
                s_ln = stack.pop()
                e_ln = l_no - 1
                sections.append((lines[s_ln:e_ln], pay_success))

            while len(stack) > 0:
                stack.pop()
            stack.append(l_no)

            c_no = ''
            section_type = 0

        if 'idata recv 4104' in line:
            section_type = 1

        if 'idata recv 4141' in line:
            section_type = 1

        if 'idata recv 4148' in line:
            section_type = 2

        if charge_no in line:
            c_no = charge_no

    park_info = {}

    for section in sections:
        section_info = {}

        lines = section[0]
        parse_func = section[1]

        for l_no in range(len(lines)):
            output = parse_func(lines[l_no], l_no, lines)
            if output is not None and output[2] is not None:
                section_info.update(output[2])

        park_info.update(section_info)

    return park_info


def charge_detail(line, line_no, lines):
    log_time = line[:23]

    if '的板子处理' in line:
        match = re.search(r""":(.*?)的板子处理""", line)
        if match:
            arm_id = match.group(1)
            return log_time, u'重定向', {u'重定向': arm_id}
    elif '13: 计费规则' in line:
        rule_list = []
        for i in range(1, 100):
            cur_line = lines[line_no + i]
            match = re.search(r'''计费模板:(.*) priority(.*)('is_use': [1|T])''', cur_line)
            if match:
                charge_rule = match.group(1).decode('utf-8')
                rule_list.append(charge_rule)
            else:
                match = re.search(r'''计费模板：\[(.*?)0\] or \[(.*?)1\]:(.*)''', cur_line)
                if match:
                    rule_0 = match.group(1).decode('utf-8')
                    rule_1 = match.group(2).decode('utf-8')
                    rule_used = match.group(3).strip()
                    if rule_used == '0':
                        rule_list.append(rule_0)
                    elif rule_used == '1':
                        rule_list.append(rule_1)

            if 'init param' in cur_line:
                return log_time, u'历史计费规则', {u'历史计费规则': rule_list}
    elif '11: 分段计费' in line:
        charge_list = []
        for i in range(300):
            cur_line = lines[line_no + i]
            if '总费用 total_price' in cur_line:
                return log_time, u'历史计费详情', {u'历史计费详情': charge_list}
            match = re.search(r'''\] (.*?):.*time:\[(.*?)\] 费用charge\[(.*?)\]''', cur_line)
            if match:
                charge_type = match.group(1).decode('utf-8')
                charge_time = match.group(2)
                charge_start = charge_time.split(' ')[0] + ' ' + charge_time.split(' ')[1]
                charge_end = charge_time.split(' ')[2] + ' ' + charge_time.split(' ')[3]

                charge_value = float(match.group(3)) / 100
                charge_list.append((charge_type, datetime.datetime.strptime(charge_start, '%Y-%m-%d %H:%M:%S'),
                                    datetime.datetime.strptime(charge_end, '%Y-%m-%d %H:%M:%S'), charge_value))
    elif '订单计算过程结束' in line:
        match = re.search(r"""should pay:(.*)""", lines[line_no + 2])
        if match:
            shoud_pay = float(match.group(1)) / 100
            return log_time, u'历史计费结果', {u'历史计费结果': shoud_pay}


def pay_success(line, line_no, lines):
    log_time = line[:23]

    if 'INSERT INTO pay_count' in line:
        return log_time, u'数据库写费时间', {u'数据库写费时间': datetime.datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f')}


def main():
    start()
    try:
        charge_no = sys.argv[1]
        log_date = sys.argv[2]
        log_date = datetime.datetime.strptime(log_date, '%Y-%m-%d').date()

        lines = read_log_lines(LogFile.IData, log_date)
        if not lines:
            raise Exception('Read nothing from log')
        sync_info = sync_info_extract(lines, charge_no)
        info(sync_info.__repr__())
    except Exception, e:
        err('%s\n%s' % (str(e), traceback()))
    end()


if __name__ == '__main__':
    main()
