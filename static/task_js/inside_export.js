$(document).ready(function () {
    $('#datetimepicker').datetimepicker();

    $("#export_btn").click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        param.end_time = $("#datetimepicker").val();

        $("#loading_gif_export").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/v3/inside_export",
            data: param,
            success: function (chunk, textStatus) {

                $("#loading_gif_export").css("visibility", "hidden");

                if (chunk.result == 0) {
                    download('/' + chunk.download_url)
                    //                    $('#download_frame').attr('src', chunk.download_url)
                    //                    bootbox.alert({
                    //                        title: "提示信息",
                    //                        message: "场内记录导出成功, 如果",
                    //                        size: "small"
                    //                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "场内记录导出失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_export").css("visibility", "hidden");
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


    $("#delete_btn").click(function () {

        var param = operate_type();
        if (!param) {
            return
        }

        param.end_time = $("#datetimepicker").val();

        $("#loading_gif_export").css("visibility", "visible");

        $.ajax({
            type: 'POST',
            url: "/api/v3/delete_inside_records",
            data: param,
            success: function (chunk, textStatus) {

                $("#loading_gif_export").css("visibility", "hidden");
                if (chunk.result == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "删除场内记录成功，并备份表park_inside和park_in至目录/home/.itools/db_dump下！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "删除场内记录失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_export").css("visibility", "hidden");
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