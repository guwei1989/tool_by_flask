from helper import get_mysql_addr, start, end, info

if __name__ == '__main__':
    start()
    addr = get_mysql_addr()
    info('%s %d' % (addr[0], addr[1]))
    end()