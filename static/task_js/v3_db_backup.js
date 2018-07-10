$(document).ready(function () {

    $("#db_dump_btn").click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        $("#loading_gif_dump").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/v3/db_backup",
            data: param,
            success: function (chunk, textStatus) {

                $("#loading_gif_dump").css("visibility", "hidden");

                if (chunk.code == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "数据库备份成功至/home/db_backup目录下！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "数据库备份失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_dump").css("visibility", "hidden");
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
