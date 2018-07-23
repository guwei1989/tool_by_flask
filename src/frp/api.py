# coding: utf-8
import json

from src.frp.llrp import frp


def frp_list():
    conns = frp.get_all_conn_info()
    re = [x for x in set([x['name'] for x in conns.values()])]
    return json.dumps(re)