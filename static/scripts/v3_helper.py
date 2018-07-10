# coding: utf-8
from helper import get_mysql_addr, l_exec_cmd


def park_records(vpr, park_date):
    """
    vpr: full_name
    type(park_datetime) = datetime.date
    return:
        [
              0         1           2           3           4           5
            (vpr, terminal_ip, park_in_id, in_time_str, park_out_id, out_time_str),
            ...
        ]
    """
    sql = """select d.out_used_plate, c.ip, d.park_in_id, d.in_time, d.park_out_id, d.out_time from depot_terminal as c join (select * from depot_site as a join (select out_used_plate, out_time, out_site_name from records_inout where out_time > '%s 00:00:00' and out_time < '%s 23:59:59' and out_used_plate='%s') as b on a.name = b.out_site_name) as d on c.id = d.terminal_id;""" % (
        str(park_date), str(park_date), vpr)

    all_records = []

    for r in run_sql(sql):
        all_records.append(r.split('\t'))

    return all_records


def run_sql(sql):
    ms_addr, _ = get_mysql_addr()
    sql_cmd = 'mysql -uroot -piraindb10241GB -h%s irain_park -sNe "%s"' % (ms_addr, sql)
    return [r for r in l_exec_cmd(sql_cmd)]
