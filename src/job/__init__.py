# coding: utf-8
def mount_on(router, url_prefix):
    from api import task_new_logs

    router.route(url_prefix + '/task_new_logs')(task_new_logs)
