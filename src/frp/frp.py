# coding: utf-8
import json
import requests
import requests.auth
import paramiko
import time

from paramiko import SSHException


class FrpManager:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.api_url = 'http://%s:%d/api/proxy/tcp' % (host, port)
        self._conn_info_cache = None
        self._conn_info_cache_time = 0
        self.request_expire_time = 3600

        self.conn_pool = {}

    def get_all_conn_info(self):
        if time.time() - self._conn_info_cache_time < self.request_expire_time:
            return self._conn_info_cache

        r = requests.get(self.api_url, auth=requests.auth.HTTPBasicAuth(self.username, self.password))
        re = {}

        proxies = json.loads(r.text)['proxies']
        for proxy in proxies:
            if proxy['status'] == 'offline' \
                    or proxy['name'].find('_web') != -1 \
                    or proxy['name'].find('picture_') != -1:
                continue
            conn = {
                'name': proxy['name'].replace('_ssh', ''),
                'host': self.host,
                'port': proxy['conf']['remote_port'],
                'runID': proxy['conf']['RunId'] if ('conf' in proxy and 'RunId' in proxy['conf']) else '0'
            }
            re[conn['name']] = conn

        self._conn_info_cache = re
        self._conn_info_cache_time = time.time()
        return re

    def get_conn_info(self, conn_name):
        if not conn_name:
            return None
        conns = self.get_all_conn_info()
        if not isinstance(conn_name, unicode):
            conn_name = conn_name.decode('utf-8')
        if conn_name in conns:
            return conns[conn_name]
        return None

    def frp_auth(self, name, user_ip):
        all_conns = self.get_all_conn_info()
        for index, conn in all_conns.items():
            if name == conn["name"]:
                try:
                    result = requests.post('http://%s:%d/api/proxy/access_records' % (conn["host"], self.port),
                                           data={"runID": conn["runID"], "ip": user_ip})
                    re = json.loads(result.content)
                except Exception:
                    return False

                if re['code'] == 0:
                    return True
        return False

    def get_conn(self, conn_name):
        # return SSHClient, int_version

        # if conn_name in self.conn_pool:
        #     return self.conn_pool[conn_name][0]

        conn_info = self.get_conn_info(conn_name)
        if not conn_info:
            return None, None

        host = conn_info['host']
        port = conn_info['port']
        try:
            self.conn_pool[conn_name] = [
                try_login(host, port),
                time.time(),
                host,
                port
            ]

            return self.conn_pool[conn_name][0]
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


frp = FrpManager('121.199.49.228', 9998, 'admin', 'irain0818')

if __name__ == '__main__':
    sp = FrpManager('121.199.49.228', 9998, 'admin', 'irain0818')
    print sp.get_all_conn_info()
    print sp.get_all_conn_info()
