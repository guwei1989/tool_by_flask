# coding:utf-8
from Queue import Queue
from section import Section
import re
import datetime


def parse_all(lines):
    section_indexes = Queue()

    for line_no in range(len(lines)):
        line = lines[line_no]

        if '====begin' in line:
            section_indexes.put(line_no - 1)
        if '====end' in line:
            section_indexes.put(line_no + 1)

    sections = []

    while not section_indexes.empty():
        # this could happen when logfile is damaged
        if section_indexes.qsize() == 1:
            break
        section_lines = lines[section_indexes.get():section_indexes.get()]
        sections.append(Section.from_lines(section_lines, _parser))

    return sections


def parse_plate(lines, plate):
    if not plate:
        return None

    section_indexes = []

    found = False
    for line_no in range(len(lines)):
        line = lines[line_no]
        vpr = ''

        if '====begin' in line:
            section_indexes.append(line_no - 1)
            found = False
        elif 'get fifo data ={' in line:
            match = re.search(r"'ComLicence': u'(.*?)'", line)
            if match:
                vpr = match.group(1).decode('unicode-escape')
            else:
                match = re.search(r"'ComLicence2': u'(.*?)'", line)
                if match:
                    vpr = match.group(1).decode('unicode-escape')
            if plate in vpr:
                found = True
        elif '双识别第二次识别数据处理流程' in line:
            found = False
        elif '====end' in line:
            if found:
                section_indexes.append(line_no + 1)
            else:
                section_indexes.pop()
            found = False

    sections = []

    for lno in range(len(section_indexes)):
        if lno % 2 == 1:
            section_lines = lines[section_indexes[lno - 1]:section_indexes[lno]]
            s = Section.from_lines(section_lines, _parser)

            parsed_info = {}
            for lg in s.logs():
                extra = lg[2]
                parsed_info.update(extra)
            sections.append(parsed_info)

            if lno == len(section_indexes) - 1:
                break

    return sections


