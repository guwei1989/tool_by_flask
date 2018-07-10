# coding: utf-8
import paramiko

from src.job.job_system import jobsystem
from src.job.remote_script_job import RemoteScriptJob


def get_local_ip(ssh_client):
    j = RemoteScriptJob(ssh_client, 'static/scripts/get_local_ip.py')
    j.run()
    for log in j.read_all():
        return log.str.strip()


def get_mysql_addr(ssh_client):
    """
    :param ssh_client:
    :return:
        ('192.168.55.248', 3306)
    """
    j = RemoteScriptJob(ssh_client, 'static/scripts/get_mysql_addr.py')
    j.run()
    for log in j.read_all():
        addr = log.str.strip().split(' ')
        return addr[0], int(addr[1])


def get_all_terminal_ip(ssh_client):
    """
        :param ssh_client:
        :return:
            ('192.168.55.248', 3306)
        """
    j = RemoteScriptJob(ssh_client, 'static/scripts/get_all_arm_ip.py')
    j.run()

    all_terminal = []
    for log in j.read_all():
        all_terminal.append(log.str.strip())
    return all_terminal


def execute_shell(ssh_client, shell_code):
    shell = ssh_client.invoke_shell()
    f_in = shell.makefile('wb')
    f_out = shell.makefile('rb')

    start_flag = 'IRAINTOOLS_START'
    start_cmd = 'echo %s' % start_flag

    end_flag = 'IRAINTOOLS_END'
    end_cmd = 'echo %s' % end_flag

    f_in.write('%s;%s;%s\n' % (start_cmd, shell_code, end_cmd))

    started = False

    while True:
        out = f_out.readline().strip()
        if out == start_flag:
            started = True
            continue
        if out == end_flag:
            return
        if started:
            yield out


def make_tunnel(ssh_client, host, username='root', password='iraindev10241GB'):
    # return (SSHClient, int_version) or (None, None) if error happened

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        chan = ssh_client.get_transport().open_channel('direct-tcpip', (host, 22), ('localhost', 0))
        c.connect(hostname=None, port=22, username=username, password=password, timeout=10, sock=chan)
        return c, 3
    except paramiko.AuthenticationException:
        pass
    return None, None


def run_all_arm(client, func):
    all_arm = get_all_terminal_ip(client)
    for arm in all_arm:
        try:
            tunnel, version = make_tunnel(client, arm)
        except Exception, err:
            print 'Fail to make tunnel to ', arm, ' due to ', str(err)
            continue
        if tunnel:
            func(tunnel, arm, version)


def run_script(client, script_path, args=()):
    j = RemoteScriptJob(client, script_path)
    j.run(args)
    return j.read_all()


def test():
    from src.frp.frp import frp

    conn, _ = frp.get_conn('凯德东')
    for out in execute_shell(conn, 'll'):
        print out


if __name__ == '__main__':
    test()
