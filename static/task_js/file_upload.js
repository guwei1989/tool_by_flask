$(function () {


    $('#upload_btn').click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        $("#loading_gif_file_upload").css("visibility", "visible");

        var park_name = null;
        var hostname = null;
        var port = null;

        var files = $('#FileUpload').prop('files');

        var data = new FormData();

        data.append("file", files[0]);

        if (param.park_name) {
            park_name = param.park_name;
            data.append("park_name", park_name);

        } else {
            hostname = param.hostname;
            port = param.port;
            data.append("hostname", hostname);
            data.append("port", port);
        }

        data.append("path", $("#file_path").val());
        data.append("version", $("#version").val());

        console.log("**************" + data);

        $.ajax({
            url: '/api/v3/file_upload',
            type: 'POST',
            data: data,
            cache: false,
            processData: false,
            contentType: false,

            success: function (chunk, textStatus) {

                $("#loading_gif_file_upload").css("visibility", "hidden");

                if (chunk.result == 0) {
                    bootbox.alert({
                        title: "提示信息",
                        message: "上传成功！",
                        size: "small"
                    });
                } else {
                    bootbox.alert({
                        title: "提示信息",
                        message: "上传文件失败，服务器端错误，请联系开发人员！",
                        size: "small"
                    });
                }
            },

            error: function () {
                $("#loading_gif_file_upload").css("visibility", "hidden");
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

});