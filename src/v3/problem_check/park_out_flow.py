# coding: utf-8
from pytz import timezone

from src.frp.frp import frp
from src.job.job import Job, JobLog, LogType
from src.utils.quick import get_mysql_addr, execute_shell, get_all_terminal_ip, run_script, make_tunnel
import datetime

from src.v3.helper.helper import park_records, cloud_terminal


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
            # arm returns datetime with GTM timezone
            # change timezone to local timezone
            tz = timezone('Asia/Shanghai')
            for k, v in value.items():
                if isinstance(v, datetime.datetime):
                    value[k] = tz.localize(v)
                elif k == u'出口计费详情':
                    value[k] = [(x[0], tz.localize(x[1]), tz.localize(x[2]), x[3]) for x in v]
            park_info.update(value)

        tz = timezone('Asia/Shanghai')

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
                                value[k] = tz.localize(v)
                            elif k == u'历史计费详情':
                                value[k] = [(x[0], tz.localize(x[1]), tz.localize(x[2]), x[3]) for x in v]
                        park_info.update(value)
                    sync_arm_tunnel.close()

        p_r = park_records(tunnel, self.vpr, self.park_time.date())
        r = filter(lambda x: x[5] == str(self.park_time), p_r)[0]

        cloud_tml = cloud_terminal(tunnel)
        cloud_tunnel, _ = make_tunnel(tunnel, cloud_tml)

        # 进出车上报情况
        for log in run_script(cloud_tunnel, 'static/scripts/sync_inout_extract.py', (r[2], )):
            value = eval(log.str)
            for k, v in value.items():
                if isinstance(v, datetime.datetime):
                    value[k] = tz.localize(v)
            park_info.update(value)

        self._info(JobLog(99, LogType.INFO, self.park_time, u'park_flow', park_info))

        self._p_end()

        tunnel.close()
        cloud_tunnel.close()
