$(document).ready(function () {

    var con_flag = true;

    var cpu_usage_time = new Queue(5);
    var cpu_usage = new Queue(5);
    var cpuChart = echarts.init(document.getElementById('cpu_status_chart'));
    var cpu_option = {
        title: {
            text: 'CPU状态'
        },
        tooltip: {},
        legend: {
            data: ['CPU占用率']
        },
        xAxis: {
            name: '时间',
            type: 'category',
            data: cpu_usage_time.quene()
        },
        yAxis: {
            name: '占用比(%)',
            type: 'value'
        },
        series: [{
            name: 'CPU占用率',
            type: 'line',
            color: '#FF0000',
            data: cpu_usage.quene()
        }]
    };
    // 使用刚指定的配置项和数据显示图表。
    cpuChart.setOption(cpu_option);

    var ram_usage_time = new Queue(5);
    var ram_usage = new Queue(5);
    var ramChart = echarts.init(document.getElementById('ram_status_chart'));
    var ram_option = {
        title: {
            text: '内存状态'
        },
        tooltip: {},
        legend: {
            data: ['内存占用率']
        },
        xAxis: {
            name: '时间',
            type: 'category',
            data: ram_usage_time.quene()
        },
        yAxis: {
            name: '占用比(%)',
            type: 'value'
        },
        series: [{
            name: '内存占用率',
            type: 'line',
            color: '#87CEFA',
            data: ram_usage.quene()
        }]
    };
    // 使用刚指定的配置项和数据显示图表。
    ramChart.setOption(ram_option);

    var rom_usage_time = new Queue(5);
    var rom_usage = new Queue(5);
    var romChart = echarts.init(document.getElementById('rom_status_chart'));
    var rom_option = {
        title: {
            text: '硬盘状态'
        },
        tooltip: {},
        legend: {
            data: ['硬盘占用率']
        },
        xAxis: {
            name: '时间',
            type: 'category',
            data: rom_usage_time.quene()
        },
        yAxis: {
            name: '占用比(%)',
            type: 'value'
        },
        series: [{
            name: '硬盘占用率',
            type: 'line',
            color: '#9932CC',
            data: rom_usage.quene()
        }]
    };
    // 使用刚指定的配置项和数据显示图表。
    romChart.setOption(rom_option);

    var network_time = new Queue(5);
    var send_data = new Queue(5);
    var receive_data = new Queue(5);
    var networkChart = echarts.init(document.getElementById('network_status_chart'));
    var network_option = {
        title: {
            text: '网络状态'
        },
        tooltip: {},
        legend: {
            data: ['发送', '接收']
        },
        xAxis: {
            name: '时间',
            type: 'category',
            data: network_time.quene()
        },
        yAxis: {
            name: '流量(KB)',
            type: 'value'
        },
        series: [{
            name: '发送',
            type: 'line',
            color: '#D2691E',
            data: send_data.quene()
        },
            {
                name: '接收',
                type: 'line',
                color: '#00FF00',
                data: receive_data.quene()
            }]
    };
    // 使用刚指定的配置项和数据显示图表。
    networkChart.setOption(network_option);


    $("#get_sys_status_btn").click(function () {

        var param = operate_type();
        if (!param) {
            return
        }
        con_flag = true;
        // $("#loadingModal").modal('show');
        $('#loadingModal').modal({backdrop: 'static', keyboard: false});

        var cpu_url = '/api/v3/cpu_usage';
        var ram_url = '/api/v3/mem_usage';
        var rom_url = '/api/v3/disk_usage';
        var network_url = '/api/v3/net_usage';

        get_data(param, cpu_url, cpu_usage, cpu_usage_time, cpuChart, cpu_option, con_flag);
        get_data(param, ram_url, ram_usage, ram_usage_time, ramChart, ram_option, con_flag);
        get_data(param, rom_url, rom_usage, rom_usage_time, romChart, rom_option, con_flag);
        get_net_data(param, network_url, send_data, receive_data, network_time, networkChart, network_option, con_flag)
    });

    $("#disconnect_arm_btn").click(function () {

        if (all_setinterval_id.length > 0) {
            bootbox.confirm({
                buttons: {
                    confirm: {
                        label: '确认',
                        className: 'btn-default'
                    },
                    cancel: {
                        label: '取消',
                        className: 'btn-default'
                    }
                },
                title: '提示信息',
                message: '确定要断开连接，停止系统监控？',
                callback: function (result) {
                    if (result) {
                        for (var i = 0; i < all_setinterval_id.length; i++) {

                            clearInterval(all_setinterval_id[i]);
                        }

                        con_flag = false;
                        all_setinterval_id.length = 0;
                    }
                }
            });

        } else {
            bootbox.alert({
                title: "提示信息",
                message: "您现在未监控任何车场系统状态！"
            })
        }

    });


    $("#arm_restart").click(function () {

        if (!$("#ip_list").val()) {
            var param = operate_type_no_ip_list();
            var msg = '此操作会将整个车场所有的arm板子的进程重启，您确定这么做吗？'
        } else {
            var param = operate_type();
            var msg = '此操作会将您选定的arm板子的进程重启，您确定这么做吗？'
        }

        if (!param) {
            return
        }

        bootbox.confirm({
            buttons: {
                confirm: {
                    label: '确认',
                    className: 'btn-default'
                },
                cancel: {
                    label: '取消',
                    className: 'btn-default'
                }
            },

            title: '警告',
            message: msg,

            callback: function (result) {
                if (result) {
                    $("#loading_gif_status").css("visibility", "visible");
                    $("#arm_restart").attr("disabled", "disabled");
                    $.ajax({
                        type: 'POST',
                        url: "/api/v3/all_arm_restart",
                        data: param,
                        success: function (chunk, textStatus) {

                            $("#loading_gif_status").css("visibility", "hidden");
                            $("#arm_restart").removeAttr("disabled");

                            if (chunk.result == 0) {
                                bootbox.alert({
                                    title: "提示信息",
                                    message: "一键重启成功！"
                                });
                            } else {
                                bootbox.alert({
                                    title: "提示信息",
                                    message: "一键重启失败，服务器端错误，请联系开发人员！"
                                });
                            }
                        },

                        error: function () {
                            $("#loading_gif_status").css("visibility", "hidden");
                            $("#arm_restart").removeAttr("disabled");
                            bootbox.alert({
                                title: "提示信息",
                                message: "网络超时，请联系管理员！"
                            });
                        },
                        timeout: 120000,
                        dataType: 'json'
                    });
                }
            }
        });

    });

});

