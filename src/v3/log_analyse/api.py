# coding: utf-8
import datetime
import json
from flask import request, jsonify
from src.job.job_system import jobsystem
from src.frp.frp import frp
from src.v3.log_analyse.park_out_analyse import ParkOutAnalyseJob


def log_parse():
    if "park_name" in request.form:
        current_ip = request.args.get("current_ip")
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        ip = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh = frp.get_conn(host=ip, port=port)
    if ssh is None:
        return jsonify({'code': 1, 'msg': '无法连接目标，当前暂不支持v2版本'}), 500

    log_type = request.form.get('log_type')
    log_date = request.form.get('datetime_start')
    log_date = datetime.datetime.strptime(log_date, '%Y-%m-%d').date()

    job_map = {
        u'出车': ParkOutAnalyseJob
    }

    if log_type not in job_map:
        return json.dumps({'code': 1, 'result': '%s 不是合法的日志类型' % log_type})

    job_cls = job_map[log_type]

    j = job_cls()
    jobsystem.add_job(j)
    jobsystem.start_pool_job(j.job_id, (park_name, log_date, ssh, False))

    return json.dumps({'code': 0, 'result': 'success', 'task_id': j.job_id})
