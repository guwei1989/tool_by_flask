$(document).ready(function () {

    $("#datepicker_in_out").click(function () {
        $("#ui-datepicker-div").css({"z-index": 1100});
    });

    $.datepicker.setDefaults($.datepicker.regional["zh-CN"]);

    $("#datetime_in_out").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "yy-mm-dd", //日期的格式  呈现在输入的文本框中
        showAnim: "toggle", //弹出日历的效果
        prevText: "上一月",
        nextText: "下一月",
        showButtonPanel: true,
        closeText: "关闭"
    });
    $("#datetime_in_out").datepicker().datepicker('setDate', new Date());

    $('#get_out_time_btn').click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        $("#loading_in_out_process").css("visibility", "visible");
        $("#out_time").empty();
        $("#out_time_list").css("visibility", "hidden");
        $("#in_out_info").empty();
        $("#in_out_info_row").css("display", "none");
        $("#in_out_process_btn").css("visibility", "hidden");
        $("#line").css("display", "none");

        param.park_date = $("#datetime_in_out").val();
        param.vpr_plate = $("#in_out_plate").val();

        $.ajax({
            type: 'GET',
            url: "/api/v3/park_records",
            data: param,
            success: function (data, textStatus) {
                if (data.code == 0) {
                    if (data.records.length == 0) {
                        bootbox.alert({
                            title: "提示信息",
                            message: "未找到该车相关进出车记录",
                            size: "small"
                        });

                        $("#loading_in_out_process").css("visibility", "hidden");

                    } else if (data.records.length != 1) {
                        $("#loading_in_out_process").css("visibility", "hidden");
                        $("#out_time_list").css("visibility", "visible");
                        $("#in_out_process_btn").css("visibility", "visible");

                        $.each(data.records, function (index, value) {
                            $("#out_time").append("<option value='" + value.out_time + "'>" + value.out_time + "</option>")
                        });
                    } else {
                        parkAnalyse($("#in_out_plate").val(), data.records[0].out_time, $("#park_name").val())
                    }
                    // $("#out_time").selectpicker("refresh");
                }
            },
            error: function () {
                bootbox.alert({
                    title: "提示信息",
                    message: "请求失败，网络超时！",
                    type: "small"
                });
            },
            timeout: 60000,
            dataType: 'json'
        });
    });

    $("#in_out_process_btn").click(function () {

        $("#loading_in_out_process").css("visibility", "visible");
        $("#in_out_info").empty();
        $("#in_out_info_row").css("display", "none");
        $("#line").css("display", "none");

        parkAnalyse($("#in_out_plate").val(), $("#out_time").val(), $("#park_name").val())
    });

    function parkAnalyse(vpr, datetime, parkName) {
        $.ajax({
            type: 'GET',
            url: '/api/v3/park_flow_analyse',
            data: {
                vpr_plate: vpr,
                park_name: parkName,
                park_time: datetime
            },
            success: function (data, err) {
                if (data.code == 0) {
                    // handle it
                    var taskId = data.task_id;
                    var task = setInterval(function () {
                        $.ajax({
                            type: 'GET',
                            url: '/api/job/output',
                            data: {
                                task_id: taskId
                            },
                            success: function (data, err) {
                                if (data.code == 0) {
                                    for (var i in data.logs) {
                                        var log = data.logs[i];
                                        if (log.log_type == "INFO") {
                                            draw(log.value);
                                        } else if (log.log_type == "END") {
                                            clearInterval(task)
                                        }
                                    }
                                }
                            }
                        })
                    }, 5000)
                }
            },
            error: function () {
                bootbox.alert({
                    title: "提示信息",
                    message: "请求失败，网络超时！",
                    type: "small"
                });
            },
            timeout: 60000,
            dataType: 'json'
        })
    }


    function draw(info) {

        console.log(info);

        $("#loading_in_out_process").css("visibility", "hidden");
        $("#in_out_info_row").css("display", "inherit");
        $("#in_out_info_row").css({"z-index": 1100});
        $("#in_out_info").css("height", 300);
        $("#line").css("display", "inherit");

        $("#in_out_info").append("<li>车   牌：  " + info["vpr"] + "</li>");
        $("#in_out_info").append("<li>入场时间：  " + info["in_time"] + "</li>");
        $("#in_out_info").append("<li>入场记录上报时间：  " + info["in_upload_time"] + "</li>");
        $("#in_out_info").append("<li>出场时间：  " + info["out_time"] + "</li>");
        $("#in_out_info").append("<li>出场记录上报时间：  " + info["out_upload_time"] + "</li>");
        $("#in_out_info").append("<li>出场方式：  " + info["out_type"] + "</li>");

        if (info["out_charge_detail"]) {
            $("#in_out_info").append("<li id='charge_rule'>出口计费详情：  </li>");

            for (var j = 0; j < info["out_charge_detail"].length; j++) {

                var date1 = info["out_charge_detail"][j][1];
                var date2 = info["out_charge_detail"][j][2];

                $("#charge_rule").append("<div style='margin-left: 30px;'>" + info["out_charge_detail"][j][0] + "</div>");
                $("#charge_rule").append("<div style='margin-left: 30px;'>" + date1 + "</div>");
                $("#charge_rule").append("<div style='margin-left: 30px;'>" + date2 + "</div>");
                $("#charge_rule").append("<div style='margin-left: 30px;'>" + info["out_charge_detail"][j][3] + "元</div>");
                $("#charge_rule").append("<HR SIZE=5>")
            }
        }
        $("#in_out_info").append("<li>出口报费：  " + info["price"] + "元</li>");
        if (info["电子券"]) {
            $("#in_out_info").append("<li id='e_coupon'>电子券：  </li>");

            for (var j in info['电子券']) {
                var coupon = info['电子券'][j];

                $("#e_coupon").append("<div style='margin-left: 30px;'>券类型:" + coupon["券类型"] + "</div>");
                $("#e_coupon").append("<div style='margin-left: 30px;'>券值:" + coupon["券值"] + "</div>");
                $("#e_coupon").append("<div style='margin-left: 30px;'>备注:" + coupon["备注"] + "</div>");
                $("#e_coupon").append("<HR SIZE=5>")
            }
        }
        $("#in_out_info").append("<li>出口抬杆时间：  " + info["open_time"] + "</li>");
        $("#in_out_info").append("<li>出场时授权：  " + info["cur_auth"] + "</li>");
        $("#in_out_info").append("<li>原本授权：  " + info["ori_auth"] + "</li>");
        if (info["授权占用车牌"]) {
            $("#in_out_info").append("<li>授权占用车牌：  " + info["auth_occupy_vpr"] + "</li>");
        }
        if (info["授权生效时间"]) {
            $("#in_out_info").append("<li>授权生效时间：  " + info["auth_takeeffect_time"] + "</li>");
        }
        $("#in_out_info").append("<li>停车时长：  " + formatSeconds(info["park_duration"]) + "</li>");
        $("#in_out_info").append("<li>大小车类型：  " + info["car_size_type"] + "</li>");
        $("#in_out_info").append("<li>能源类型：  " + info["energy_type"] + "</li>");
        if (info["charge_rule"]) {
            $("#in_out_info").append("<li>计费规则：  " + info["charge_rule"] + "</li>");
        }
        $("#in_out_info").append("<li>预留时间：  " + info["reserve_time"] + "秒</li>");
        if (info["corss_overlap"]) {
            $("#in_out_info").append("<li>跨时段叠加：  " + (info["corss_overlap"]).toString() + "</li>");
        }
        if (info["history_pay_time"]) {
            $("#in_out_info").append("<li>历史支付时间：  " + info["history_pay_time"] + "</li>");
        }
        if (info["history_pay_no"]) {
            $("#in_out_info").append("<li>历史支付订单：  " + info["history_pay_no"] + "</li>");
        }
        if (info["history_charge_no"]) {
            $("#in_out_info").append("<li>历史计费订单：  " + info["history_charge_no"] + "</li>");
        }
        if (info["history_pay_type"]) {
            $("#in_out_info").append("<li>历史支付类型：  " + info["history_pay_type"] + "</li>");
        }
        if (info["history_pay_amount"]) {
            $("#in_out_info").append("<li>历史支付金额：  " + info["history_pay_amount"] + "元</li>");
        }

        if (info["history_charge_detail"]) {
            $("#in_out_info").append("<li id='charge_rule'>历史计费详情：  </li>");

            for (var j = 0; j < info["history_charge_detail"].length; j++) {

                var date1 = info["history_charge_detail"][j][1];
                var date2 = info["history_charge_detail"][j][2];

                $("#charge_rule").append("<div style='margin-left: 30px;'>" + info["history_charge_detail"][j][0] + "</div>");
                $("#charge_rule").append("<div style='margin-left: 30px;'>" + date1 + "</div>");
                $("#charge_rule").append("<div style='margin-left: 30px;'>" + date2 + "</div>");
                $("#charge_rule").append("<div style='margin-left: 30px;'>" + info["history_charge_detail"][j][3] + "元</div>");
                $("#charge_rule").append("<HR SIZE=5>")
            }
        }

        if (info["history_charge_rule"]) {
            $("#in_out_info").append("<li>历史计费规则：  " + info["history_charge_rule"] + "</li>");
        }
        if (info["history_charge_amount"]) {
            $("#in_out_info").append("<li>历史计费结果：  " + info["history_charge_amount"] + "元</li>");
        }

        $("#in_out_info").append("<li>数据库查费时间：  " + info["db_charge_lookup_time"] + "</li>");
        $("#in_out_info").append("<li>进车记录id：  " + info["park_in_id"] + "</li>");
        $("#in_out_info").append("<li>出车记录id：  " + info["park_out_id"] + "</li>");
        $("#in_out_info").append("<li>出场耗时：  " + info["out_cost"] + "秒</li>");


        $("#in_out_info").append("<li>抬杆透传相机：  " + info["open_vpr"] + "</li>");
        $("#in_out_info").append("<li>语音透传相机：  " + info["voice_vpr"] + "</li>");
        // $("#in_out_info").append("<li>出场识别仪IP：  " + info["识别仪地址"] + "</li>");
    }
});