$(document).ready(function () {

    $('#parkname_init_loadingModal').modal({backdrop: 'static', keyboard: false});

    var init_frp_park_name = "/api/frp/init_frp_park_name";

    $.ajax({
        type: 'GET',
        url: init_frp_park_name,
        success: function (chunk, textStatus) {
            $("#park_name").autocomplete({
                source: chunk
            });
            $("#parkname_init_loadingModal").modal('hide');
        },
        error: function () {

            $("#parkname_init_loadingModal").modal('hide');

            bootbox.alert({
                title: "提示信息",
                message: "车产数据初始化失败，网络超时！",
                size: "small"
            });
        },
        timeout: 60000,
        dataType: 'json'
    });

    $('#tab1').on("shown.bs.tab", function (e) {
        $("#ip_list_btn").css("display", "inherit")
    });

    $('#tab2').on("shown.bs.tab", function (e) {
        $("#ip_list_btn").css("display", "none")
    });

    $('#tab3').on("shown.bs.tab", function (e) {
        $("#ip_list_btn").css("display", "none")
    });

    $('#tab5').on("shown.bs.tab", function (e) {
        $("#ip_list_btn").css("display", "none")
    });


    $("#oprate_type").change(function () {

        if ($("#oprate_type").val() == "Frp模式") {
            $("#inout_net_type").css("display", "none");
            $("#park_name_type").css("display", "inherit")
        } else {
            $("#inout_net_type").css("display", "inherit");
            $("#park_name_type").css("display", "none")
        }

    });


    $("#ip_list_btn").click(function () {

        if (!$("#park_name").val()) {
            bootbox.alert({
                title: "提示信息",
                message: "请输入有效的车场名称！",
                size: "small"
            });
            return
        }

        $("#ip_list").empty();

        $('#parkip_init_loadingModal').modal({backdrop: 'static', keyboard: false});

        $.ajax({
            type: 'GET',
            url: "/api/v3/get_arm_ip_list",
            data: {park_name: $("#park_name").val()},

            success: function (chunk, textStatus) {

                $("#parkip_init_loadingModal").modal('hide');

                if (!$.isArray(chunk.result)) {

                    bootbox.alert({
                        title: "提示信息",
                        message: "暂不支持V2车场的arm IP获取！"
                    });

                    return
                }

                if (chunk.result.length > 0) {
                    $("#ip_list_info").css("display", "inherit");
                    $.each(chunk.result, function (index, value) {
                        $("#ip_list").append("<option value='" + value + "'>" + value + "</option>")
                    });
                    $("#ip_list").selectpicker("refresh");
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "未获取到arm IP，输入的车场名称有误！"
                    });
                }
            },

            error: function () {
                $("#parkip_init_loadingModal").modal('hide');

                bootbox.alert({
                    title: "提示信息",
                    message: "车场IP列表获取失败，请联系管理员！"
                });
            },
            timeout: 60000,
            dataType: 'json'
        });

    });

});