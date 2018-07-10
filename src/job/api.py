# coding: utf-8
from flask import request
from flask.json import jsonify

from job_system import jobsystem
import json


def task_new_logs():
    job_id = request.args.get('task_id')
    j = jobsystem.get_job(job_id)

    if j is None:
        return json.dumps({
            'code': 1,
            'result': 'Job not exist'
        })

    logs = j.read(False)
    progress = j.progress()

    return jsonify({
        'code': 0,
        'result': 'success',
        'logs': [{'progress': lg.progress, 'time': str(lg.time), 'log_type': lg.log_type.name, 'msg': lg.str,
                  'value': lg.value} for lg in logs],
        'progress': progress
    })
