# coding=utf-8
import datetime
import re
import sys

from helper import start, end, info, err, traceback
from log_helper import read_log_lines, LogFile

ecoupon_lookup = {
    66: u'次数券',
    67: u'小时券',
    68: u'时间段券',
    69: u'金额券',
    70: u'折扣券',
    71: u'通用金额券'
}


def extract_park_info(lines, plate, out_datetime):
    # 过滤section时只过滤plate
    # 解析section时，根据解析结果 out_datetime再进行第二次过滤
    if not plate:
        return None

    # [ (lines[], parse_func)... ]
    sections = []

    # 0: undefined
    # 1: normal_out
    # 2: online_pay_at_outport
    # 3: pay_open
    # 4: update_plate
    section_type = 0

    vpr = ''

    # stack half-matched section start line num
    stack = []

    for l_no in range(len(lines)):
        line = lines[l_no]

        if '====begin' in line:
            stack.append(l_no)
        elif '====end' in line:
            if plate not in vpr or section_type == 0:
                stack.pop()
                vpr = ''
                section_type = 0
                continue
            elif section_type == 1 or section_type == 4:
                start_n = stack.pop()
                end_n = l_no + 1
                sections.append((lines[start_n:end_n], _normal_out))
            elif section_type == 2:
                start_n = stack.pop()
                end_n = l_no + 1
                sections.append((lines[start_n:end_n], _online_pay_at_outport))
            elif section_type == 3:
                start_n = stack.pop()
                end_n = l_no + 1
                sections.append((lines[start_n:end_n], _pay_open))
            section_type = 0
            vpr = ''
        elif "get fifo data ={'ComSpecial" in line:
            vpr_tmp = ''
            match = re.search(r"'ComLicence': u'(.*?)'", line)
            if match:
                vpr_tmp = match.group(1).decode('unicode-escape')
            else:
                match = re.search(r"'ComLicence2': u'(.*?)'", line)
                if match:
                    vpr_tmp = match.group(1).decode('unicode-escape')
            if vpr_tmp:
                section_type = 1
            vpr = vpr_tmp
        elif "get fifo data ={'type': u'update_plate'" in line:
            vpr_tmp = ''
            match = re.search(r"para': u'(.*?)'", line)
            if match:
                vpr_tmp = match.group(1).decode('unicode-escape')
            if vpr_tmp:
                section_type = 4
            vpr = vpr_tmp
        elif '当前出口车牌' in line:
            # online_pay_at_outport
            section_type = 2
            match = re.search(r"""当前出口车牌(.*)""", line)
            if match:
                vpr_tmp = match.group(1)
                if plate in vpr_tmp:
                    vpr = vpr_tmp
        elif '收费开闸流程' in line:
            # online_pay_at_outport
            section_type = 3
            match = re.search(r"""收费开闸流程 \[plate\] (.*?) \[""", line)
            if match:
                vpr_tmp = match.group(1)
                if plate in vpr_tmp:
                    vpr = vpr_tmp

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


