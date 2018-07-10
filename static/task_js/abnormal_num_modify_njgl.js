$(document).ready(function () {

    $("#db_ok_btn_njgl").click(function () {

        if (!$("#abnormal_num").val()) {
            bootbox.alert({
                title: "提示信息",
                message: "异常进出车数量不可为空！",
                size: 'small'
            });
            return
        }

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        param.abnormal_num = $("#abnormal_num").val();

        $("#loading_gif_abnormal").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/v3/abnormal_num_modify",
            data: param,

            success: function (chunk, textStatus) {

                $("#loading_gif_abnormal").css("visibility", "hidden");

                if (chunk.result == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "修改异常进出车数量成功！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "修改异常进出车数量失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_abnormal").css("visibility", "hidden");
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
