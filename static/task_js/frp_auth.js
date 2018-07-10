$(document).ready(function () {

    // $("#park_name_frp_auth").on('input propertychange', function () {
    //     $(".ui-menu").css("z-index", 1100);
    // });

    $("#auth_btn_frp_auth").click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        if (param.hostname) {
            bootbox.alert({
                title: "提示信息",
                message: "获取FRP授权只支持车场名称模式！",
                size: "small"
            });
            return
        }

        $("#loading_gif_frp_auth").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/frp/get_frp_auth",
            data: param,

            success: function (chunk, textStatus) {

                $("#loading_gif_frp_auth").css("visibility", "hidden");

                if (chunk.Code == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "获取FRP授权成功！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "获取FRP授权失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_frp_auth").css("visibility", "hidden");
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