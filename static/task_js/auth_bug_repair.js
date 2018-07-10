$(document).ready(function () {

    $('[data-toggle="tooltip"]').tooltip();

    $("#reduce_showtime_btn_auth_bug").click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        $("#loading_gif_auth_bug").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/v3/reduce_auth_show_time",
            data: param,

            success: function (chunk, textStatus) {

                $("#loading_gif_auth_bug").css("visibility", "hidden");

                if (chunk.result == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "操作成功，此车界面显示的授权时间已经减少一天，您的收入不会受影响！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "操作失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_auth_bug").css("visibility", "hidden");
                bootbox.alert({
                    title: "提示信息",
                    message: "网络超时，请联系管理员！",
                    size: "small"
                });
            },
            timeout: 60000,
            dataType: 'json'
        });

    });


    $("#extend_authtime_btn_auth_bug").click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        $("#loading_gif_auth_bug").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/v3/extend_auth_time",
            data: param,
            success: function (chunk, textStatus) {

                $("#loading_gif_auth_bug").css("visibility", "hidden");
                if (chunk.result == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "操作成功，此车的实际授权时间增加了一天，让客户满意是艾润的遵旨！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "操作失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_auth_bug").css("visibility", "hidden");
                bootbox.alert({
                    title: "提示信息",
                    message: "网络超时，请联系管理员！",
                    size: "small"
                });
            },
            timeout: 60000,
            dataType: 'json'
        });

    })

});
