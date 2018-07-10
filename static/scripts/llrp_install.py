import os
import ConfigParser
from collections import OrderedDict
import time
from helper import start, end, info

server_ip = "120.26.7.171"
server_port = 6160
api_port = 6161
url = "http://104.27.147.80:8080/llrpc.jpg"

VERSION = 0
if os.path.exists('/home/park/log'):
    VERSION = 3
else:
    VERSION = 2


def remove_old_tar():
    os.system("rm -f /home/llrpc.tar.gz")


def download_tar():
    os.system("""cd /home;wget --header='Host: www.llrp.download:8080' -O llrpc.tar.gz "%s" """ % url)


def remove_old():
    os.system("cd /home;rm -rf /home/llrp")


def unzip():
    os.system("cd /home;tar zxvf llrpc.tar.gz")


def crontab():
    content = "*/10 * * * * cd /home/llrp;./upgrade"
    with open("/var/spool/cron/crontabs/root", "r+") as f:
        for line in f.readlines():
            if line.find(content) != -1:
                return
        os.system("sh /home/llrp/cron.sh")


def get_arm_code():
    if VERSION == 3:
        stdin = os.popen(
            'mysql -uroot -piraindb10241GB -h%s irain_park -sNe "select value from project_conf where id=4"'
            % get_mysql_addr()[0])
        park_code = stdin.readline().strip()
        out = os.popen(
            """ifconfig eth0 | grep 'inet addr'|awk '{print $2}'|awk -F':' '{print $2}'"""
        )
        result = out.read()
        out.close()
        ip = result.replace('\n', '')
        return park_code + ip.split('.')[-1].zfill(4)
    else:
        out = os.popen(
            "cat /mnt/nfs/local/wacs/etc/device.conf|grep 'armid '|awk '{print $3}'")
        armid = out.readline().strip()
        out.close()
        return armid


def get_park_name():
    if VERSION == 3:
        stdin = os.popen(
            'mysql -uroot -piraindb10241GB -h%s irain_park -sNe "select name from depot_conf limit 1"'
            % get_mysql_addr()[0])
        park_name = stdin.readline().strip()
        return park_name
    else:
        out = os.popen(
            'mysql -uroot -pa1b2c3 -h%s acdbs -sNe "select name from nest_group"'
            % get_mysql_addr()[0])
        park_name = out.readline().strip()
        return park_name


def get_mysql_addr():
    """
    :return:
        tuple
        ( '192.168.0.5', 3306)
    """
    if VERSION == 3:
        out = os.popen("cat /home/park/config/config.cfg |grep -A5 '\[mysql\]' | grep -v mysql | awk "
                       "'{print $3}'")
        output = out.readlines()
        addr = output[0].replace('\n', '')
        port = int(output[3])
        out.close()
        return addr, port
    else:
        out = os.popen("cat /mnt/nfs/local/wacs/etc/device.conf |grep -E 'db_server '|awk '{print $3}'")
        output = out.readlines()
        addr = output[0].replace('\n', '')
        addr = "127.0.0.1" if addr == 'localhost' else addr
        out2 = os.popen("cat /mnt/nfs/local/wacs/etc/device.conf |grep -E 'db_server_port '|awk '{print $3}'")
        output2 = out2.readlines()
        port = output2[0].replace('\n', '')
        out.close()
        out2.close()
        return addr, port


def setup_ini():
    cfg = OrderedDict()

    cfg["common"] = {
        "server_ip": server_ip,
        "server_port": server_port,
        "api_port": api_port,
        "client_id": get_arm_code(),
        "name": get_park_name()
    }
    ini = ConfigParser.ConfigParser()
    for section_name, section in cfg.items():
        ini.add_section(section_name)
        for k, v in section.items():
            ini.set(section_name, k, v)
    with open("/home/llrp/llrpc.ini", "r+") as f:
        ini.write(f)


def stop_old():
    os.system("pkill -f llrpc")


if __name__ == '__main__':
    start()
    remove_old_tar()
    download_tar()
    remove_old()
    unzip()
    setup_ini()
    time.sleep(3)
    crontab()
    stop_old()
    info("success")
    end()

