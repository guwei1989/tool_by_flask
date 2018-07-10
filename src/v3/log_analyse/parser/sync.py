# coding=utf-8
from Queue import Queue
from section import Section
import re


def parse(lines):
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
            ip_addr = line[begin + 12:end]

        plate_match = re.search(r"'ComLicence': u'(.*?)'", line)
        if plate_match is not None:
            plate = plate_match.group(1).decode('unicode-escape')
        if plate == '':
            plate_match = re.search(r"'ComLicence2': u'(.*?)'", line)
            if plate_match is not None:
                plate = plate_match.group(1).decode('unicode-escape')
        if plate == '':
            plate = u'无数据'
        begin = line.find("'ComTime': u'")
        end = line.find("'", begin + 13)
        if begin != -1 and end != -1:
            cap_time = line[begin + 13:end]
            return log_time, u'收到识别仪数据', {u'车牌': plate, u'识别仪地址': ip_addr, u'图像捕捉时间': cap_time}
    if "get fifo data ={'type': u'online_pay_at_outport'," in line:
        # status = u'出车'
        # plate = ''
        begin = line.find("'para': u'")
        end = line.find("'", begin + 10)
        if begin != -1:
            plate = str(line[begin + 10:end]).decode('unicode-escape')
        return log_time, u'线上支付，开始抬杆', None
    if 'init log success' in line:
        return log_time, u'进程启动', None
    elif u'出口抬杆'.encode('utf-8') in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = ''
        if begin != -1:
            vpr_ip = line[begin + 3:end]
        begin = line.find('#')
        return log_time, u'出口抬杆', {u'发送指令相机IP': vpr_ip}
    elif u'出口发送语音'.encode('utf-8') in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = ''
        if begin != -1:
            vpr_ip = line[begin + 3:end]
        begin = line.find('#')
        return log_time, u'出口发送语音', {u'发送指令相机IP': vpr_ip}
    elif u'出口led'.encode('utf-8') in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = ''
        if begin != -1:
            vpr_ip = line[begin + 3:end]
        begin = line.find('#')
        return log_time, u'出口发送LED显示', {u'发送指令相机IP': vpr_ip}
    elif u'应缴费='.encode('utf-8') in line:
        begin = line.find('=')
        price = ''
        end = len(line)
        if begin != -1:
            price = line[begin + 1:end]
        return log_time, u'计费结果', {u'金额': float(price) / 100}
    elif u'本次出车类型: '.encode('utf-8') in line:
        re_auth_pattern = re.search(r'''本次出车类型: (.*?)\[(.*?)授权身份: (.*?) \[''', line)
        if re_auth_pattern is not None:
            current_park_auth_type = line[re_auth_pattern.regs[1][0]: re_auth_pattern.regs[1][1]].decode(
                'utf-8')
            auth_type = line[re_auth_pattern.regs[3][0]: re_auth_pattern.regs[3][1]].decode('utf-8')
            return log_time, u'出车授权身份', {u'原本授权身份': auth_type, u'本次身份': current_park_auth_type}
    elif u'大小车类型'.encode('utf-8') in line:
        re_car_type_pattern = re.search(r'''vehicle_type\]:(.*?) 是否军警车\[police_flag\]:(.*)''', line)
        if re_car_type_pattern is not None:
            car_type = line[re_car_type_pattern.regs[1][0]: re_car_type_pattern.regs[1][1]].decode('utf-8')
            police_car_flag = line[re_car_type_pattern.regs[2][0]: re_car_type_pattern.regs[2][1]].decode(
                'utf-8')
            return log_time, u'车型判断', {u'车型': car_type, u'是否军警车': u'否' if u'False' in police_car_flag else u'是'}
    elif u'停车时长 [stopping_time]:'.encode('utf-8') in line:
        re_park_time_parttern = re.search(r'''停车时长 \[stopping_time\]:(.*)''', line)
        if re_park_time_parttern is not None:
            park_time = re_park_time_parttern.group(1).decode('utf-8')
            return log_time, u'停车时长', {u'时长/秒': park_time}
    elif u'8: 历史计费总额'.encode('utf-8') in line:
        re_prepay_pattern = re.search(r'''历史付费的总金额 \[history_total_price\]:(.*)''', lines[line_no + 2])
        prepay_amount = 0
        if re_prepay_pattern is not None:
            prepay_str = re_prepay_pattern.group(1).decode(
                'utf-8')
            prepay_amount = float(prepay_str) / 100
        return log_time, u'到出口前付费历史', {u'金额/元': prepay_amount}
    elif u'计费产生计费订单号'.encode('utf-8') in line:
        pay_order_pattern = re.search(r'''自动生成订单号 \[charge order number\]:(.*)''',
                                      lines[line_no + 2])
        if pay_order_pattern is not None:
            order_number = pay_order_pattern.group(1).decode(
                'utf-8')
            return log_time, u'计费订单号', {u'订单号': order_number}
    elif u'9: 预留时间参数'.encode('utf-8') in line:
        reserved_time_pattern = re.search(r'''获取出车预留时间 \[reserved_out_time\]:(.*)''',
                                          lines[line_no + 4])
        if reserved_time_pattern is not None:
            reserved_time_str = reserved_time_pattern.group(1).decode(
                'utf-8')
            return log_time, u'出车预留时长', {u'时长/秒': reserved_time_str}
    elif u'12: 计费规则'.encode('utf-8') in line:
        rule_list = []
        for i in range(40):
            charge_rule_pattern = re.search(r'''计费模板:(.*) priority''',
                                            lines[line_no + i])
            if charge_rule_pattern is not None:
                charge_rule = lines[line_no + i][
                              charge_rule_pattern.regs[1][0]: charge_rule_pattern.regs[1][1]].decode(
                    'utf-8')
                rule_list.append(charge_rule)
        return log_time, u'计费规则', {u'规则': u'-'.join(rule_list)}
