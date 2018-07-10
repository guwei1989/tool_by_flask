# coding: utf-8
import os

r_itools_root = '/home/.itools/'
dependencies = ['static/scripts/helper.py', 'static/scripts/log_helper.py', 'static/scripts/v3_helper.py']
for i in range(len(dependencies)):
    dep = dependencies[i]
    dependencies[i] = os.path.join(*dep.split('/'))


def file_md5(f):
    content = f.read()
    return abs(hash(content))


def execute_file(ssh_client, local_file, args=(), interpreter='python'):
    with open(local_file) as f:
        f_md5 = file_md5(f)
        md5_file_name = '%s.%s' % (os.path.basename(f.name), f_md5)
        remote_file = os.path.join(r_itools_root, md5_file_name)

        sftp = ssh_client.open_sftp()

        shell = ssh_client.invoke_shell()
        stdin = shell.makefile('wb')
        stdout = shell.makefile('rb')

        stdin.write("cd %s\n" % r_itools_root)

        if not r_file_exist(sftp, r_itools_root):
            sftp.mkdir(r_itools_root)

        if not r_file_exist(sftp, remote_file):
            files = sftp.listdir(r_itools_root)
            for f in files:
                if os.path.basename(local_file) in f:
                    sftp.remove(os.path.join(r_itools_root, f))
            sftp.put(local_file, remote_file)

        # copy dependencies
        for dep in dependencies:
            with open(dep) as dep_f:
                dep_md5 = file_md5(dep_f)
                remote_dep_md5 = os.path.join(r_itools_root, "%s.%s" %
                                              (os.path.basename(dep), dep_md5))
                remote_dep = os.path.join(r_itools_root, "%s" %
                                          os.path.basename(dep))
                if not r_file_exist(sftp, remote_dep_md5):
                    files = sftp.listdir(r_itools_root)
                    for f in files:
                        if os.path.basename(dep) in f:
                            sftp.remove(os.path.join(r_itools_root, f))
                    sftp.put(dep, remote_dep_md5)
                    sftp.put(dep, remote_dep)

    cmd = "%s %s" % (interpreter, remote_file)
    if args is not None:
        for i in range(len(args)):
            cmd += " %s" % args[i]

    stdin.write("%s\n" % cmd)
    return stdout


def r_file_exist(sftp, file_path):
    try:
        sftp.stat(file_path)
    except IOError:
        return False
    return True


def test():
    import paramiko

    # monkey patch working directory
    os.chdir('../../')
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn.connect(
        hostname='192.168.55.52',
        port=22,
        username='root',
        password='iriandev10241GB',
        timeout=10)
    out = execute_file(conn, 'static/scripts/a.py')
    while True:
        print out.readline()


if __name__ == '__main__':
    test()
