# coding: utf-8
import json
import requests
import requests.auth
import paramiko
import time

from paramiko import SSHException


class LLRPManager(object):
    def __init__(self, host, port, auth_token, self_ip):
        self.host = host
        self.port = port
        self.token = auth_token
        self.ip = self_ip

        self.clients_url = 'http://%s:%d/api/clients' % (host, port)
        self.auth_url = 'http://%s:%d/api/client/auth/%s' % (host, port, auth_token)

        self._conns_cache = None
        self._conn_cache_time = 0
        self._cache_expiration = 3600

    def get_all_conn_info(self):
        if time.time() - self._conn_cache_time < self._cache_expiration:
            return self._conns_cache

        r = requests.get(self.clients_url)
        re = {}

        proxies = json.loads(r.text)
        for proxy in proxies:
            info = {
                'name': proxy['Name'],
                'host': self.host,
                'id': proxy['Id'],
                'runId': proxy['RunId']
            }
            re[info['id']] = info

        self._conns_cache = re
        self._conn_cache_time = time.time()
        return re

    def get_conn_info(self, con_name):
        if not con_name:
            return None
        if not isinstance(con_name, unicode):
            con_name = con_name.decode('utf-8')

        conns = self.get_all_conn_info()
        for conn in conns.values():
            if conn['name'] == con_name:
                return conn

        return None

    def _llrp_auth(self, client_id):
        r = requests.post(self.auth_url, json=[{
            'client_id': client_id,
            'forward_port': 22,
            'user_ip': self.ip
        }], headers={'Content-Type': 'application/json'})
        return r.json()

    def get_conn(self, conn_name):
        # return SSHClient, int_version

        # if conn_name in self.conn_pool:
        #     return self.conn_pool[conn_name][0]

        conn_info = self.get_conn_info(conn_name)
        if not conn_info:
            return None, None

        auth_info = self._llrp_auth(conn_info['id'])

        if not auth_info:
            return None, None

        try:
            return try_login(auth_info[0]['server_ip'], auth_info[0]['server_port'])
        except SSHException:
            return None, None


def try_login(host=None, port=22):
    # return (SSHClient, int_version) or (None, None) if neither v2 nor v3
    # both ip:port and ssh_tunnel are supported
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        conn.connect(hostname=host, port=port, username="root", password="iraindev10241GB", timeout=30)
        return conn, 3
    except paramiko.AuthenticationException:
        try:
            conn.connect(hostname=host, port=port, username="root", password="123456", timeout=30)
            return conn, 2
        except paramiko.AuthenticationException:
            pass

    return None, None


frp = LLRPManager('120.26.7.171', 6161, '56ca0d4773a92891d2d6418bdb2a6ed5', '121.199.49.228')

if __name__ == '__main__':
    sp = LLRPManager('120.26.7.171', 6161, '56ca0d4773a92891d2d6418bdb2a6ed5', '113.132.180.233')
    print sp.get_all_conn_info()
    print sp.get_conn('天领国际大厦停车场')
