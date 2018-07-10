# coding: utf-8
from src.frp.frp import frp
from src.job.remote_script_job import RemoteScriptJob


def deploy(park_list):
    for p_name in park_list:
        _handle_one_park(p_name)


def _handle_one_park(p_name):
    client = None
    try:
        client, version = frp.get_conn(p_name)
        if version == 3:
            _v3(client, p_name)
        elif version == 2:
            print 'impossible v2'
        else:
            print 'impossible v?'
            return
    except Exception, err:
        return
    finally:
        if client:
            client.close()


def _v3(client, p_name):
    j = RemoteScriptJob(client, 'static/scripts/3500bugfix.py')
    j.run()
    for output in j.read_all():
        if output.str == 'ok':
            print p_name, ' is ok'
            return
    print p_name, ' is wrong'


if __name__ == '__main__':
    import os

    os.chdir('../../..')

    deploy(['成都上锦雅筑停车场', '成都索菲斯民族酒店', '成都青羊工业园D区地面', '成都青羊工业园B区地面', '成都上城花园地面',
            '成都上城花园地库', '成都聚能国际', '成都珠峰大酒店', '成都蜀都中心二期', '成都胜利家园', '成都开新家园B区',
            '成都开新家园A区', '东方广场商业中心', '东方广场二期', '东方广场一期'])
