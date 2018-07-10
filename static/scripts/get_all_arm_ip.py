from helper import get_all_terminals_addr, start, end, info

if __name__ == '__main__':
    start()
    for addr in get_all_terminals_addr():
        info(addr)
    end()