# coding: utf-8
def mount_on(router, url_prefix):
    from api import api_cpu_usage, api_disk_usage, api_mem_usage, api_net_usage, api_all_arm_restart, \
        api_get_arm_ip_list
    router.route(url_prefix + '/cpu_usage')(api_cpu_usage)
    router.route(url_prefix + '/disk_usage')(api_disk_usage)
    router.route(url_prefix + '/mem_usage')(api_mem_usage)
    router.route(url_prefix + '/net_usage')(api_net_usage)
    router.route(url_prefix + '/all_arm_restart', methods=['POST'])(api_all_arm_restart)
    router.route(url_prefix + '/get_arm_ip_list', methods=['GET'])(api_get_arm_ip_list)
