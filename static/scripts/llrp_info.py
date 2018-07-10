# coding: utf-8
import os
from helper import start, end, info


def main():
    if not os.path.exists('/home/llrp/llrpc.ini'):
        info('fail')
        return

    with open('/home/llrp/llrpc.ini') as f:
        for line in f.readlines():
            if 'client_id' in line:
                info (line)
            if 'name' in line:
                info(line)
                return


if __name__ == '__main__':
    start()
    main()
    end()
