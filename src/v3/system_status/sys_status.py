# coding: utf-8


def cpu_usage(client):
    command = '''start=`cat /proc/stat | grep '' -m1 |awk '{print $5 "\\t" $2+$3+$4+$5+$6}'`;sleep .5;end=`cat /proc/stat | grep '' -m1 |awk '{print $5 "\\t" $2+$3+$4+$5+$6}'`;echo $start$'\\n'$end |awk 'NR==1 {idle1=$1; total1=$2} NR==2{idle2=$1;total2=$2;printf "%.5f\\n", (idle2-idle1)/(total2-total1)}' '''
    _, out, err = client.exec_command(command)
    info = out.read()
    return 1 - float(info)


def mem_usage(client):
    _, out, err = client.exec_command(
        '''cat /proc/meminfo | grep 'MemTotal\|MemFree' | awk 'NR==1{total=$2} NR==2{free=$2;printf "%d\\t%d\\n", free, total}'   ''')
    info = out.read().split('\t')
    free = int(info[0])
    total = int(info[1])
    return total - free, total


def disk_usage(client):
    _, out, err = client.exec_command("df -h | grep /dev/root | awk '{print $5}'")
    info = out.read().replace('%', '')
    return float(info) / 100


def net_inout_bytes(client):
    command = '''start=`cat /proc/net/dev |grep eth0 |awk '{print $2 "\\t" $10}'`;sleep .3;end=`cat /proc/net/dev |grep eth0 |awk '{print $2 "\\t" $10}'`;echo $start$'\\n'$end | awk 'NR==1{recv1=$1;send1=$2} NR==2{recv2=$1;send2=$2;printf "%d\\t%d\\n", (recv2-recv1)/.3, (send2-send1)/.3}' '''
    _, out, err = client.exec_command(command)
    info = out.read().split('\t')
    return int(info[0]), int(info[1])


