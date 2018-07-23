$(document).ready(function () {

    $("#arm_check_btn").click(function () {

        var param = operate_type_no_ip_list();
        if (!param) {
            return
        }

        $("#arm_check_btn").attr("disabled", "disabled");
        $("#check_info").empty();
        $("#check_progress").css("width", "0%");
        $("#check_now").html("体检准备中，请稍等。。。");

        $.ajax({
            type: 'POST',
            url: "/api/v3/arm_check",
            data: param,
            success: function (chunk, textStatus) {
                data = chunk;
                if (data.result == "success") {

                    var task_id = data.task_id;
                    intervalJob = setInterval(function () {
                        $.ajax({
                            type: 'GET',
                            url: "/api/job/output",
                            data: {"task_id": task_id},
                            success: function (chunk, textStatus) {
                                data = chunk;
                                $("#check_progress").css("width", data.progress + "%");
                                $("#check_now").html("体检中：" + data.progress + "%");

                                // console.log(data.logs);
                                var logs = data.logs;
                                for (var log in logs) {
                                    if (logs[log].log_type == "START" || logs[log].log_type == "END") {
                                        continue;
                                    }
                                    if (logs[log].log_type == "ERR") {
                                        var logItem = $("<li style='color: red;'>" + logs[log].time +
                                            ":&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + logs[log].msg + "</li>")

                                    } else {
                                        var logItem = $("<li>" + logs[log].time + ":&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                                            + logs[log].msg + "</li>")
                                    }
                                    $("#check_info").append(logItem);
                                    logItem.hide().show('slow')
                                }

                                if (data.progress == 100) {
                                    $("#check_now").html("体检完成：" + data.progress + "%");
                                    clearInterval(intervalJob);
                                    bootbox.alert({
                                        title: "提示信息",
                                        message: "体检完成，结果详见输出栏！"
                                    });
                                    $("#arm_check_btn").removeAttr("disabled");
                                }
                            },
                            error: function () {
                                $("#check_now").html("体检失败！");
                                $("#arm_check_btn").removeAttr("disabled");
                            },
                            timeout: 60000,
                            dataType: 'json'
                        });
                    }, 2000)
                }

            },
            error: function () {
                $("#check_now").html("体检失败！");
                bootbox.alert({
                    title: "提示信息",
                    message: "体检失败，网络超时！"
                });
                $("#arm_check_btn").removeAttr("disabled");
            },
            timeout: 60000,
            dataType: 'json'
        });

    });

});