# coding: utf-8
import datetime
import json

from flask import request, jsonify
from src.frp.frp import frp
from src.job.job_system import jobsystem
from src.utils.quick import get_mysql_addr, execute_shell
from src.v3.problem_check.park_out_flow import ParkFlowJob


def park_flow_analyse():
    park_time = request.args.get('park_date')
    vpr_plate = request.args.get('vpr_plate')
    park_name = request.args.get('park_name')

    park_time = datetime.datetime.strptime(park_time, '%Y-%m-%d %H:%M:%S')

    j = ParkFlowJob(park_time, park_name, vpr_plate)
    jobsystem.run(j)
    return json.dumps({
        'code': 0,
        'msg': 'success',
        "task_id": j.job_id
    })


def park_records():
    park_date = request.args.get('park_date')
    vpr_plate = request.args.get('vpr_plate')
    park_name = request.args.get('park_name')

    park_date = datetime.datetime.strptime(park_date, '%Y-%m-%d').date()

    conn, ver = frp.get_conn(park_name)
    if not conn:
        return jsonify({
            'code': 1,
            'msg': 'Could not establish connection to %s' % park_name,
            'records': []
        })

    mysql_addr, _ = get_mysql_addr(conn)

    # vpr, terminal_ip, out_time
    all_records = []
    sql = """select d.out_used_plate, c.ip, d.in_time, d.out_time from depot_terminal as c join (select * from depot_site as a join (select out_used_plate, out_time, out_site_name, in_time from records_inout where out_time > '%s 00:00:00' and out_time < '%s 23:59:59' and out_used_plate='%s') as b on a.name = b.out_site_name) as d on c.id = d.terminal_id;""" % (
        str(park_date), str(park_date), vpr_plate)
    for r in execute_shell(conn, 'mysql -uroot -piraindb10241GB -h%s irain_park -sNe "%s"' % (mysql_addr, sql)):
        all_records.append(r.split('\t'))

    return jsonify({
        'code': 0,
        'msg': 'success',
        'records': [{'vpr': x[0], 'terminal_ip': x[1], 'out_time': x[3]} for x in all_records]
    })


if __name__ == '__main__':
    import os

    os.chdir('../../../')
    park_flow_analyse()
