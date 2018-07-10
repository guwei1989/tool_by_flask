# coding: utf-8
from helper import start, end, info
from v3_helper import run_sql


def main():
    run_sql('create index trace_pay_uk on pay_count_history(trace_pay_uk)')
    info('ok')


if __name__ == '__main__':
    start()
    main()
    end()
