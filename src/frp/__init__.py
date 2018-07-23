# coding: utf-8
def mount_on(router, url_prefix):
    from api import frp_list
    router.route(url_prefix + '/init_frp_park_name')(frp_list)
