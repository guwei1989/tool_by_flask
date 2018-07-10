# coding: utf-8
def mount_on(router, url_prefix):
    from api import log_parse
    router.route(url_prefix + '/log_parse', methods=['POST'])(log_parse)
