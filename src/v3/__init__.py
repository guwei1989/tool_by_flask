# coding: utf-8
def mount_on(app, url_prefix):
    import system_status
    import data_maintain
    import log_analyse
    import problem_check

    system_status.mount_on(app, url_prefix)
    data_maintain.mount_on(app, url_prefix)
    log_analyse.mount_on(app, url_prefix)
    problem_check.mount_on(app, url_prefix)
