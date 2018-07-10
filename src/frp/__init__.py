# coding: utf-8
def mount_on(router, url_prefix):
    from api import get_frp_auth, frp_list
    router.route(url_prefix + '/get_frp_auth', methods=['POST'])(get_frp_auth)
    router.route(url_prefix + '/init_frp_park_name')(frp_list)
