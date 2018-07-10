# coding: utf-8
def mount_on(router, url_prefix):
    from api import all_arm_health_check, extend_auth_time, mod_abnormal_inout_num, reduce_auth_show_time, db_backup, \
        delete_inside_records, inside_records_export, file_upload
    router.route(url_prefix + '/arm_check', methods=['POST'])(all_arm_health_check)
    router.route(url_prefix + '/inside_export', methods=['POST'])(inside_records_export)
    router.route(url_prefix + '/delete_inside_records', methods=['POST'])(delete_inside_records)
    router.route(url_prefix + '/reduce_auth_show_time', methods=['POST'])(reduce_auth_show_time)
    router.route(url_prefix + '/extend_auth_time', methods=['POST'])(extend_auth_time)
    router.route(url_prefix + '/db_backup', methods=['POST'])(db_backup)
    router.route(url_prefix + '/abnormal_num_modify', methods=['POST'])(mod_abnormal_inout_num)
    router.route(url_prefix + '/file_upload', methods=['POST'])(file_upload)