var all_setinterval_id = [];

/*向后台每隔2S发一次http请求*/
function get_data(options, url, usage, time_line, chart_name, chart_option, con_flag) {

    var status_id = setInterval(function () {
        $.ajax({
            type: 'GET',
            url: url,
            data: options,
            success: function (chunk, textStatus) {

                if (!con_flag) {
                    return
                }

                data = chunk;
                usage.push(data.usage * 100);
                time_line.push(formatDateTime(data.timestamp).slice(11));
                chart_name.setOption(chart_option);

                $("#loadingModal").modal('hide');

                $("#park_info").css("display", "inherit");

                if ($("#oprate_type").val() == "Frp") {

                    $("#park_info").text("正在监控车场名称：" + $("#park_name").val())

                } else {
                    $("#park_info").text("正在监控IP：" + $("#arm_address").val() + "；端口号为：" + $("#arm_port").val())
                }
            },
            error: function () {

            },
            timeout: 60000,
            dataType: 'json'
        });

    }, 2000);

    all_setinterval_id.push(status_id)
}

function get_net_data(options, url, send_data, receive_data, time, chart_name, chart_option, con_flag) {
    var status_id = setInterval(function () {

        $.ajax({
            type: 'GET',
            url: url,
            data: options,
            success: function (chunk, textStatus) {

                if (!con_flag) {
                    return
                }

                data = chunk;
                send_data.push(data.outbound / 1024);
                receive_data.push(data.inbound / 1024);
                time.push(formatDateTime(data.timestamp).slice(11));
                chart_name.setOption(chart_option);
                $("#loadingModal").modal('hide');
            },

            error: function () {

            },
            timeout: 60000,
            dataType: 'json'
        });

    }, 2000);

    all_setinterval_id.push(status_id)
}
