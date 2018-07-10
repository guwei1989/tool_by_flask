# coding: utf-8
from multiprocessing.pool import ThreadPool
from threading import Lock

from src.frp.frp import frp
from src.job.job import LogType
from src.job.remote_script_job import RemoteScriptJob
from src.utils.quick import run_all_arm


def main(park_list):
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
            safe_log('%s self: miss' % info['name'])
            return
    except Exception, err:
        safe_log(str(err))
        return
    finally:
        if client:
            client.close()


def _v3(client, info):
    return _v2(client, info)


all_task = []


def _v2(client, info):
    all_task.append(info['name'])

    def task(ssh_client, ip, version):
        inner_j = RemoteScriptJob(ssh_client, 'static/scripts/llrp_info.py')
        inner_j.run()

        logs = []
        for j_log in inner_j.read_all():
            if j_log.log_type == LogType.INFO:
                logs.append(j_log.str.decode('utf-8'))

        safe_log('%s %s:%s' % (info['name'], ip, u';'.join(logs)))
        all_task.remove(info['name'])
        ssh_client.close()

    task(client, 'self', 3)
    # run_all_arm(client, task)


t_lk = Lock()


def safe_log(msg):
    t_lk.acquire()
    print msg
    log_f.write(('%s\n' % msg).encode('utf-8'))
    log_f.flush()
    t_lk.release()


if __name__ == '__main__':
    import os

    os.chdir('../../..')
    log_f = open('log.txt', 'w+')

    conns = frp.get_all_conn_info()
    conns = map(lambda x: x['name'], conns.values())

    main(conns)
    log_f.close()
