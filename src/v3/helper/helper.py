# coding: utf-8
from src.utils.quick import execute_shell, get_mysql_addr


def run_sql(ssh_client, sql):
    all_records = []

    mysql_addr, _ = get_mysql_addr(ssh_client)

    for r in execute_shell(ssh_client, 'mysql -uroot -piraindb10241GB -h%s irain_park -sNe "%s"' % (mysql_addr, sql)):
        all_records.append(r)

    return all_records


def park_records(ssh_client, vpr, park_date):
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
    sql = """select d.out_used_plate, c.ip, d.park_in_id, d.in_time, d.park_out_id, d.out_time from depot_terminal as c join (select * from depot_site as a join (select out_used_plate, out_time, out_site_name, in_time, park_in_id, park_out_id from records_inout where out_time > '%s 00:00:00' and out_time < '%s 23:59:59' and out_used_plate='%s') as b on a.name = b.out_site_name) as d on c.id = d.terminal_id;""" % (
        str(park_date), str(park_date), vpr)

    all_records = []

    for r in run_sql(ssh_client, sql):
        all_records.append(tuple(r.split('\t')))

    return all_records


def cloud_terminal(ssh_client):
    """
    :return
        '192.168.55.248'
    """
    sql = "select value from project_conf where name = 'terminal_operator'"

    for r in run_sql(ssh_client, sql):
        return r.strip()
