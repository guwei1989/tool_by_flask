# coding: utf-8
import json
import os
import time
from flask import request
from src.job.job_system import jobsystem
from src.job.remote_script_job import RemoteScriptJob
from src.frp.frp import frp
from src.frp.frp import try_login
from src.v3.data_maintain.health_check import HealthCheckJob
import traceback
from src.utils.quick import run_all_arm


def all_arm_health_check():
    if "park_name" in request.form:
        park_name = request.form.get('park_name')
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    try:
        j = HealthCheckJob(ssh)
        jobsystem.add_job(j)
        jobsystem.run(j.job_id)
    except Exception, e:
        return json.dumps({"code": 1, "result": str(e)})
    return json.dumps({"code": 0, "result": "success", "task_id": j.job_id})


def inside_records_export():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    end_time = str(request.form.get('end_time'))
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "inside_records_export.py")
        job = RemoteScriptJob(ssh, path)
        job.run((end_time,))

        for out_put in job.read_all():
            if "FilePath" in out_put.str:
                f_path = out_put.str[10:]
                sftp = ssh.open_sftp()
                tool_run_time = time.strftime('%Y%m%d_%H%M%S', time.localtime())
                l_path = 'static/download/inside_records_%s.xlsx' % str(tool_run_time)
                sftp.get(f_path, l_path)
                return json.dumps({"result": 0, "download_url": l_path})
        return json.dumps({"result": 1})
    except Exception as e:
        return json.dumps({"result": str(e)})


def delete_inside_records():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    end_time = str(request.form.get('end_time'))
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "inside_records_del.py")
        job = RemoteScriptJob(ssh, path)
        jobsystem.run(job, (end_time,))

        for out_put in job.read_all():
            if "success" in out_put.str:
                return json.dumps({"result": 0})
        return json.dumps({"result": 1})
    except Exception as e:
        return json.dumps({"result": str(e)})


def reduce_auth_show_time():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "reduce_auth_show_time.py")
        job = RemoteScriptJob(ssh, path)
        jobsystem.run(job)

        for out_put in job.read_all():
            if "success" in out_put.str:
                return json.dumps({"result": 0})
        return json.dumps({"result": 1})

    except Exception as e:
        return json.dumps({"result": str(e)})


def extend_auth_time():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "set_more_validity_time.py")
        job = RemoteScriptJob(ssh, path)
        jobsystem.run(job)

        for out_put in job.read_all():
            if "success" in out_put.str:
                return json.dumps({"result": 0})
        return json.dumps({"result": 1})
    except Exception as e:
        return json.dumps({"result": str(e)})


def db_backup():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "v3_db_backup.py")
        j = jobsystem.create_rs_job(ssh, path)
        jobsystem.run(j)
        while not jobsystem.is_finished(j):
            time.sleep(1)
    except Exception, e:
        return json.dumps({"code": 1, "result": str(e)})
    return json.dumps({"code": 0, "result": "success", "task_id": j.job_id})


def mod_abnormal_inout_num():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    abnormal_num = request.form.get("abnormal_num")
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "abnormal_inout_num_mod.py")
        job = RemoteScriptJob(ssh, path)
        jobsystem.run(job, (abnormal_num,))

        for out_put in job.read_all():
            if "success" in out_put.str:
                return json.dumps({"result": 0})
        return json.dumps({"result": 1})
    except Exception as e:
        return json.dumps({"result": str(e)})


def file_upload():
    file = request.files.get("file")
    upload_path = request.form.get("path")
    version = request.form.get("version")
    file_name = file.filename

    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh = frp.get_conn(conn_name=park_name)
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)

    replace_path = "/usr/local/lib/python2.7/dist-packages/irain_park-%s-py2.7.egg%s" % (version, upload_path)

    def work(ssh_tunnel, ip, verison):
        ssh_tunnel.exec_command("cd %s;mv %s %s_old" % (replace_path, file_name, file_name))
        sftp = ssh_tunnel.open_sftp()
        sftp.putfo(file, replace_path + "/%s" % file_name, file_size=10248)

    try:
        run_all_arm(ssh, work)
    except Exception as e:
        return json.dumps("restart failuer: %s\n%s" % (e, traceback.format_exc()))
    return json.dumps({"result": 0})
