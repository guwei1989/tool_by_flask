# coding: utf-8
import json
from flask import request
from src.frp.frp import frp


def frp_list():
    conns = frp.get_all_conn_info()
    re = [x['name'] for _, x in conns.items()]
    return json.dumps(re)


def get_frp_auth():
    if "park_name" in request.form:
        park_name = request.form.get("park_name")
        user_ip = request.remote_addr
        if frp.frp_auth(park_name, user_ip):
            return json.dumps({
                "Code": 0
            })

    return json.dumps({
        "Code": 1
    })
