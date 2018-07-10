# coding: utf-8
import json
import os
import time
from flask import request, jsonify
from src.job.job import LogType
from src.job.remote_script_job import RemoteScriptJob
from src.frp.frp import frp
from src.frp.frp import try_login
from src.utils.quick import make_tunnel
from sys_status import cpu_usage, mem_usage, net_inout_bytes, disk_usage


def api_cpu_usage():
    if "park_name" in request.args:
        current_ip = request.args.get("current_ip")
        conn, _ = frp.get_conn(request.args.get('park_name'))
        ssh, _ = make_tunnel(conn, current_ip)
    else:
        host = request.args.get('hostname')
        port = int(request.args.get('port'))
        ssh, _ = try_login(host=host, port=port)
    percentage = cpu_usage(ssh)
    return jsonify({
        "timestamp": int(time.time()),
        "usage": percentage
    })


def api_mem_usage():
    if "park_name" in request.args:
        current_ip = request.args.get("current_ip")
        conn, _ = frp.get_conn(request.args.get('park_name'))
        ssh, _ = make_tunnel(conn, current_ip)
    else:
        host = request.args.get('hostname')
        port = int(request.args.get('port'))
        ssh, _ = try_login(host=host, port=port)
    usage = mem_usage(ssh)
    return jsonify({
        "timestamp": int(time.time()),
        "usage": float(usage[0]) / usage[1]
    })


def api_disk_usage():
    if "park_name" in request.args:
        current_ip = request.args.get("current_ip")
        conn, _ = frp.get_conn(request.args.get('park_name'))
        ssh, _ = make_tunnel(conn, current_ip)
    else:
        host = request.args.get('hostname')
        port = int(request.args.get('port'))
        ssh, _ = try_login(host=host, port=port)
    usage = disk_usage(ssh)
    return jsonify({
        "timestamp": int(time.time()),
        "usage": usage
    })


def api_net_usage():
    if "park_name" in request.args:
        current_ip = request.args.get("current_ip")
        conn, _ = frp.get_conn(request.args.get('park_name'))
        ssh, _ = make_tunnel(conn, current_ip)
    else:
        host = request.args.get('hostname')
        port = int(request.args.get('port'))
        ssh, _ = try_login(host=host, port=port)
    usage = net_inout_bytes(ssh)
    return jsonify({
        "timestamp": int(time.time()),
        "inbound": usage[0],
        "outbound": usage[1]
    })


def api_get_arm_ip_list():
    park_name = request.args.get("park_name")
    try:
        conn, version = frp.get_conn(park_name)
        if version == 3:
            path = os.path.join('static', 'scripts', 'get_all_arm_ip.py')
            job = RemoteScriptJob(conn, path)
            job.run()
            ip_list = []

            for out_put in job.read_all():
                if out_put.log_type == LogType.INFO:
                    ip_list.append(out_put.str.strip())
            return json.dumps({"result": ip_list})
        else:
            return json.dumps({"code": 1, "result": u'不支持v2车场'})
    except Exception as e:
        return json.dumps({"result": str(e)})


def api_all_arm_restart():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        ssh, _ = frp.get_conn(conn_name=park_name)
        if "current_ip" in request.form:
            current_ip = request.form.get("current_ip")
            ssh, _ = make_tunnel(ssh, current_ip)
            _, stdout, _ = ssh.exec_command("cd /home/park;sh restart.sh")
            return json.dumps({"result": 0})
    else:
        host = request.form.get('hostname')
        port = int(request.form.get('port'))
        ssh, _ = try_login(host=host, port=port)
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                            "static", "scripts", "all_arm_restart.py")
        job = RemoteScriptJob(ssh, path)
        job.run()

        for out_put in job.read_all():
            if "success" in out_put.str:
                return json.dumps({"result": 0})
        return json.dumps({"result": 1})
    except Exception as e:
        return json.dumps({"result": str(e)})