def _parser(line, line_no, lines):
    """
    :param line:
    :return:  (log_time[str], log_type[str], extra_data[dict][None if no data])
    """
    log_time = line[:23]

    if 'get fifo data ={' in line:
        plate = ''
        ip_addr = ''
        begin = line.find("'IpAddr': u'")
        end = line.find("'", begin + 12)
        if begin != -1 and end != -1:
            ip_addr = line[begin + 12:end].decode('utf-8')

        match = re.search(r"'ComLicence': u'(.*?)'", line)
        if match:
            plate = match.group(1).decode('unicode-escape')
        if plate == '':
            match = re.search(r"'ComLicence2': u'(.*?)'", line)
            if match:
                plate = match.group(1).decode('unicode-escape')
        if plate == '':
            plate = u'无数据'
        begin = line.find("'ComTime': u'")
        end = line.find("'", begin + 13)
        if begin != -1 and end != -1:
            cap_time = line[begin + 13:end]
            return log_time, u'收到识别仪数据', {u'车牌': plate, u'识别仪地址': ip_addr,
                                          u'出场时间': datetime.datetime.strptime(cap_time, '%Y-%m-%d %H:%M:%S')}
    if "get fifo data ={'type': u'online_pay_at_outport'," in line:
        begin = line.find("'para': u'")
        end = line.find("'", begin + 10)
        if begin != -1:
            plate = str(line[begin + 10:end]).decode('unicode-escape')
        return log_time, u'线上支付，开始抬杆', None
    if 'init log success' in line:
        return log_time, u'进程启动', None
    elif '出口抬杆' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        return log_time, u'出口抬杆', {u'抬杆时间': datetime.datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f'),
                                   u'发送抬杆指令相机': vpr_ip}
    elif '出口发送语音' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        begin = line.find('#')
        return log_time, u'出口发送语音', {u'语音相机': vpr_ip}
    elif '出口led' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        return log_time, u'出口发送LED显示', {u'屏幕显示': vpr_ip}
    elif '应缴费=' in line:
        begin = line.find('=')
        price = ''
        end = len(line)
        if begin != -1:
            price = line[begin + 1:end]
        return log_time, u'计费结果', {u'应付金额': float(price) / 100}
    elif '本次出车类型' in line:
        match = re.search(r'''本次出车类型: (.*?) \[.*授权身份: (.*?) \[''', line)
        if match:
            out_auth = match.group(1).decode('utf-8')
            ori_auth = match.group(2).decode('utf-8')
            return log_time, u'出场授权', {u'出场授权': out_auth, u'原本授权': ori_auth}
    elif '停车时长 [stopping_time]:' in line:
        match = re.search(r'''停车时长 \[stopping_time\]:(.*)''', line)
        if match:
            park_time = int(match.group(1))
            return log_time, u'停车时长', {u'停车时长': park_time}
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
                return log_time, u'计费规则', {u'计费规则': rule_list}
    elif '是否跨时段叠加计费' in line:
        match = re.search(r'''cross_add\]: (.*)''', line)
        if match:
            is_cross = match.group(1)
            is_cross = True if is_cross == '1' else False
            return log_time, u'跨时段叠加', {u'跨时段叠加': is_cross}
    elif '入场记录[park_in_info]' in line:
        match = re.search(r'''in_time=(.*?),''', line)

        if match:
            in_time = match.group(1)
            return log_time, u'入场时间', {u'入场时间': datetime.datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')}
    elif 'Total running time calc_process' in line:
        match = re.search(r'''Total running time calc_process:(.*)''', line)
        if match:
            cost = float(match.group(1))
            return log_time, u'整体耗时', {u'耗时': cost}
    elif '已经支付的记录' in line:
        match = re.search(r'''charge_time': (.*?), '.*serial_no': u'(.*?)'.*pay_type': (.*?)L.*value': (.*?)L''', line)
        if match:
            charge_time = eval(match.group(1))
            serial_no = match.group(2).decode('utf-8')
            pay_type = match.group(3).decode('utf-8')
            pay_value = float(match.group(4)) / 100
            return log_time, u'历史支付', {u'历史支付时间': charge_time, u'历史订单号': serial_no, u'历史支付类型': pay_type,
                                       u'历史支付金额': pay_value}
    elif '入场记录[park_in_info]' in line:
        match = re.search(r'''in_time=(.*?),''', line)
        if match:
            in_time = datetime.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
            return log_time, u'入场时间', {u'入场时间': in_time}
    elif '大小车类型' in line:
        match = re.search(r'''大小车类型\[vehicle_type\]:(.*)''', line)
        if match:
            car_type = match.group(1).decode('utf-8')
            return log_time, u'大小车类型', {u'大小车类型': car_type}
    elif '能源类型' in line:
        match = re.search(r'''能源类型\[power_type\]:(.*)''', line)
        if match:
            power_type = match.group(1).decode('utf-8')
            return log_time, u'能源类型', {u'能源类型': power_type}
    elif '11: 分段计费' in line:
        charge_list = []
        for i in range(300):
            cur_line = lines[line_no + i]
            if '总费用 total_price' in cur_line:
                return log_time, u'计费详情', {u'计费详情': charge_list}
            match = re.search(r'''\] (.*?):.*time:\[(.*?)\] 费用charge\[(.*?)\]''', cur_line)
            if match:
                charge_type = match.group(1).decode('utf-8')
                charge_time = match.group(2)
                charge_start = charge_time.split(' ')[0] + ' ' + charge_time.split(' ')[1]
                charge_end = charge_time.split(' ')[2] + ' ' + charge_time.split(' ')[3]

                charge_value = float(match.group(3)) / 100
                charge_list.append((charge_type, datetime.datetime.strptime(charge_start, '%Y-%m-%d %H:%M:%S'),
                                    datetime.datetime.strptime(charge_end, '%Y-%m-%d %H:%M:%S'), charge_value))
    elif '获取出车预留时间' in line:
        match = re.search(r'''reserved_out_time\]:(.*)''', line)
        if match:
            reserved_time = int(match.group(1))
            return log_time, u'预留时间', {u'预留时间': reserved_time}
    elif 'SELECT vpr_plate FROM new_auth_share WHERE is_occupied=1' in line:
        match = re.search(r'''vpr_plate': u'(.*?)'}''', lines[line_no + 1])
        if match:
            auth_occupied = match.group(1).decode('unicode-escape')
            return log_time, u'授权占用', {u'授权占用车牌': auth_occupied}
    elif '授权生效时间=' in line:
        match = re.search(r'''授权生效时间=(.*?)\s(.*?)\s''', line)
        if match:
            auth_takeeffect_time = match.group(1) + ' ' + match.group(2)
            return log_time, u'授权生效时间', {
                u'授权生效时间': datetime.datetime.strptime(auth_takeeffect_time, '%Y-%m-%d %H:%M:%S')}
    elif '授权时段: [' in line:
        match = re.search(r'''授权时段：\[(.*)\]''')
        if match:
            pass
    elif 'SELECT * FROM pay_count' in line:
        return log_time, u'数据库查费时间', {u'数据库查费时间': datetime.datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f')}
    elif '出车记录id' in line:
        match = re.search(r'''park_out_id:(.*)''', line)
        if match:
            park_out_id = match.group(1).decode('utf-8')
            return log_time, u'出车记录id', {u'出车记录id': park_out_id}
    elif 'SELECT * FROM park_in WHERE id=' in line:
        match = re.search(r'''WHERE id=(.*)''', line)
        if match:
            park_in_id = match.group(1).decode('utf-8')
            return log_time, u'进车记录id', {u'进车记录id': park_in_id}


if __name__ == '__main__':
    import os

    os.chdir('../../../../')
    # conn, _ = frp.get_conn_new(u'凯德东')
    # tunnel, _ = make_tunnel(conn, '192.168.55.246')
    # with open(get_log(IRainLogType.PARK_OUT, datetime.date.today(), u'凯德东', ssh_client=tunnel), 'r') as f:
    with open(
            '/Users/shenbaihan/Documents/irain_tools_web/log_file/kaidedong/192.168.55.246/irain_park_out.log.2018-06-06',
            'r') as f:
        for every_record in parse_plate(f.readlines(), u'A00CU6'):
            for k, v in every_record.items():
                print k, v

    # print u'你' in u'我你他'
    # print '你' in '我你他'
    # print u'你' in '我你他'
    # print '你' in u'我你他'
