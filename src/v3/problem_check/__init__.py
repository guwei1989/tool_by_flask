# coding: utf-8
def mount_on(router, url_prefix):
    from api import park_flow_analyse, park_records
    router.route(url_prefix + '/park_flow_analyse', methods=['GET'])(park_flow_analyse)
    router.route(url_prefix + '/park_records', methods=['GET'])(park_records)