def _normal_out(line, line_no, lines):
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
            return log_time, u'收到识别仪数据', {u'车牌': plate,
                                          u'出场时间': datetime.datetime.strptime(cap_time, '%Y-%m-%d %H:%M:%S')}
    if 'init log success' in line:
        return log_time, u'进程启动', None
    elif '出口抬杆' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        return log_time, u'出口抬杆', {u'抬杆时间': datetime.datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f'),
                                   u'抬杆透传相机': vpr_ip}
    elif '出口发送语音' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        begin = line.find('#')
        return log_time, u'出口发送语音', {u'语音透传相机': vpr_ip}
    elif '应缴费=' in line:
        begin = line.find('=')
        price = ''
        end = len(line)
        if begin != -1:
            price = line[begin + 1:end]
        return log_time, u'出口报费', {u'出口报费': float(price) / 100}
    elif '本次出车类型' in line:
        match = re.search(r'''本次出车类型: (.*?) \[.*授权身份: (.*?) \[''', line)
        if match:
            out_auth = match.group(1).decode('utf-8')
            ori_auth = match.group(2).decode('utf-8')
            return log_time, u'出场时授权', {u'出场时授权': out_auth, u'原本授权': ori_auth}
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
        match = re.search(
            r'''charge_time': (.*?), '.*serial_no': u'(.*?)'.*pay_type': (.*?)L.*value': (.*?)L.*charge_order_number': u'(.*?)'}''',
            line)
        if match:
            charge_time = eval(match.group(1))
            serial_no = match.group(2).decode('utf-8')
            pay_type = match.group(3).decode('utf-8')
            pay_value = float(match.group(4)) / 100
            charge_order_no = match.group(5).decode('utf-8')
            return log_time, u'历史支付', {u'历史支付时间': charge_time, u'历史支付订单': serial_no, u'历史支付类型': pay_type,
                                       u'历史支付金额': pay_value, u'历史计费订单': charge_order_no}
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
                return log_time, u'出口计费详情', {u'出口计费详情': charge_list}
            match = re.search(r'''\] (.*?):?.*time:?\[(.*?)\].*charge\[(.*?)\]''', cur_line)
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
    elif '在预留时间内足额支付了' in line:
        return log_time, u'出场方式', {u'出场方式': u'场内支付,预留时间内放行'}
    elif '获取电子券' in line:
        match = re.search(r'''获取电子券:(.*)''', line)
        if match:
            e_coupon_list_str = match.group(1)
            e_coupon_list = eval(e_coupon_list_str)
            return log_time, u'电子券', {u'电子券': [
                {u'券类型': ecoupon_lookup[x['e_type']] if x['e_type'] in ecoupon_lookup else u'未知%d' % x['e_type'],
                 u'备注': x['remarks'], u'券值': x['value']} for x in e_coupon_list]}


def _online_pay_at_outport(line, line_no, lines):
    log_time = line[:23]

    if '出口线上支付处理流程' in line:
        return log_time, u'出场方式', {u'出场方式': u'出口线上支付'}
    elif '出口抬杆' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        return log_time, u'出口抬杆', {u'抬杆时间': datetime.datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f'),
                                   u'抬杆透传相机': vpr_ip}


def _pay_open(line, line_no, lines):
    log_time = line[:23]

    if '收费开闸流程' in line:
        return log_time, u'出场方式', {u'出场方式': u'收费开闸'}
    elif '出口抬杆' in line:
        begin = line.find('ip:')
        end = line.rfind(' ')
        vpr_ip = u''
        if begin != -1:
            vpr_ip = line[begin + 3:end].decode('utf-8')
        return log_time, u'出口抬杆', {u'抬杆时间': datetime.datetime.strptime(log_time, '%Y-%m-%d %H:%M:%S,%f'),
                                   u'抬杆透传相机': vpr_ip}


def _update_plate(line, line_no, lines):
    r1, r2, r3 = _normal_out(line, line_no, lines)
    if (r1, r2, r3) != (None, None, None):
        return r1, r2, r3


def main():
    start()
    try:
        vpr = sys.argv[1]
        log_datetime = sys.argv[2]
        log_datetime = datetime.datetime.strptime(log_datetime, '%Y-%m-%d %H:%M:%S')

        lines = read_log_lines(LogFile.ParkOut, log_datetime.date())
        if not lines:
            raise Exception('Read nothing from log')
        park_info = extract_park_info(lines, vpr, log_datetime)

        if u'出场方式' not in park_info:
            if u'出口报费' in park_info and park_info[u'出口报费'] == 0:
                park_info[u'出场方式'] = u'自动抬杆出场'
            else:
                park_info[u'出场方式'] = u'未知'

        info(park_info.__repr__())
    except Exception, e:
        err('%s\n%s' % (str(e), traceback()))
    end()


if __name__ == '__main__':
    main()
