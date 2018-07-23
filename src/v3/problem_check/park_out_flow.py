# coding: utf-8
import datetime

from src.frp.llrp import frp
from src.job.job import Job, JobLog, LogType
from src.utils.quick import get_mysql_addr, execute_shell, get_all_terminal_ip, run_script, make_tunnel
from src.v3.helper.helper import park_records, cloud_terminal

mapping = {
    u'车牌': u'vpr',
    u'出场时间': u'out_time',
    u'抬杆时间': u'open_time',
    u'抬杆透传相机': u'open_vpr',
    u'语音透传相机': u'voice_vpr',
    u'出口报费': u'price',
    u'出场时授权': u'cur_auth',
    u'原本授权': u'ori_auth',
    u'停车时长': u'park_duration',
    u'计费规则': u'charge_rule',
    u'跨时段叠加': u'corss_overlap',
    u'耗时': u'out_cost',
    u'历史支付时间': u'history_pay_time',
    u'历史支付订单': u'history_pay_no',
    u'历史支付类型': u'history_pay_type',
    u'历史支付金额': u'history_pay_amount',
    u'历史计费订单': u'history_charge_no',
    u'入场时间': u'in_time',
    u'大小车类型': u'car_size_type',
    u'能源类型': u'energy_type',
    u'出口计费详情': u'out_charge_detail',
    u'预留时间': u'reserve_time',
    u'授权占用车牌': u'auth_occupy_vpr',
    u'授权生效时间': u'auth_takeeffect_time',
    u'数据库查费时间': u'db_charge_lookup_time',
    u'出车记录id': u'park_out_id',
    u'进车记录id': u'park_in_id',
    u'出场方式': u'out_type',
    u'电子券': u'ecoupon',
    u'券类型': u'ecoupon_type',
    u'备注': u'ecoupon_mark',
    u'券值': u'ecoupon_value',
    u'历史计费规则': u'history_charge_rule',
    u'历史计费详情': u'history_charge_detail',
    u'历史计费结果': u'history_charge_amount',
    u'数据库写费时间': u'db_charge_insert_time',
    u'入场记录上报时间': u'in_upload_time',
    u'出场记录上报时间': u'out_upload_time'
}


class ParkFlowJob(Job):
    def __init__(self, park_time, park_name, vpr):
        Job.__init__(self)
        self.park_time = park_time
        self.park_name = park_name
        self.vpr = vpr

    def run(self):
        self._p_start()
        # get park_out record within park_date
        conn, ver = frp.get_conn(self.park_name)

        if ver == 2:
            self._info(JobLog(99, LogType.INFO, self.park_time, u'non 3399 not support yet', None))
            self._p_end()
            return

        mysql_addr, _ = get_mysql_addr(conn)

        # vpr, terminal_ip, out_time
        record = None
        sql = """select d.out_used_plate, c.ip, d.out_time from depot_terminal as c join (select * from depot_site as a join (select out_used_plate, out_time, out_site_name from records_inout where out_time = '%s' and out_used_plate='%s') as b on a.name = b.out_site_name) as d on c.id = d.terminal_id;""" % (
            str(self.park_time), self.vpr)
        for r in execute_shell(conn, 'mysql -uroot -piraindb10241GB -h%s irain_park -sNe "%s"' % (mysql_addr, sql)):
            record = r.split('\t')
            break

        terminal_ip = record[1]
        tunnel, _ = make_tunnel(conn, terminal_ip)

        park_info = {}

        for log in run_script(tunnel, 'static/scripts/park_info_extract.py', (self.vpr, '"%s"' % self.park_time)):
            value = eval(log.str)
            for k, v in value.items():
                if isinstance(v, datetime.datetime):
                    value[k] = str(v)
                elif k == u'出口计费详情':
                    value[k] = [(x[0], str(x[1]), str(x[2]), x[3]) for x in v]
            park_info.update(value)

        # 场内支付情况
        if u'历史计费订单' in park_info:
            charge_no = park_info[u'历史计费订单']

            all_arm = get_all_terminal_ip(conn)
            for arm_ip in all_arm:
                squeeze_ip = arm_ip.replace('.', '')
                if charge_no.find(squeeze_ip) == 0:
                    sync_arm_tunnel, _ = make_tunnel(conn, arm_ip)

                    for log in run_script(sync_arm_tunnel, 'static/scripts/idata_info_extract.py',
                                          (charge_no, '"%s"' % self.park_time.date())):
                        value = eval(log.str)

                        for k, v in value.items():
                            if isinstance(v, datetime.datetime):
                                value[k] = str(v)
                            elif k == u'历史计费详情':
                                value[k] = [(x[0], str(x[1]), str(x[2]), x[3]) for x in v]
                        park_info.update(value)
                    sync_arm_tunnel.close()

        p_r = park_records(tunnel, self.vpr, self.park_time.date())
        r = filter(lambda x: x[5] == str(self.park_time), p_r)[0]

        cloud_tml = cloud_terminal(tunnel)
        cloud_tunnel, _ = make_tunnel(tunnel, cloud_tml)

        # 进出车上报情况
        for log in run_script(cloud_tunnel, 'static/scripts/sync_inout_extract.py', (r[2],)):
            value = eval(log.str)
            for k, v in value.items():
                if isinstance(v, datetime.datetime):
                    value[k] = str(v)
            park_info.update(value)

        for k, v in park_info.items():
            if k not in mapping:
                continue
            new_k = mapping[k]
            park_info[new_k] = v
            del park_info[k]

        self._info(JobLog(99, LogType.INFO, self.park_time, u'park_flow', park_info))

        self._p_end()

        tunnel.close()
        cloud_tunnel.close()
