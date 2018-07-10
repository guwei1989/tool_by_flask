# coding: utf-8
from multiprocessing.pool import ThreadPool
from threading import RLock
from src.job.job import LogType
from src.frp.frp import frp
import traceback

from src.job.remote_script_job import RemoteScriptJob
from src.utils.quick import run_all_arm

log_lock = RLock()


def deploy(park_list):
    all_conns = {k: v for k, v in {x: frp.get_conn_info(x) for x in park_list}.items() if v is not None}

    all_conns = all_conns.values()
    all_conns.reverse()

    pool = ThreadPool(100)

    pool.map(_handle_one_park, all_conns)
    pool.close()
    pool.join()


def _handle_one_park(info):
    client = None
    try:
        client, version = frp.get_conn(info['name'])
        if version == 3:
            _v3(client, info)
        elif version == 2:
            _v2(client, info)
        else:
            log(('MISS %s\n' % info['name']).encode('utf-8'))
            return
    except Exception, err:
        log(
            ('FAIL %s %s %s\n' % (info['name'], str(err), traceback.format_exc().replace('\n', ' '))).encode(
                'utf-8'))
        return
    finally:
        if client:
            client.close()
    log(('GOOD %s\n' % info['name']).encode('utf-8'))


def _v3(client, info):
    def task(ssh_client, ip, version):
        try:
            print 'trying ', info['name'], ' ', ip
            inner_j = RemoteScriptJob(ssh_client, 'static/scripts/llrp_install.py')
            inner_j.run()
            for j_log in inner_j.read_all():
                if j_log.log_type == LogType.INFO:
                    pass
            ssh_client.close()
        except Exception, err:
            print info['name'], ' ', ip, str(err), traceback.format_exc()

    run_all_arm(client, task)


def _v2(client, info):
    return _v3(client, info)


def log(msg):
    print msg
    handle_f.write(msg)
    handle_f.flush()


def str_similarity(str_a, str_b, w_tb_a):
    l_a = [w_tb_a[x] if x in w_tb_a and x in str_b else 0 for x in str_a]
    l_b = [w_tb_a[x] if x in w_tb_a and x in str_a else 0 for x in str_b]

    v_a = reduce(lambda a, b: a + b, l_a) / len(l_a)
    v_b = reduce(lambda a, b: a + b, l_b) / len(l_b)

    v = v_a * v_b
    return v


if __name__ == '__main__':
    import os

    os.chdir('../../..')

    # conns = frp.get_all_conn_info()
    # conns = map(lambda x: x['name'], conns.values())

    handle_f = open('records.txt', 'w+')

    with open('log.txt', 'r') as f:
        lines = f.readlines()
        filtered = [line.split(' ')[0] for line in lines if 'fail' in line]

    deploy(['西安御城龙脉南区'])

    handle_f.close()
